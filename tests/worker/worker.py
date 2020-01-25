import thread_meeting

import concurrent.futures
import enum
import inspect
from overrides import EnforceOverrides, final  # , overrides
import random
import time
from typing import Optional

from .decorators import transcribe_func
from .kill_executor import kill_executor
from .message import Message
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

    # STATIC METHODS
    @staticmethod
    def execute_meeting(*args) -> None:
        """
        Launch all workers and wait for them to complete.
        The first exception found is raised, if any.
        :param args: Zero or more Worker-based objects to launch.
        :return Nothing.
        """
        if 0 == len(args):
            # A meeting with nobody in it.  Cancel it.
            thread_meeting.transcribe("Canceled meeting with no attendees.")
            return
        workers = args

        with concurrent.futures.ThreadPoolExecutor(
                max_workers=len(args)) as executor:

            # We MUST have the starting baton before creating workers,
            # otherwise they WILL keep us from getting it.
            with thread_meeting.starting_baton() as baton:
                if not baton:
                    # Should NEVER happen!
                    raise RuntimeError("Could not get starting baton!")

                for worker in workers:
                    worker.meeting_members = workers
                # Start all workers.
                futures = [executor.submit(worker.thread_entry)
                           for worker in args]

                # Wait for all workers to hit IDLE.
                ready = False
                for i in range(20):
                    states = [worker.state for worker in args]
                    if states.count(WorkerState.IDLE) == len(args):
                        ready = True
                        break
                    time.sleep(0.3)

                if not ready:
                    # If initialization takes more than 6 seconds, assume
                    # something is wrong.  Ask the living ones to quit,
                    # and then kill the zombies.
                    baton.post(Message.QUIT.value, None)
                    time.sleep(10)
                    kill_executor(executor)
                    raise RuntimeError("Worker(s) failed to reach IDLE state")

                baton.post(Message.START.value, None)  # OK, let's go!
            # Now nothing to do but wait for the end.
            for future in concurrent.futures.as_completed(futures):
                try:
                    state = future.result()
                except BaseException as e:
                    kill_executor(executor)
                    raise RuntimeError("Worker failed") from e

    # CONSTRUCTOR AND PROPERTIES
    def __init__(self, *, name: str = '', enum_class: enum.Enum = Message):
        if not name:
            name = self.__class__.__name__
        self._requested_name = name
        self._state = None
        self._attendee = None
        self._fad = None
        self._Message = enum_class
        self._wake_from_idle_after = dict()

        self.meeting_members = list()
        self.timeout = 60  # Expect to respond within 60 seconds.

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
    def end_meeting(self):
        pass

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
        queue = self._queue()
        while not queue:
            # No items in the queue means we are still idle.
            time.sleep(0.1)
            self._check_for_delayed_messages()
        # There's a message: we're no longer idle.
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
    @final
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

                    data = self._fad.data if self._fad.data else dict()

                    # Don't log enter/exit for on_message, but do for
                    # everything else.
                    if self._fad.func == self.on_message:
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
                        # No instructions.  Default to IDLE.
                        self._fad = FuncAndData(self.on_idle)
                    else:
                        raise RuntimeError("Illegal return value from function")

                except BaseException:
                    self.end_meeting()
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

    def _post_to_others(self, item: enum.Enum, *, payload=None,
                        target_state: Optional[WorkerState] = None
                        ) -> bool:
        """
        Post a message to other workers.

        An exception will be raised if the item is not an instance
        of the self._Message class.

        :param item: The message to post.
        :param payload: The optional payload to post.
        :param target_state: The state to wait for the other workers to reach.
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

            take = baton.post(item.value, payload)
            if target_state is None:
                return True
            # In case the thread has quit (so it won't respond), we need to
            # also check for the FINAL state.
            target_states = set([WorkerState.FINAL, target_state])

            # Wait for all other threads to acknowledge receiving the message.
            start_time = time.time()
            wait_until = dict()
            for member in self.meeting_members:
                if member == self:
                    continue
                wait_until[member] = start_time + member.timeout

            while wait_until:
                now = time.time()
                for worker in [worker for worker in wait_until
                               if worker.state in target_states]:
                    del wait_until[worker]
                for worker, timeout in wait_until.items():
                    if timeout < now:
                        raise TimeoutError(worker.name)
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
