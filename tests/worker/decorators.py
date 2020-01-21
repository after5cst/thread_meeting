import thread_meeting as meeting

def transcribe_func(func):
    """
    Decorator to log a state entry and exit.
    :param func: The function to call.
    :return: The function wrapper, as expected on decorators.
    """
    def function_wrapper(*args, **kwargs):
        try:
            meeting.transcribe(func.__name__, meeting.TranscriptType.Enter)
            result = func(*args, **kwargs)
        finally:
            meeting.transcribe(func.__name__, meeting.TranscriptType.Exit)
        return result
    return function_wrapper
