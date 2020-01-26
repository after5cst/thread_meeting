import unittest

if __name__ == '__main__':
    from worker import Worker
    from worker import WorkerState
    # Worker-derived classes
    from worker import IdleUntilQuit
    from worker import InterruptableCounter
    from worker import RecordMeeting
    from worker import TimedQuit
else:
    from .worker import Worker
    from .worker import WorkerState
    # Worker-derived classes
    from .worker import IdleUntilQuit
    from .worker import InterruptableCounter
    from .worker import RecordMeeting
    from .worker import TimedQuit


class BatonTest(unittest.TestCase):

    def test_can_send_message_to_worker(self):
        workers = [RecordMeeting(), IdleUntilQuit(), TimedQuit(5),
                   InterruptableCounter()]
        try:
            Worker.execute_meeting(*workers)
            # If we get here, then we managed to start the workers,
            # sent a start message, and the workers exited.
            # So, we sent a message to the worker(s).
            for worker in workers:
                self.assertTrue(worker.state == WorkerState.FINAL)
        finally:
            oas = workers[0].oas
            print('oas_path={}'.format(oas.path))
            if oas.path.is_file():
                print(oas)
                oas.path.unlink()


if __name__ == '__main__':
    unittest.main()
