import unittest

import thread_meeting


class EnterExitTest(unittest.TestCase):
    
    def create_enter_exit_instance(self):
        """
        Since EnterExit objects can't be directly created,
        this helper function returns something that is
        an EnterExit object.
        """
        return thread_meeting.participate("Me")

    def test_cannot_directly_create_enter_exit(self):
        with self.assertRaises(TypeError) as context:
            thread_meeting._EnterExit()
        self.assertTrue("No constructor defined!"
            in str(context.exception), str(context.exception))

    def test_can_create_enter_exit_indirectly(self):
        self.create_enter_exit_instance()

    def test_can_create_two_on_same_thread(self):
        one = self.create_enter_exit_instance()
        two = self.create_enter_exit_instance()
    
    def test_can_serialize_context_manager_on_same_thread(self):
        one = self.create_enter_exit_instance()
        with one:
            pass
        with one:
            pass
    
    def test_cannot_recursively_use_enter_exit(self):
        one = self.create_enter_exit_instance()
        with one:
            with self.assertRaises(RuntimeError) as context:
                with one:
                    pass
            self.assertTrue("object in use by ContextManager"
                in str(context.exception), str(context.exception))
    

if __name__ == '__main__':
    unittest.main()
