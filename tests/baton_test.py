from thread_meeting import transcriber, TranscriptItem

import unittest

if __name__ == '__main__':
    from utils.object_array_storage import ObjectArrayStorage
    from worker import Worker
    from worker import WorkerState
else:
    from .utils.object_array_storage import ObjectArrayStorage
    from .worker import Worker
    from .worker import WorkerState


class BatonTest(unittest.TestCase):

    def test_can_send_message_to_worker(self):
        queue = None
        try:
            with transcriber() as transcript:
                queue = transcript  # Keep transcript from losing scope.
                workers = [Worker(name='worker') for i in range(2)]
                Worker.execute_meeting(*workers)
                # If we get here, then we managed to start the workers,
                # sent a start message, and the workers exited.
                # So, we sent a message to the worker(s).
                for worker in workers:
                    self.assertTrue(worker.state == WorkerState.FINAL)
        finally:
            with ObjectArrayStorage(TranscriptItem) as oas:
                while queue:
                    oas.append(queue.get())

        print('oas_path={}'.format(oas.path))
        if oas.path.is_file():
            print(oas)


if __name__ == '__main__':
    unittest.main()
