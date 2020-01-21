import unittest

import thread_meeting
from .worker import Worker



class BatonTest(unittest.TestCase):
    
    def test_can_send_message_to_worker(self):
        try:
            with thread_meeting.transcriber() as transcriber:
                workers = list()
                for i in range(2):
                    workers.append(Worker(name='worker' + str(i)))
                threads = Worker.execute_meeting(*workers)
        finally:
            while transcriber:
                print(transcriber.get())


if __name__ == '__main__':
    unittest.main()
