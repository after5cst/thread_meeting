import thread_meeting
from .base.worker import Worker, WorkerState
from .base.decorators import with_baton
from .message import Message


class TimedQuit(Worker):

    def __init__(self, wait_in_seconds: int = 0):
        """
        A worker that waits and then sends a quit message.
        :param wait_in_seconds: Delay before sending the quit message.
        """
        super().__init__()
        self.delay_in_sec = wait_in_seconds

    def on_start(self):
        """
        Set a timer to go off delay_in_sec seconds after start.
        :return: None.
        """
        self._queue_message_after_delay(message=Message.TIMER,
                                        delay_in_sec=self.delay_in_sec)

    @with_baton(message=Message.TIMER)
    def on_timer(self, *, baton: thread_meeting.Baton):
        """
        Tell other workers to quit.
        In order to give instructions to the other workers, the _post_to_others
        function must acquire the baton.

        If it does, and posts the quit message to others, then post a message
        to this worker to quit.

        If it does not, then post another TIMER message to this worker so
        we can try again.

        :return: The on_message function.
        """
        message = Message.QUIT
        # Tell others to quit.
        keep = baton.post(message.value)
        # Wait for them to receive the message.
        self._wait_for_keep_acknowledgements(keep)
        # Wait for them to actually quit.
        self._wait_for_workers_to_reach_state(WorkerState.FINAL)
        # And tell myself to quit.
        self._post_to_self(message=message)
