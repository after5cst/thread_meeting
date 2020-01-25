import thread_meeting

import ctypes
import concurrent.futures


def terminate_thread(thread):
    """Terminates a python thread from another thread.

    :param thread: a threading.Thread instance
    """
    # Use non-deprecated function if available.
    living = thread.is_alive if hasattr(thread, 'is_alive') else thread.isAlive
    if not living():
        return

    exc = ctypes.py_object(SystemExit)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(thread.ident), exc)
    if res == 0:
        pass
    elif res > 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)


def kill_executor(executor: concurrent.futures.ThreadPoolExecutor) -> None:
    """
    Attempt to kill all threads in the executor.
    :param executor: The executor to use.
    :return: None
    """
    executor.shutdown(wait=False)
    for t in executor._threads:
        msg = "Killing thread {}".format(t.ident)
        thread_meeting.transcribe(msg)
        terminate_thread(t)
