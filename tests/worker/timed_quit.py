from .worker import FuncAndData, Worker, WorkerState
from .message import Message

from overrides import overrides
from typing import Optional


class TimedQuit(Worker):

    def __init__(self, wait_in_seconds: int = 0):
        """
        A worker that waits and then sends a quit message.
        :param wait_in_seconds: Delay before sending the quit message.
        """
        super().__init__()
        self.delay_in_sec = wait_in_seconds
        self.timeout = 2  # We should respond to messages in < 2 seconds.

    def on_start(self):
        """
        Go IDLE on start.
        :return: The next function to run.
        """
        self._queue_message_after_delay(message=Message.TIMER,
                                        delay_in_sec=self.delay_in_sec)
        return self.on_idle

    def on_timer(self):
        """
        Tell other workers to quit.
        If this is successful,
        :return:
        """
        my_message = Message.TIMER
        if self._post_to_others(Message.QUIT,
                                target_state=WorkerState.FINAL):
            my_message = Message.QUIT
        # Post a message in our Queue.  This is done rather than
        # returning the next function to call because we want to
        # ensure that the message is not dropped by having
        # a message in the queue.
        self._post_to_self(item=my_message)
        return self.on_message
