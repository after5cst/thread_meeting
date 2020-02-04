from example.worker.base.worker import Worker, WorkerState
from example.worker.base.object_array_storage import ObjectArrayStorage

from thread_meeting import transcriber, TranscriptItem

from overrides import overrides
import time


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
        self.path = None
        self.meeting_in_progress = False
        self.timeout = 2  # We should respond to messages in < 2 seconds.

    def on_start(self):
        """
        Note that the meeting started.
        :return: None.  The base class will default to on_idle.
        """
        self.meeting_in_progress = True

    @overrides
    def on_idle(self):
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
            if self.meeting_in_progress and self._am_alone():
                self._debug("Last one in meeting, leaving")
                return self.on_quit
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
        with ObjectArrayStorage(TranscriptItem, target=self.path) as self.oas:
            self.path = self.oas.path
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
            still_working = [x.name for x in self.meeting_members
                             if x.state != WorkerState.FINAL]
            self.do_transcription()
        self.meeting_in_progress = False

    def _am_alone(self) -> bool:
        """
        Check is this is the last worker.
        :return: True if this is the last worker.
        """
        for worker in self.meeting_members:
            if worker is not self and worker.state != WorkerState.FINAL:
                return False
        return True
