import functools
import time
from typing import Optional

import thread_meeting as meeting
from ..message import Message


class Interruption(Exception):
    """Simple exception that notes the thread was interrupted."""
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
        name = func.__name__  # if not hasattr(func, 'name') else func.name
        message = "Method:{}()".format(name)
        try:
            meeting.transcribe(message, meeting.TranscriptType.Enter)
            result = func(*args, **kwargs)
        except Interruption:
            meeting.transcribe("Interrupted", meeting.TranscriptType.Custom)
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
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        attendee = meeting.me()
        with attendee.interrupt_with(Interruption):
            result = func(*args, **kwargs)
        return result
    # _wrapper.name = func.__name__
    return _wrapper


def with_baton(*, message: Optional[Message] = None, payload=None):
    def decorator_with_baton(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            attendee = meeting.me()
            with attendee.request_baton() as baton:

                if baton is None:
                    meeting.transcribe(
                        "Failed to acquire baton",
                        ti_type=meeting.TranscriptType.Debug)
                    if message is not None:
                        time.sleep(0.1)
                        attendee.note(message.value, payload)
                    return None

                modified_kwargs = {k: v for k, v in kwargs.items()}
                result = func(*args, baton=baton, **modified_kwargs)
            return result
        return _wrapper
    return decorator_with_baton
