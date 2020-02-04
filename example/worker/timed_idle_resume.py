import thread_meeting

from .base.worker import Worker, WorkerState
from .base.decorators import with_baton
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
    def on_timer(self, *, baton: thread_meeting.Baton) -> None:

        if self.resume_count < self.max_resumes:
            message = Message.GO_IDLE
            expected_state = WorkerState.IDLE
            self.resume_count += 1
        else:
            message = Message.QUIT
            expected_state = WorkerState.FINAL

        # Send message to others, and wait for them to reach expected state.
        keep = baton.post(message.value)
        self._wait_for_keep_acknowledgements(keep)
        self._wait_for_workers_to_reach_state(expected_state)

        if expected_state == WorkerState.IDLE:
            # Everyone is IDLE, now start them again.
            message = Message.START
            keep = baton.post(message.value)
            self._wait_for_keep_acknowledgements(keep)

        # And give myself the same last message we sent out.
        self._post_to_self(message=message)
