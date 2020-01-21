import thread_meeting as meeting

from overrides import EnforceOverrides, final, overrides
import ctypes
import concurrent.futures
import time
from typing import List, Optional, Tuple

from .worker_state import WorkerState
from .decorators import transcribe_func


def terminate_thread(thread):
    """Terminates a python thread from another thread.

    :param thread: a threading.Thread instance
    """
    if not thread.isAlive():
        return

    exc = ctypes.py_object(SystemExit)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(thread.ident), exc)
    if res == 0:
        raise ValueError("nonexistent thread id")
    elif res > 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")



class FuncAndData:
    def __init__(self, func = None, data = None):
        self.func = func
        self.data = data
        
    def __bool__(self):
        return self.func is not None
        
    def exec(self):
        if (self.func):
            self.func(self.data)
        

class Worker(EnforceOverrides):
    
    # STATIC METHODS
    @staticmethod
    def execute_meeting( *args ) -> None:
        """
        Launch all workers and wait for them to complete.
        The first exception found is raised, if any.
        :param args: Zero or more Worker-based objects to launch.
        :return Nothing.
        """
        if 0 == len(args):
            # A meeting with nobody in it.  Cancel it.
            meeting.transcribe("Canceled meeting with no attendees.")
            return

        with concurrent.futures.ThreadPoolExecutor(
                max_workers=len(args)) as executor:
            
            # We MUST have the starting baton before creating workers,
            # otherwise they WILL keep us from getting it.
            with meeting.starting_baton() as baton:
                if not baton:
                    # Should NEVER happen!
                    raise RuntimeError("Could not get starting baton!")
                
                # Start all workers.
                futures = [executor.submit(worker.thread_entry)
                                for worker in args]
                
                # Wait for all workers to hit IDLE.
                ready = False
                for i in range(20):
                    states = [worker.state for worker in args]
                    if states.count(WorkerState.IDLE) == len(args):
                        ready = True
                        break
                    time.sleep(0.3)
                    
                if not ready:
                    executor.shutdown(wait=False)
                    for t in executor._threads:
                        terminate_thread(t)
                    raise RuntimeError("Boom! {}".format(states))
                    
                baton.post("start", None)  # OK, let's go!
                
            # Now nothing to do but wait for the end.
            for future in concurrent.futures.as_completed(futures):
                try:
                    state = future.result()
                except BaseException as e:
                    print("BOOM! {}".format(e))
                    # TODO : Kill other threads?
                    executor.shutdown(wait=False)
                    raise

    # CONSTRUCTOR AND PROPERTIES
    def __init__(self, *, name : str):
        self._requested_name = name
        self._state = None
        self._attendee = None
        self._fad = None
        
    @property
    def name(self) -> Optional[str]:
        """
        Get the Worker name, if assigned.
        :return None or the assigned name of the Worker
        """
        if self._attendee:
            return self._attendee.name
        return None
        
    @property
    def state(self) -> WorkerState:
        if not self._attendee:
            new_state = WorkerState.FINAL if self._state else WorkerState.INIT
        elif not self._fad:
            new_state = WorkerState.IDLE
        else:
            new_state = WorkerState.BUSY
        # TODO : WorkerState.WORK
            
        if new_state != self._state:
            meeting.transcribe(new_state.value, meeting.TranscriptType.State)
            self._state = new_state
            
        return self._state

    # OVERRIDE-ABLE METHODS
    def end_meeting(self):
        pass
        
    def on_default(self, data) -> FuncAndData:
        """
        This method is called if the worker doesn't find an appropriate
        function to call from the queue item.  In many cases, this item
        probably just needs to be ignored.
        :param data: A tuple of (name, payload) that was found in the queue.
        """
        name, payload = data
        meeting.transcribe("Ignoring '{}'".format(name))
        return self._fad
        
    def on_idle(self, data) -> FuncAndData:
        while self._attendee and not self._attendee.queue:
            time.sleep(0.1)
        return None
        
    def on_start(self, data) -> FuncAndData:
        self._attendee.note("quit", data)
        
    def on_quit(self, data) -> FuncAndData:
        self._attendee = None
        
    # PUBLIC METHODS
    @final
    def thread_entry(self):
        """
        Thread entry point launched by start_all for each worker.
        """
        with meeting.participate(self._requested_name) as self._attendee:
            while self.state != WorkerState.FINAL:
                try:
                    if self.state == WorkerState.IDLE:
                        fad = FuncAndData(self.on_idle)
                    else:
                        fad = self._fad
                    fad = self._process_queue_item(fad)
                    if fad:
                        # Wrapper the function so it will transcribe
                        # that it started/stopped.  Then call it.
                        func = transcribe_func(fad.func)
                        self._fad = func(fad.data)
                    else:
                        self._fad = None
                        
                except:
                    self.end_meeting()
                    raise
        return self.state
        
    # PRIVATE METHODS
    def _process_queue_item(self, fad: Optional[FuncAndData]
            ) -> Optional[FuncAndData]:
        """
        Process a message from the queue.
        :param fad: The default FunctionAndData object
        :return: The possibly changed FuncAndData object
        """
        if not self._attendee.queue:
            # No items in the queue, use the default.
            return fad
            
        item = self._attendee.queue.get()
        fad.data = item.payload
        
        func_name = "on_{}".format(item.name)
        new_func = getattr(self, func_name, None)
        if callable(new_func):
            fad.func = new_func
        else:
            fad.func = self.on_default
            fad.data = (item.name, item.payload)
        return fad








