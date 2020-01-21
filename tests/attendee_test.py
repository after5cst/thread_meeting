import threading
import time
import unittest

import thread_meeting


class AttendeeTest(unittest.TestCase):
    
    def test_cannot_directly_create_attendee(self):
        with self.assertRaises(TypeError) as context:
            thread_meeting.Attendee("Bilbo")
        self.assertTrue("No constructor defined!"
            in str(context.exception), str(context.exception))

    def test_can_create_attendee_indirectly(self):
        with thread_meeting.participate("Bilbo") as attendee:
            self.assertIsInstance(attendee, thread_meeting.Attendee)

    def test_attendee_knows_name(self):
        with thread_meeting.participate("Bilbo") as attendee:
            self.assertEqual("Bilbo", attendee.name)

    def test_attendee_name_will_default(self):
        with thread_meeting.participate() as attendee:
            self.assertEqual("(primary)", attendee.name)

    def test_attendee_can_leave_and_come_back(self):
        with thread_meeting.participate() as one:
            self.assertEqual("(primary)", one.name)
        with thread_meeting.participate() as two:
            self.assertEqual("(primary)", two.name)

    def test_cannot_recursively_use_context_manager(self):
        with thread_meeting.participate() as one:
            self.assertEqual("(primary)", one.name)
            with self.assertRaises(RuntimeError) as context:
                with thread_meeting.participate():
                    pass
            self.assertTrue("' already present"
                in str(context.exception), str(context.exception))

    def test_attendee_can_change_names_while_gone(self):
        with thread_meeting.participate("Bilbo") as one:
            self.assertEqual(one.name, "Bilbo")
        with thread_meeting.participate("Baggins") as one:
            self.assertEqual(one.name, "Baggins")

    def test_attendee_cannot_change_name_in_meeting(self):
        with thread_meeting.participate("Bilbo") as one:
            with self.assertRaises(AttributeError) as context:
                one.name = "Baggins"
            self.assertTrue("can't set attribute"
                in str(context.exception), str(context.exception))

    def test_attendee_can_get_baton(self):
        with thread_meeting.participate("Bilbo") as me:
            with me.request_baton() as baton:
                self.assertIsNotNone(baton)

    def test_attendee_cannot_recursively_get_baton(self):
        with thread_meeting.participate("Bilbo") as me:
            with me.request_baton() as baton:
                self.assertIsNotNone(baton)
                with me.request_baton() as baton2:
                    self.assertIsNone(baton2)

    def test_attendee_can_get_baton_twice(self):
        with thread_meeting.participate("Bilbo") as me:
            with me.request_baton() as baton:
                self.assertIsNotNone(baton)
            with me.request_baton() as baton:
                self.assertIsNotNone(baton)

    @staticmethod
    def hold_baton(data: dict):
        with thread_meeting.participate("hold_baton") as me:
            with me.request_baton() as baton:
                data['baton'] = baton
                data['state'] = 'baton'
                while data['state'] == 'baton':
                    time.sleep(0.1)
            data['state'] = 'done'
            while data['state'] == 'done':
                time.sleep(0.1)

    def test_attendee_cannot_get_baton_held_in_other_thread(self):
        data = dict(state='before')
        worker = threading.Thread(target=self.hold_baton, args=(data,))
        worker.start()
        while data['state'] == 'before':
            time.sleep(0.1)
        with thread_meeting.participate("Bilbo") as me:
            # The worker should have the baton, we should not.
            with me.request_baton() as baton:
                self.assertIsNone(baton)
                self.assertTrue(data['baton'])
            data['state'] = 'after'
            while data['state'] == 'after':
                time.sleep(0.1)
            # Worker should have given up the baton, we can wait.
            self.assertFalse(data['baton'])
            with me.request_baton() as baton:
                self.assertIsNotNone(baton)
        # Tell the worker to quit, and wait on it.
        data['state'] = 'quit'
        worker.join()

    def test_can_find_me_in_scope(self):
        with thread_meeting.participate("Bilbo") as bilbo:
            # Find bilbo through a function call.
            me = thread_meeting.me()
            self.assertEqual(me.name, bilbo.name)
            self.assertTrue(bilbo)
            self.assertTrue(me)
            # Ensure they are equivalent: get the baton with me.
            with me.request_baton() as baton:
                self.assertIsNotNone(baton)
        # Ensure that bilbo and me both went invalid when
        # we left the 'with' statement.
        self.assertFalse(bilbo)
        self.assertFalse(me)
        # And ensure that if I try to find me outside the with,
        # only None is returned.
        me = thread_meeting.me()
        self.assertIsNone(me)

    def test_attendee_can_use_queue(self):
        with thread_meeting.participate("Bilbo"):
            # could have also use ... `as me` in the with statement.
            queue = thread_meeting.me().queue
            self.assertFalse(queue)
            thread_meeting.me().note("one", 1)
            self.assertTrue(queue)
            self.assertIsInstance(queue.head, thread_meeting.Take)
            self.assertEqual(queue.head.payload, 1)
            self.assertEqual(queue.head.name, "one")
            self.assertEqual(queue.get().payload, 1)
            self.assertFalse(queue)


if __name__ == '__main__':
    unittest.main()
