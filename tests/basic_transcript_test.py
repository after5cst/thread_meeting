import unittest

import thread_meeting
from thread_meeting import transcribe
from thread_meeting import TranscriptionType as TT


class BasicTranscriptionTest(unittest.TestCase):
    
    def test_transcribe_requires_message(self):
        with self.assertRaises(TypeError) as context:
            transcribe()
        self.assertTrue("incompatible function arguments"
            in str(context.exception), str(context.exception))

    def test_transcribe_requires_valid_transcription_type(self):
        with self.assertRaises(TypeError) as context:
            transcribe("Hello", 1)
        self.assertTrue("incompatible function arguments"
            in str(context.exception), str(context.exception))

    def test_transcribe_can_succeed(self):
        item = transcribe("Hello")

    def test_transcribe_returns_none_without_transcriber(self):
        message = "Message will be dropped"
        item = transcribe(message)
        self.assertEqual(item, None)

    def test_transcribe_returns_item_with_transcriber(self):
        message = "Message will be returned"
        with thread_meeting.transcriber() as transcriber:
            item = transcribe(message)
            self.assertEqual(item.message, message)
        # See that the item was added to the transcriber
        self.assertEqual(transcriber.get(), item)
        # And that 'get' removed it, and there are no more
        self.assertFalse(transcriber)


if __name__ == '__main__':
    unittest.main()
