from example.worker.base.worker import Worker, WorkerState
from example.worker.base.decorators import with_baton
from .message import Message


class TimedIdleResume(Worker):

    def __init__(self, wait_in_seconds: int = 0,
                 max_resumes: int = 3):
        """
        A worker that controls other workers.
        :param wait_in_seconds: Delay before sending each message.
        """
        super().__init__()
        self.delay_in_sec = wait_in_seconds
        self.resume_count = 0
        self.max_resumes = max_resumes

    def on_start(self):
        """
        Set a timer to go off delay_in_sec seconds after start.
        :return: None.
        """
        self._queue_message_after_delay(message=Message.TIMER,
                                        delay_in_sec=self.delay_in_sec)

    @with_baton(message=Message.TIMER)
    def on_timer(self, *, baton, message, payload):
        """
        Control other workers.

        :return: The next function to run.
        """
        # my_message = Message.TIMER
        # if self._post_to_others(Message.QUIT,
        #                         target_state=WorkerState.FINAL):
        #     my_message = Message.QUIT
        # # Post a message in our Queue.  This is done rather than
        # # returning the next function to call because we want to
        # # ensure that the message is not dropped by having
        # # a message in the queue.
        # self._post_to_self(message=my_message)
        # return self.on_message
        pass
