from .message import Message
from .worker import FuncAndData, Worker, WorkerState
try:
    from ..utils.object_array_storage import ObjectArrayStorage
except ValueError:
    # If the unit tests were run from the command line, then
    # the above gives an error:
    #   ValueError: attempted relative import beyond top-level package
    # This then retries assuming we're running from the tests directory.
    from utils.object_array_storage import ObjectArrayStorage

from thread_meeting import transcriber, TranscriptItem

from overrides import overrides
import time
from typing import Optional


class RecordMeeting(Worker):
    """
    A "court reporter" for the meeting.

    This worker is very atypical, and does things that normal workers don't,
    since it needs to constantly be reporting events.
    """
    def __init__(self):
        super().__init__()
        self.transcript = None
        self.oas = None
        self.timeout = 2  # We should respond to messages in < 2 seconds.

    @overrides
    def on_idle(self) -> Optional[FuncAndData]:
        """
        Process transcript items while we wait for messages.
        This could also be done with a timer, but it really clutters
        the log with information that isn't helpful.
        :return: The next function to be called.
        """
        queue = self._queue()
        while not queue:
            # No items in the queue means we are still idle.
            time.sleep(0.5)
            self.do_transcription()
            self._check_for_delayed_messages()
        # There's a message: we're no longer idle.
        return self.on_message

    def do_transcription(self):
        while self.transcript:
            self.oas.append(self.transcript.get())

    @overrides
    def thread_entry(self):
        """
        Perform the thread functions within the context of a reporting
        scenario.
        """
        with ObjectArrayStorage(TranscriptItem) as self.oas:
            with transcriber() as self.transcript:
                super().thread_entry()
            self.do_transcription()

    @overrides
    def on_quit(self) -> None:
        super().on_quit()  # Mark ourselves as quit.
        # But still hang around to log events until everyone else
        # has quit.
        previous = None
        sleep_time = 1.0
        still_working = [x.name for x in self.meeting_members
                         if x.state != WorkerState.FINAL]
        while still_working:
            if previous != still_working:
                self._debug("Waiting on: {}".format(
                    ', '.join(still_working)))
                previous = still_working
            time.sleep(sleep_time)
            self.do_transcription()
            still_working = [x.name for x in self.meeting_members
                             if x.state != WorkerState.FINAL]
