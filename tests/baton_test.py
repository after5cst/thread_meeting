import unittest

if __name__ == '__main__':
    from worker import Worker
    from worker import WorkerState
    # Worker-derived classes
    from worker import Counter
    from worker import IdleUntilQuit
    from worker import InterruptableCounter
    from worker import RaiseOnStart
    from worker import RecordMeeting
    from worker import TimedQuit
else:
    from .worker import Worker
    from .worker import WorkerState
    # Worker-derived classes
    from .worker import Counter
    from .worker import IdleUntilQuit
    from .worker import InterruptableCounter
    from .worker import RaiseOnStart
    from .worker import RecordMeeting
    from .worker import TimedQuit


class BatonTest(unittest.TestCase):

    def test_can_send_message_to_worker(self):
        recorder = RecordMeeting()
        workers = [
            recorder,
            IdleUntilQuit(),
            TimedQuit(5),
            Counter(),
            InterruptableCounter()
        ]

        try:
            Worker.execute_meeting(*workers)
            # If we get here, then we managed to start the workers,
            # sent a start message, and the workers exited.
            # So, we sent a message to the worker(s).
            for worker in workers:
                self.assertTrue(worker.state == WorkerState.FINAL)
        except BaseException:
            oas = recorder.oas
            if oas and oas.path and oas.path.is_file():
                print(oas)
                oas.path.unlink()
            raise

    def test_can_execute_two_meetings(self):
        recorder = RecordMeeting()

        try:
            workers = [
                recorder
            ]
            for i in range(2):
                Worker.execute_meeting(*workers)
                # If we get here, then we managed to start the workers,
                # sent a start message, and the workers exited.
                # So, we sent a message to the worker(s).
                for worker in workers:
                    self.assertTrue(worker.state == WorkerState.FINAL)
        except BaseException:
            oas = recorder.oas
            if oas and oas.path and oas.path.is_file():
                print(oas)
                oas.path.unlink()
            raise

    def test_can_detect_worker_raise(self):
        recorder = RecordMeeting()
        workers = [
            recorder,
            IdleUntilQuit(),
            RaiseOnStart()
        ]
        with self.assertRaises(RuntimeError) as context:
            Worker.execute_meeting(*workers)
        self.assertTrue("I crashed (on purpose)"
                        in str(context.exception), str(context.exception))


if __name__ == '__main__':
    unittest.main()
