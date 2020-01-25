from thread_meeting import transcriber, TranscriptItem

import unittest

if __name__ == '__main__':
    from utils.object_array_storage import ObjectArrayStorage
    from worker import Worker
    from worker import WorkerState
    from worker import IdleUntilQuit
else:
    from .utils.object_array_storage import ObjectArrayStorage
    from .worker import Worker
    from .worker import WorkerState
    # Worker-derived classes
    from .worker import IdleUntilQuit
    from .worker import TimedQuit


class BatonTest(unittest.TestCase):

    def test_can_send_message_to_worker(self):
        queue = None
        try:
            with transcriber() as transcript:
                workers = [IdleUntilQuit(), TimedQuit(5)]
                queue = transcript  # Keep transcript from losing scope.
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
                oas.path.unlink()


if __name__ == '__main__':
    unittest.main()
