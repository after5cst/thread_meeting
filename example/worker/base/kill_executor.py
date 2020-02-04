import thread_meeting

import ctypes
import concurrent.futures
import os
import time


def thread_is_alive(thread) -> bool:
    return thread.is_alive if hasattr(thread, 'is_alive') else thread.isAlive


def terminate_thread(thread) -> bool:
    """Terminates a python thread from another thread.

    :param thread: a threading.Thread instance
    """
    # Use non-deprecated function if available.

    if not thread_is_alive(thread):
        return True

    exc = ctypes.py_object(SystemExit)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(thread.ident), exc)
    if res == 0:
        return True
    elif res > 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)
    return False


def kill_executor(executor: concurrent.futures.ThreadPoolExecutor) -> None:
    """
    Attempt to kill all threads in the executor.
    :param executor: The executor to use.
    :return: None
    """
    executor.shutdown(wait=False)
    no_need_to_die = True

    for t in executor._threads:
        print("no_need_to_die={}".format(no_need_to_die))
        no_need_to_die &= terminate_thread(t)
        msg = "Killing thread {}".format(t.ident)
        thread_meeting.transcribe(msg)

    if not no_need_to_die:
        print("Deliberate app crash.")
        # os._exit(-1)
