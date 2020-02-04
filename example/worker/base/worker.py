import thread_meeting

import datetime
import enum
import inspect
from overrides import EnforceOverrides
import time
from typing import Optional

from .decorators import transcribe_func, interruptable
from example.worker.message import Message
from .worker_state import WorkerState


class FuncAndData:
    def __init__(self, func=None, data=None):
        self.func = func
        self.data = data

    def __bool__(self):
        return self.func is not None

    def exec(self):
        if self.func:
            self.func(self.data)


class Worker(EnforceOverrides):

    # CONSTRUCTOR AND PROPERTIES
    def __init__(self, *, name: str = '', enum_class: enum.Enum = Message):
        if not name:
            name = self.__class__.__name__
        self._requested_name = name
        self._state = None
        self._attendee = None
        self._fad = None

        # Base class methods without an override don't log enter/exit.
        self._no_transcript_for = list()
        for method in [self.on_message, self.on_default, self.on_idle,
                       self.on_quit]:
            self._no_transcript_without_override(method)

        self._Message = enum_class
        self._wake_from_idle_after = dict()

        self.meeting_members = list()
        self.timeout = 60  # Expect to respond within 60 seconds.

    def _no_transcript_without_override(self, method):
        """
        Add the method to _no_transcript_for if it isn't overridden.
        :param method: The method to test.
        :return: None
        """
        method_name = method.__name__
        # Now, walk down the class stack to see if this method changes.
        class_method = getattr(self.__class__.mro()[0], method_name, None)
        for base_class in self.__class__.mro()[1:]:
            method_base = getattr(base_class, method_name, None)
            if method_base is not None and method_base != class_method:
                # The method changed: there is an override.
                return

        # If we reached here, then this base method is not overridden,
        # so we don't need an auto transcript.
        self._no_transcript_for.append(method)

    @property
    def name(self) -> Optional[str]:
        """
        Get the Worker name, if assigned.
        :return: None or the assigned name of the Worker
        """
        if self._attendee:
            return self._attendee.name
        return None

    @property
    def state(self) -> WorkerState:
        if not self._attendee:
            new_state = WorkerState.FINAL if self._state else WorkerState.INIT
        elif self._fad.func == self.on_idle:
            new_state = WorkerState.IDLE
        else:
            new_state = WorkerState.BUSY
        # TODO : WorkerState.WORK

        if new_state != self._state:
            thread_meeting.transcribe(new_state.value,
                                      thread_meeting.TranscriptType.State)
            self._state = new_state

        return self._state

    # OVERRIDE-ABLE METHODS

    def on_default(self, name, payload) -> FuncAndData:
        """
        Process an unknown message.
        This method is called if the worker doesn't find an appropriate
        function to call from the queue item.  The default behavior is to
        ignore the item.
        :param name: The name of the message.
        :param payload: The payload (if any) of the message.
        """
        queue = self._queue()
        self._debug("Ignoring '{}'".format(name))
        return FuncAndData(self.on_message if queue else self.on_idle)

    def on_idle(self) -> Optional[FuncAndData]:
        """
        Wait for an item to be put in the queue.
        :return: The next function to be called.
        """
        while self._no_messages():
            time.sleep(0.1)
        return FuncAndData(self.on_message)

    def on_message(self) -> Optional[FuncAndData]:
        """
        Process a message from the queue.
        :param kwargs:  Ignored.
        :return: The next function to be called.
        """
        queue = self._queue()
        if not queue:
            # Weird, the message is gone.
            self._debug("on_message called without a message")
            return FuncAndData(self.on_idle)

        item = queue.get()
        fad = FuncAndData()

        func_name = "on_{}".format(item.name)
        new_func = getattr(self, func_name, None)
        if callable(new_func):
            fad.func = new_func
            fad.data = dict()
            if item.payload is not None:
                fad.data = dict(payload=item.payload)
        else:
            fad.func = self.on_default
            fad.data = dict(name=item.name, payload=item.payload)
        return fad

    def on_quit(self) -> None:
        """
        Process a QUIT message.  This should be the final message processed.
        :return: None
        """
        self._attendee = None
        return None

    # PUBLIC METHODS
    def thread_entry(self):
        """
        Thread entry point launched by start_all for each worker.
        """
        with thread_meeting.participate(self._requested_name) as self._attendee:
            self._fad = FuncAndData(self.on_idle)
            while self.state != WorkerState.FINAL:
                try:
                    # If we have any delayed messages to add to the queue,
                    # then add them (to the back).
                    self._check_for_delayed_messages()

                    # We're going to expand data as kwargs, so it must be
                    # in dict format... even if there's nothing in it.
                    data = self._fad.data if self._fad.data else dict()

                    # Don't log enter/exit for on_* functions in the base class
                    # if they are not overloaded, but do for everything else.
                    if self._fad.func in self._no_transcript_for:
                        func = self._fad.func
                    else:
                        func = transcribe_func(self, self._fad.func)

                    # Run the function and find out what the next function is.
                    if self._fad.data:
                        func_return = func(**data)
                    else:
                        func_return = func()

                    if callable(func_return):
                        # If the callee just returned the next function,
                        # there's no data.  Wrap it into a FuncAndData for them.
                        self._fad = FuncAndData(func_return)
                    elif isinstance(func_return, FuncAndData):
                        # The callee returned exactly what we want.
                        self._fad = func_return
                    elif func_return is None:
                        # No instructions.
                        if self.state == WorkerState.FINAL:
                            self._fad = None
                        elif self.state == WorkerState.IDLE:
                            self._fad = FuncAndData(self.on_idle)
                        else:
                            self._fad = FuncAndData(self.on_message)
                    else:
                        raise RuntimeError("Illegal return value from function")

                except BaseException as e:
                    self._debug("Exception detected, thread FAILED")
                    raise
        return self.state

    # PROTECTED METHODS
    def _check_for_delayed_messages(self) -> None:
        """
        Add messages to the queue if the delay has been met.
        :return: None
        """
        if not self._attendee:
            # No queue.
            return
        queue = self._attendee.queue
        keys = sorted(self._wake_from_idle_after.keys())
        now = time.time()
        for key in keys:
            if key <= now:
                self._post_to_self(item=self._wake_from_idle_after[key])
                del self._wake_from_idle_after[key]
            else:
                break

    def _debug(self, message: str) -> None:
        """
        Write a debug message to the transcript.
        :param message: The message to write.
        :return: None
        """
        thread_meeting.transcribe(message,
                                  ti_type=thread_meeting.TranscriptType.Debug)

    def _no_messages(self) -> bool:
        """
        Return True if there are no messages waiting to be processed.
        :return: True if queue is empty.
        """
        queue = self._queue()
        if queue:
            # There's a message!
            return False

        # No items in the queue means we are still idle.
        self._check_for_delayed_messages()

        # Now that we have given a chance for delayed messages to
        # be added to the queue, return whether or not the queue is empty.
        return not queue

    def _queue_message_after_delay(self, *, message: enum.Enum,
                                   delay_in_sec: float) -> None:
        """
        Post a note to this worker after no less than some specified delay.
        :param note: The message to note.
        :param delay_in_sec: The delay time in seconds.
        :return: None
        """
        target_time = time.time() + float(delay_in_sec)
        while target_time in self._wake_from_idle_after:
            target_time += 1
        self._wake_from_idle_after[target_time] = message
        self._debug("{}: Queued for delivery after {}".format(
            message.value, datetime.datetime.fromtimestamp(
            target_time).strftime('%H:%M:%S')
        ))

    def _post_to_others(self, item: enum.Enum, *, payload=None,
                        target_state: Optional[WorkerState] = None) -> bool:
        """
        Post a message to other workers.

        An exception will be raised if the item is not an instance
        of the self._Message class.

        :param item: The message to post.
        :param payload: The optional payload to post.
        :param target_state: The expected end state for the other workers.
        :return: True if message was posted.
        """
        if not isinstance(item, self._Message):
            raise ValueError("Invalid item type({} != {}".format(
                type(item), self._Message))
        with self._attendee.request_baton() as baton:
            if baton is None:
                thread_meeting.transcribe(
                    "Failed to acquire baton",
                    ti_type=thread_meeting.TranscriptType.Debug)
                return False

            keep = baton.post(item.value, payload)
            if target_state is None:
                return True

            # Wait until all messages have been at least acknowledged.
            start_time = time.time()
            end_time = start_time + max(
                [x.timeout for x in self.meeting_members])
            while keep.pending > 0 and time.time() < end_time:
                time.sleep(1)

            # In case the thread has quit (so it won't respond), we need to
            # also check for the FINAL state.
            target_states = {WorkerState.FINAL, target_state}

            # Wait for all other threads to acknowledge receiving the message.
            wait_until = dict()
            for member in self.meeting_members:
                if member == self:
                    continue
                wait_until[member] = start_time + member.timeout

            while wait_until:
                now = time.time()
                for worker in [item for item in wait_until
                               if item.state in target_states]:
                    del wait_until[worker]
                for worker, timeout in wait_until.items():
                    if timeout < now:
                        raise TimeoutError(str(worker))
                time.sleep(0.1)
        return True

    def _post_to_self(self, item: enum.Enum, *, payload=None) -> None:
        """
        Post a message to our own queue.
        This message does not raise an exception and will be
        processed whenever this object gets around to running
        _process_queue_item.

        An exception will be raised if the item is not an instance
        of the self._Message class.

        :param item: The message to post.
        :param payload: The optional payload to post.
        :return: None
        """
        if not isinstance(item, self._Message):
            raise ValueError("Invalid item type({} != {}".format(
                type(item), self._Message))
        self._attendee.note(item.value, payload)

    def _queue(self) -> thread_meeting.PeekableQueue:
        """
        Return the Attendee queue object.
        If the Attendee is invalid, raise an error.
        :return:
        """
        if self._attendee is None:
            # Raise the caller's name as the source of the error.
            raise RuntimeError("{}: Not in a meeting".format(
                inspect.stack()[1].function))
        return self._attendee.queue
