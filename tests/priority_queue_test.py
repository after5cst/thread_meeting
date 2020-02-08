import time
import unittest

import thread_meeting


class PriorityQueueTest(unittest.TestCase):
    
    def check_empty(self, q: thread_meeting.PriorityQueue):
        self.assertFalse(q)
        self.assertIsNone(q.get())
        
    def test_queue_starts_empty(self):
        q = thread_meeting.PriorityQueue()
        self.check_empty(q)

    def test_can_append_to_queue(self):
        q = thread_meeting.PriorityQueue()
        q.push_low(1)
        self.assertTrue(q)
        self.assertEqual(q.get(), 1)
        self.check_empty(q)

    def test_queue_items_are_in_order(self):
        q = thread_meeting.PriorityQueue()
        for i in range(10):
            q.push_low(i)
        for i in range(10):
            self.assertEqual(q.get(), i)
        self.check_empty(q)

    def test_queue_priorities(self):
        q = thread_meeting.PriorityQueue()
        q.push_future(1, delay_in_sec=1)
        q.push_low(2)
        q.push_high(3)
        self.assertEqual(q.get(False), 3)
        self.assertEqual(q.get(), 2)
        self.check_empty(q)
        time.sleep(1)
        self.assertEqual(q.get(), 1)

    def test_queue_purge(self):
        q = thread_meeting.PriorityQueue()
        q.push_future(1, delay_in_sec=1)
        q.push_low(2)
        q.push_high(3)
        self.assertEqual(q.get(), 3)
        self.check_empty(q)
        time.sleep(1)
        self.check_empty(q)

    def test_queue_delays(self):
        q = thread_meeting.PriorityQueue()
        q.push_future(1, delay_in_sec=2)
        q.push_future(2, delay_in_sec=1.5)
        q.push_future(3, delay_in_sec=1)
        self.check_empty(q)
        time.sleep(2)
        self.assertEqual(q.get(), 3)
        self.assertEqual(q.get(), 2)
        self.assertEqual(q.get(), 1)


if __name__ == '__main__':
    unittest.main()
