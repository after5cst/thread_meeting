import pathlib
import sys
import unittest

_THIS_DIR = pathlib.Path(__file__).parent

if __name__ == '__main__':
    sys.path.append(_THIS_DIR)

from example.worker import execute_meeting
from example.worker import WorkerState
# Worker-derived classes
from example.worker import Counter
from example.worker import IdleUntilQuit
from example.worker import InterruptableCounter
from example.worker import RaiseOnStart
from example.worker import RecordMeeting
from example.worker import TimedQuit
from example.worker import TimedIdleResume


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
            execute_meeting(*workers)
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
                execute_meeting(*workers)
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
            execute_meeting(*workers)
        self.assertTrue("I crashed (on purpose)"
                        in str(context.exception), str(context.exception))

    def test_can_pause_and_resume_workers(self):
        recorder = RecordMeeting()
        workers = [
            recorder,
            IdleUntilQuit(),
            TimedIdleResume(2,3),
            TimedQuit(10)
        ]
        execute_meeting(*workers)
        oas = recorder.oas
        if oas and oas.path and oas.path.is_file():
            print(oas)
            oas.path.unlink()
        self.assertTrue(False)


if __name__ == '__main__':
    unittest.main()
