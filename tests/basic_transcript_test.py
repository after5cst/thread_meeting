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
        # The first item in the transcript is the start message
        # automatically created by the transcriber.  Throw it out.
        self.assertEqual(transcriber.get().message_type, TT.Enter)

        # See that the item was added to the transcriber
        self.assertEqual(transcriber.get(), item)

        # The next item in the transcript is the end message
        # automatically created by the transcriber.  Throw it out.
        self.assertEqual(transcriber.get().message_type, TT.Exit)
        # There should be no more messages!
        self.assertFalse(transcriber)


if __name__ == '__main__':
    unittest.main()
