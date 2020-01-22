from thread_meeting import transcriber
import unittest

from .worker import Worker
from .worker import WorkerState


class BatonTest(unittest.TestCase):

    def test_can_send_message_to_worker(self):
        with transcriber() as transcript:
            queue = transcript  # Keep transcript from losing scope.
            workers = [Worker(name='worker') for i in range(10)]
            Worker.execute_meeting(*workers)
            # If we get here, then we managed to start the workers,
            # sent a start message, and the workers exited.
            # So, we sent a message to the worker(s).
            for worker in workers:
                self.assertTrue(worker.state == WorkerState.FINAL)
        while queue:
            queue.get()  # print(queue.get())


if __name__ == '__main__':
    unittest.main()
