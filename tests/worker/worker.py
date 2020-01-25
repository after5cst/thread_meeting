import thread_meeting as meeting

from overrides import EnforceOverrides, final  # , overrides
import enum
import concurrent.futures
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
            meeting.transcribe("Canceled meeting with no attendees.")
            return

        with concurrent.futures.ThreadPoolExecutor(
                max_workers=len(args)) as executor:

            # We MUST have the starting baton before creating workers,
            # otherwise they WILL keep us from getting it.
            with meeting.starting_baton() as baton:
                if not baton:
                    # Should NEVER happen!
                    raise RuntimeError("Could not get starting baton!")

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
                    # If initialization takes more than 20 seconds, assume
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
                    raise

    # CONSTRUCTOR AND PROPERTIES
    def __init__(self, *, name: str, enum_class: enum.Enum = Message):
        self._requested_name = name
        self._state = None
        self._attendee = None
        self._fad = None
        self._Message = enum_class

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
        elif not self._fad:
            new_state = WorkerState.IDLE
        else:
            new_state = WorkerState.BUSY
        # TODO : WorkerState.WORK

        if new_state != self._state:
            meeting.transcribe(new_state.value, meeting.TranscriptType.State)
            self._state = new_state

        return self._state

    # OVERRIDE-ABLE METHODS
    def end_meeting(self):
        pass

    def on_default(self, data) -> FuncAndData:
        """
        This method is called if the worker doesn't find an appropriate
        function to call from the queue item.  In many cases, this item
        probably just needs to be ignored.
        :param data: A tuple of (name, payload) that was found in the queue.
        """
        name, payload = data
        meeting.transcribe("Ignoring '{}'".format(name))
        return self._fad

    def on_idle(self, payload) -> FuncAndData:
        while self._attendee and not self._attendee.queue:
            time.sleep(0.1)
        if self._attendee and self._attendee.queue:
            return FuncAndData(self.on_message())

    def on_message(self, fad: Optional[FuncAndData]
                   ) -> Optional[FuncAndData]:
        """
        Process a message from the queue.
        :param fad: The default FunctionAndData object
        :return: The possibly changed FuncAndData object
        """
        if not self._attendee.queue:
            # No items in the queue, use the default.
            return fad

        item = self._attendee.queue.get()
        fad.data = item.payload

        func_name = "on_{}".format(item.name)
        new_func = getattr(self, func_name, None)
        if callable(new_func):
            fad.func = new_func
        else:
            fad.func = self.on_default
            fad.data = (item.name, item.payload)
        return fad

    def on_start(self, payload) -> FuncAndData:
        time_delay = random.uniform(0.5, 1.5)
        time.sleep(time_delay)
        self._post_to_self(Message.QUIT)
        return FuncAndData()

    def on_quit(self, payload) -> FuncAndData:
        self._attendee = None
        return FuncAndData()

    # PUBLIC METHODS
    @final
    def thread_entry(self):
        """
        Thread entry point launched by start_all for each worker.
        """
        with meeting.participate(self._requested_name) as self._attendee:
            while self.state != WorkerState.FINAL:
                try:
                    if self.state == WorkerState.IDLE:
                        fad = FuncAndData(self.on_idle)
                    else:
                        fad = self._fad
                    fad = self.on_message(fad)
                    if fad:
                        # Wrapper the function so it will transcribe
                        # that it started/stopped.  Then call it.
                        func = transcribe_func(self, fad.func)
                        self._fad = func(fad.data)
                    else:
                        self._fad = None

                except BaseException:
                    self.end_meeting()
                    raise
        return self.state

    # PRIVATE METHODS
    def _post_to_others(self, item: enum.Enum, *, payload=None) -> None:
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
