from .worker import Worker, WorkerState
from .message import Message


class TimedQuit(Worker):

    def __init__(self, wait_in_seconds: int = 0):
        """
        A worker that waits and then sends a quit message.
        :param wait_in_seconds: Delay before sending the quit message.
        """
        super().__init__()
        self._queue_message_after_delay(message=Message.TIMER,
                                        delay_in_sec=wait_in_seconds)

    def on_start(self):
        """
        Go IDLE on start.
        :return: The next function to run.
        """
        return self.on_idle

    def on_timer(self):
        if not self._post_to_others(Message.QUIT,
                                    target_state=WorkerState.FINAL):
            # Message was not posted, try again later.
            return self.on_timer
        return self.on_quit
