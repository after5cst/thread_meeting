import unittest

import thread_meeting
from thread_meeting import transcribe
from thread_meeting import TranscriptionType as TT
from thread_meeting import TranscriptionItem as TI


class BasicTranscriptionTest(unittest.TestCase):

    def verify_transcription_items(self, transcriber, *args):
        for arg in args:
            self.assertIsInstance(arg, TI)
            item = transcriber.get()
            self.assertIsInstance(item, TI)
            self.assertEqual(arg.message_type, item.message_type)
            self.assertTrue(arg.message in item.message,
                "'{}' not in '{}'".format(arg.message, item.message)
                )
        if transcriber:
            self.assertFalse(bool(transcriber), "Unexpected item '{}:{}'".format(
                transcriber.head.message_type, transcriber.head.message
                ))
    
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
        transcribe("Hello")

    def test_transcribe_returns_none_without_transcriber(self):
        message = "Message will be dropped"
        item = transcribe(message)
        self.assertEqual(item, None)

    def test_transcribe_returns_item_with_transcriber(self):
        message = "Message will be returned"
        with thread_meeting.transcriber() as transcriber:
            item = transcribe(message)
            self.assertEqual(item.message, message)
        expected = (
            TI('Transcript started', TT.Enter),
            TI(message, TT.Custom),
            TI('Transcript ended', TT.Exit)
            )
        self.verify_transcription_items(transcriber, *expected)

    def test_transcribe_sees_attendee_enter_exit(self):
        with thread_meeting.transcriber() as transcriber:
            with thread_meeting.participate("Bilbo"):
                pass
            with thread_meeting.participate("Baggins"):
                pass
        expected = (
            TI('Transcript started', TT.Enter),
            TI('Bilbo', TT.Enter),
            TI('Bilbo', TT.Exit),
            TI('Baggins', TT.Enter),
            TI('Baggins', TT.Exit),
            TI('Transcript ended', TT.Exit)
            )
        self.verify_transcription_items(transcriber, *expected)

    def test_transcribe_sees_baton_enter_exit(self):
        with thread_meeting.transcriber() as transcriber:
            with thread_meeting.participate("Bilbo") as bilbo:
                with bilbo.request_baton():
                    pass
        expected = (
            TI('Transcript started', TT.Enter),
            TI('Bilbo', TT.Enter),
            TI('Baton', TT.Enter),
            TI('Baton', TT.Exit),
            TI('Bilbo', TT.Exit),
            TI('Transcript ended', TT.Exit)
            )
        self.verify_transcription_items(transcriber, *expected)


if __name__ == '__main__':
    unittest.main()
