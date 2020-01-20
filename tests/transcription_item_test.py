from datetime import datetime
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
        before = datetime.now()
        item = TranscriptItem('hi')
        after = datetime.now()
        self.assertEqual(item.message, 'hi')
        self.assertEqual(item.message_type, TT.Custom)
        # This should be on the primary thread, so the name is set.
        self.assertEqual(item.source, '(primary)')
        self.assertEqual(item.destination, '(primary)')
        self.assertGreaterEqual(item.timestamp, before)
        self.assertLessEqual(item.timestamp, after)

    def test_transcript_item_can_init_type(self):
        item = TranscriptItem('message', TT.Ack)
        self.assertEqual(item.message_type, TT.Ack)

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
            item.message_type = TT.Custom
        self.assertTrue("can't set attribute"
            in str(context.exception), str(context.exception))

        with self.assertRaises(AttributeError) as context:
            item.timestamp = datetime.now()
        self.assertTrue("can't set attribute"
            in str(context.exception), str(context.exception))

if __name__ == '__main__':
    unittest.main()
