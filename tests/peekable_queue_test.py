import time
import unittest

import thread_meeting


class PeekableQueueTest(unittest.TestCase):
    
    def check_empty(self, q: thread_meeting.PeekableQueue):
        self.assertFalse(q)
        self.assertIsNone(q.head)
        self.assertIsNone(q.get())
        
    def test_queue_starts_empty(self):
        q = thread_meeting.PeekableQueue()
        self.check_empty(q)

    def test_can_append_to_queue(self):
        q = thread_meeting.PeekableQueue()
        q.append(1)
        self.assertTrue(q)
        self.assertEqual(q.head, 1)
        self.assertEqual(q.get(), 1)
        self.check_empty(q)

    def test_queue_items_are_in_order(self):
        q = thread_meeting.PeekableQueue()
        for i in range(10):
            q.append(i)
        for i in range(10):
            self.assertEqual(q.head, i)
            self.assertEqual(q.get(), i)
        self.check_empty(q)

    def test_queue_head_and_get_can_be_separated(self):
        q = thread_meeting.PeekableQueue()
        for i in range(10):
            q.append(i)
            
        i = q.head # Will be zero.
        while q:
            try:
                temp = q.head
                self.assertEqual(i, temp)
                i += 1
            finally:
                q.get() # discard head
        self.check_empty(q)
        self.assertEqual(temp, i-1)

    def test_queue_priorities(self):
        q = thread_meeting.PeekableQueue()
        q.append(1, delay_in_sec=1)
        q.append(2)
        with thread_meeting.participate():
            q.append(3)
        self.assertEqual(q.get(), 2)
        self.assertEqual(q.get(), 3)
        self.check_empty(q)
        time.sleep(1)
        self.assertEqual(q.get(), 1)

    def test_queue_purge(self):
        q = thread_meeting.PeekableQueue()
        q.append(1, delay_in_sec=1)
        q.append(2)
        with thread_meeting.participate("", is_admin=True):
            q.append(3)
        self.assertEqual(q.get(), 3)
        self.check_empty(q)
        time.sleep(1)
        self.check_empty(q)

    def test_queue_delays(self):
        q = thread_meeting.PeekableQueue()
        q.append(1, delay_in_sec=2)
        q.append(2, delay_in_sec=1)
        q.append(3, delay_in_sec=1)
        self.check_empty(q)
        time.sleep(2)
        self.assertEqual(q.get(), 2)
        self.assertEqual(q.get(), 3)
        self.assertEqual(q.get(), 1)


if __name__ == '__main__':
    unittest.main()
