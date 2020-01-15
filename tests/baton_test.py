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
            self.assertTrue(attendee.name.startswith("Thread"))

    def test_attendee_can_leave_and_come_back(self):
        with thread_meeting.participate() as one:
            self.assertTrue(one.name.startswith("Thread"))
        with thread_meeting.participate() as two:
            self.assertTrue(two.name.startswith("Thread"))

    def test_cannot_recursively_use_context_manager(self):
        with thread_meeting.participate() as one:
            self.assertTrue(one.name.startswith("Thread"))
            with self.assertRaises(RuntimeError) as context:
                with thread_meeting.participate() as two:
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


if __name__ == '__main__':
    unittest.main()
