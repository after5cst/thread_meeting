import unittest

import thread_meeting


class JoinTest(unittest.TestCase):
    
    def test_can_create_join(self):
        join = thread_meeting.Join()
    
    def test_can_create_two_joins_on_same_thread(self):
        join1 = thread_meeting.Join()
        join2 = thread_meeting.Join()
    
    def test_cannot_create_join_while_joined(self):
        with thread_meeting.Join():
            with self.assertRaises(ValueError) as context:
                thread_meeting.Join()
            self.assertTrue("Meeting already joined on this thread" 
                in str(context.exception))
    
    def test_cannot_enter_join_while_joined(self):
        join1 = thread_meeting.Join()
        join2 = thread_meeting.Join()
        with join1:
            with self.assertRaises(RuntimeError) as context:
                with join2:
                    pass
            self.assertTrue("Meeting already joined on thread" 
                in str(context.exception), str(context.exception))


if __name__ == '__main__':
    unittest.main()
