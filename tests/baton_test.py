import unittest

import thread_meeting
from .worker import Worker



class BatonTest(unittest.TestCase):
    
    def test_can_send_message_to_worker(self):
        workers = list()
        for i in range(10):
            workers.append(Worker(name='worker_' + str(i)))
        threads = Worker.execute_meeting(*workers)
        # If we get here, then we managed to start the workers,
        # sent a start message, and the workers exited.
        # So, we sent a message to the worker(s).


if __name__ == '__main__':
    unittest.main()
