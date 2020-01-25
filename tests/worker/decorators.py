import thread_meeting as meeting


def transcribe_func(state_object, func):
    """
    Decorator to log a state entry and exit.
    :param state_object: An object to reference the .state attribute.
    :param func: The function to call.
    :return: The function wrapper, as expected on decorators.
    """
    def function_wrapper(*args, **kwargs):
        current_state = state_object.state
        message = "Method:{}()".format(func.__name__)
        try:
            meeting.transcribe(message, meeting.TranscriptType.Enter)
            result = func(*args, **kwargs)
        finally:
            meeting.transcribe(message, meeting.TranscriptType.Exit)
        return result
    return function_wrapper
