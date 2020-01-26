from .message import Message
from .worker import FuncAndData, Worker, WorkerState
from ..utils.object_array_storage import ObjectArrayStorage

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
                try:
                    super().thread_entry()
                finally:
                    # We're in the FINAL state already, but don't actually
                    # exit the thread until all the other workers are also
                    # in the FINAL state.
                    previous = None
                    still_working = [x.name for x in self.meeting_members
                                     if x.state != WorkerState.FINAL]
                    while still_working:
                        if previous != still_working:
                            self._debug("Still working: {}".format(
                                ', '.join(still_working)))
                            previous = still_working
                        time.sleep(0.5)
                        self.do_transcription()
                        still_working = [x.name for x in self.meeting_members
                                         if x.state != WorkerState.FINAL]
