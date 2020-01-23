import time
import unittest

from thread_meeting import TranscriptType as TT
from thread_meeting import TranscriptItem


class TranscriptItemTest(unittest.TestCase):
    
    def test_transcript_item_requires_message(self):
        with self.assertRaises(ValueError) as context:
            item = TranscriptItem()
        self.assertTrue("Message may not be empty"
            in str(context.exception), str(context.exception))

    def test_transcript_item_sets_defaults(self):
        before = time.time()
        # Need a sleep before and after because Transcript
        # time stamps are only ms-accurate
        time.sleep(1.0)
        item = TranscriptItem('hi')
        time.sleep(1.0)
        after = time.time()
        self.assertEqual(item.message, 'hi')
        self.assertEqual(item.ti_type, TT.Custom)
        # This should be on the primary thread, so the name is set.
        self.assertEqual(item.source, '(primary)')
        self.assertEqual(item.destination, '(primary)')
        self.assertGreater(item.timestamp, before)
        self.assertLess(item.timestamp, after)

    def test_transcript_item_can_init_type(self):
        item = TranscriptItem('message', TT.Ack)
        self.assertEqual(item.ti_type, TT.Ack)

    def test_transcript_item_cannot_change_values(self):
        item = TranscriptItem('message')
        item = TranscriptItem('hi')

        with self.assertRaises(AttributeError) as context:
            item.source = 'text'
        self.assertTrue("can't set attribute"
            in str(context.exception), str(context.exception))

        with self.assertRaises(AttributeError) as context:
            item.destination = 'text'
        self.assertTrue("can't set attribute"
            in str(context.exception), str(context.exception))

        with self.assertRaises(AttributeError) as context:
            item.message = 'text'
        self.assertTrue("can't set attribute"
            in str(context.exception), str(context.exception))

        with self.assertRaises(AttributeError) as context:
            item.ti_type = TT.Custom
        self.assertTrue("can't set attribute"
            in str(context.exception), str(context.exception))

        with self.assertRaises(AttributeError) as context:
            item.timestamp = time.time()
        self.assertTrue("can't set attribute"
            in str(context.exception), str(context.exception))

if __name__ == '__main__':
    unittest.main()
