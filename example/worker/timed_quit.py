from example.worker.base.worker import Worker, WorkerState
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

    def on_timer(self):
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
        my_message = Message.TIMER
        if self._post_to_others(message=Message.QUIT,
                                target_state=WorkerState.FINAL):
            my_message = Message.QUIT
        # Post a message in our Queue.  This is done rather than
        # returning the next function to call because we want to
        # ensure that the message is not dropped by having
        # a message in the queue.
        self._post_to_self(item=my_message)
        return self.on_message
