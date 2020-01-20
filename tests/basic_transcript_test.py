import unittest

import thread_meeting
from thread_meeting import transcribe
from thread_meeting import TranscriptType as TT
from thread_meeting import TranscriptItem as TI

dump = False

class BasicTranscriptTest(unittest.TestCase):
    
    def setUp(this):
        global dump
        dump = False

    def verify_transcript_items(self, transcriber, *args):
        for arg in args:
            self.assertIsInstance(arg, TI)
            item = transcriber.get()
            if dump:
                print(item)
            self.assertIsInstance(item, TI)
            self.assertEqual(arg.message_type, item.message_type)
            self.assertTrue(arg.message in item.message,
                "'{}' not in '{}'".format(arg.message, item.message)
                )
            self.assertEqual(arg.message, item.message)
        if transcriber:
            self.assertFalse(bool(transcriber), "Unexpected item '{}:{}'".format(
                transcriber.head.message_type, transcriber.head.message
                ))
    
    def test_transcribe_requires_message(self):
        with self.assertRaises(TypeError) as context:
            transcribe()
        self.assertTrue("incompatible function arguments"
            in str(context.exception), str(context.exception))

    def test_transcribe_requires_valid_transcript_type(self):
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
            self.assertIsNotNone(transcriber)
            item = transcribe(message)
            self.assertIsNotNone(item)
            self.assertEqual(item.message, message)
        expected = (
            TI('Transcript', TT.Enter),
            TI(message, TT.Custom),
            TI('Transcript', TT.Exit)
            )
        self.verify_transcript_items(transcriber, *expected)

    def test_transcribe_sees_attendee_enter_exit(self):
        with thread_meeting.transcriber() as transcriber:
            with thread_meeting.participate("Bilbo"):
                pass
            with thread_meeting.participate("Baggins"):
                pass
        expected = (
            TI('Transcript', TT.Enter),
            TI('Bilbo', TT.Enter),
            TI('Bilbo', TT.Exit),
            TI('Baggins', TT.Enter),
            TI('Baggins', TT.Exit),
            TI('Transcript', TT.Exit)
            )
        self.verify_transcript_items(transcriber, *expected)

    def test_transcribe_sees_baton_enter_exit(self):
        with thread_meeting.transcriber() as transcriber:
            with thread_meeting.participate("Bilbo") as bilbo:
                with bilbo.request_baton():
                    pass
        expected = (
            TI('Transcript', TT.Enter),
            TI('Bilbo', TT.Enter),
            TI('Baton', TT.Enter),
            TI('Baton', TT.Exit),
            TI('Bilbo', TT.Exit),
            TI('Transcript', TT.Exit)
            )
        self.verify_transcript_items(transcriber, *expected)

    def test_transcribe_sees_baton_enter_exit_with_exception(self):
        with thread_meeting.transcriber() as transcriber:
            with self.assertRaises(RuntimeError) as context:
                with thread_meeting.participate("Bilbo") as bilbo:
                    with bilbo.request_baton():
                        raise RuntimeError('this error is expected')
            self.assertTrue("this error is expected"
                in str(context.exception), str(context.exception))
        expected = (
            TI('Transcript', TT.Enter),
            TI('Bilbo', TT.Enter),
            TI('Baton', TT.Enter),
            TI('Baton', TT.Exit),
            TI('Bilbo', TT.Exit),
            TI('Transcript', TT.Exit)
            )
        self.verify_transcript_items(transcriber, *expected)

    def test_transcribe_sees_attendee_add_to_queue(self):
        with thread_meeting.transcriber() as transcriber:    # ENTER Transcript
            with thread_meeting.participate("Bilbo") as me:  # ENTER Bilbo
                me.note("Ring", "The One Ring")              # NOTE Ring
                me.note("Sword", "Sting")                    # NOTE Sword
                me.queue.get().protest()                     # NACK Ring
                # exit with scope here                       # EXIT Bilbo
            me.queue.get()                                   # ACK sword
            # exit with scope here                           # EXIT Transcript
        expected = (
            TI('Transcript', TT.Enter),
            TI('Bilbo', TT.Enter),
            TI('Ring', TT.Note),
            TI('Sword', TT.Note),
            TI('Ring', TT.Nack),
            TI('Bilbo', TT.Exit),
            TI('Sword', TT.Ack),
            TI('Transcript', TT.Exit)
            )
        self.verify_transcript_items(transcriber, *expected)


if __name__ == '__main__':
    unittest.main()
