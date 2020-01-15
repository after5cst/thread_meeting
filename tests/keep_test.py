import unittest

import thread_meeting


_KEEP_NAME = 'my name'


class KeepTest(unittest.TestCase):
    
    def test_can_read_name(self):
        keep = thread_meeting.Keep(_KEEP_NAME, None)
        self.assertEqual(_KEEP_NAME, keep.name)
        self.assertEqual(None, keep.payload)

    def test_cannot_change_name(self):
        keep = thread_meeting.Keep(_KEEP_NAME, None)
        self.assertEqual(_KEEP_NAME, keep.name)
        
        new_name = _KEEP_NAME.upper()
        self.assertNotEqual(keep.name, new_name)
        
        with self.assertRaises(AttributeError) as context:
            keep.name = new_name
        self.assertTrue("can't set attribute" in str(context.exception))
    
    def test_keep_starts_with_no_takes(self):
        keep = thread_meeting.Keep(_KEEP_NAME)
        self.assertListEqual(keep.acknowledged, list())
        self.assertListEqual(keep.pending, list())
        self.assertListEqual(keep.protested, list())

if __name__ == '__main__':
    unittest.main()
