import thread_meeting as meeting


class Interruption(Exception):
    pass


def transcribe_func(state_object, func):
    """
    Decorator to log a state entry and exit.
    :param state_object: An object to reference the .state attribute.
    :param func: The function to call.
    :return: The function wrapper, as expected on decorators.
    """
    def _wrapper(*args, **kwargs):
        current_state = state_object.state
        name = func.__name__ if not hasattr(func, 'name') else func.name
        message = "Method:{}()".format(name)
        try:
            meeting.transcribe(message, meeting.TranscriptType.Enter)
            result = func(*args, **kwargs)
        except Interruption:
            meeting.transcribe("Interrupted!", meeting.TranscriptType.Custom)
            result = None
        finally:
            meeting.transcribe(message, meeting.TranscriptType.Exit)
        return result
    return _wrapper


def interruptable(func):
    """
    Decorator to set the thread's attendee to interruptable while in scope.
    :param func: The function to call.
    :return: The function wrapper, as expected on decorators.
    """
    def _wrapper(*args, **kwargs):
        attendee = meeting.me()
        with attendee.interrupt_with(Interruption):
            result = func(*args, **kwargs)
        return result
    _wrapper.name = func.__name__
    return _wrapper

