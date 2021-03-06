import gc
import unittest

import thread_meeting


_KEEP_NAME = 'my name'
_ANOTHER_KEEP_NAME = 'something else'
_DEFAULT_KEEP_COUNT = 3


class TakeTest(unittest.TestCase):
    
    def setUp(self):
        self.keep = thread_meeting.Keep(_KEEP_NAME, None)
        self.takes = [ 
            self.keep.create_take() for i in range(_DEFAULT_KEEP_COUNT)
            ]
        
    def tearDown(self):
        del(self.takes)
        del(self.keep)
        
    def test_can_setup(self):
        pass
    
    def test_can_read_take_name(self):
        for i in range(_DEFAULT_KEEP_COUNT):
            self.assertEqual(self.keep.name, self.takes[i].name)

    def test_cannot_change_take_name(self):
        take = self.takes[0]
        with self.assertRaises(AttributeError) as context:
            take.name = _KEEP_NAME
        self.assertTrue("can't set attribute" in str(context.exception))

    def test_initial_take_status_is_pending(self):
        take = self.takes[0]
        self.assertEqual(take.status, thread_meeting.TakeStatus.Pending)

    def test_set_take_to_acknowledged(self):
        take = self.takes[0]
        take.acknowledge()
        self.assertEqual(take.status, thread_meeting.TakeStatus.Acknowledged)

    def test_set_take_to_protested(self):
        take = self.takes[0]
        take.protest()
        self.assertEqual(take.status, thread_meeting.TakeStatus.Protested)

    def test_set_can_set_take_status_to_same(self):
        take = self.takes[0]
        take.acknowledge()
        take.acknowledge()
        self.assertEqual(take.status, thread_meeting.TakeStatus.Acknowledged)
        take = self.takes[1]
        take.protest()
        take.protest()
        self.assertEqual(take.status, thread_meeting.TakeStatus.Protested)

    def test_cannot_change_take_status(self):
        take = self.takes[0]
        take.protest()
        with self.assertRaises(ValueError) as context:
            take.acknowledge()
        self.assertTrue("Can't change status" in str(context.exception),
            str(context.exception))
        self.assertEqual(take.status, thread_meeting.TakeStatus.Protested)
        
        take = self.takes[1]
        take.acknowledge()
        with self.assertRaises(ValueError) as context:
            take.protest()
        self.assertTrue("Can't change status" in str(context.exception))
        self.assertEqual(take.status, thread_meeting.TakeStatus.Acknowledged)
        
    def test_keep_sees_change_to_manual_acknowledge(self):
        take = self.takes[0]
        self.assertEqual(_DEFAULT_KEEP_COUNT, self.keep.pending)
        self.assertEqual(0, self.keep.acknowledged)
        self.assertEqual(0, self.keep.protested)
        take.acknowledge()
        self.assertEqual(_DEFAULT_KEEP_COUNT - 1, self.keep.pending)
        self.assertEqual(1, self.keep.acknowledged)
        self.assertEqual(0, self.keep.protested)
        
    def test_keep_sees_change_to_manual_protest(self):
        take = self.takes[0]
        self.assertEqual(_DEFAULT_KEEP_COUNT, self.keep.pending)
        self.assertEqual(0, self.keep.acknowledged)
        self.assertEqual(0, self.keep.protested)
        take.protest()
        self.assertEqual(_DEFAULT_KEEP_COUNT - 1, self.keep.pending)
        self.assertEqual(0, self.keep.acknowledged)
        self.assertEqual(1, self.keep.protested)
        
    def test_keep_sees_change_to_default_acknowledge(self):
        self.assertEqual(_DEFAULT_KEEP_COUNT, self.keep.pending)
        self.assertEqual(0, self.keep.acknowledged)
        self.assertEqual(0, self.keep.protested)
        self.takes[0] = None  # Remove the take: it should be auto-acknowledged.
        self.assertEqual(_DEFAULT_KEEP_COUNT - 1, self.keep.pending)
        self.assertEqual(1, self.keep.acknowledged)
        self.assertEqual(0, self.keep.protested)
    

if __name__ == '__main__':
    unittest.main()
