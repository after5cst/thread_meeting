import concurrent.futures
import thread_meeting
import time

from .message import Message
from .base.worker_state import WorkerState


def execute_meeting(*args) -> None:
    """
    Launch all workers and wait for them to complete.
    The first exception found is raised, if any.
    :param args: Zero or more Worker-based objects to launch.
    :return Nothing.
    """
    if 0 == len(args):
        # A meeting with nobody in it.  Cancel it.
        thread_meeting.transcribe("Canceled meeting with no attendees.")
        return
    workers = args

    with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(args)) as executor:
        # We MUST have the starting baton before creating workers,
        # otherwise they WILL keep us from getting it.
        baton = thread_meeting.primary_baton()
        if not baton:
            # Should NEVER happen!
            raise RuntimeError("Could not get starting baton!")

        try:
            futures = list()
            workers_are_idle = True
            for worker in workers:
                # Start the worker
                worker.meeting_members = workers
                futures.append(executor.submit(worker.thread_entry))

                # Wait for the worker to hit IDLE.
                for i in range(30):
                    state = worker.state
                    if state == WorkerState.IDLE:
                        break
                    time.sleep(0.3)

                if not WorkerState.IDLE == state:
                    # If initialization takes more than 9 seconds, assume
                    # something is wrong.  The Worker has likely generated
                    # an exception.  We will catch it below.
                    workers_are_idle = False
                    break

            if workers_are_idle:
                baton.post(Message.START.value, None)  # OK, let's go!

            # Now nothing to do but wait for workers to end.  If they 'raise'
            # then future.result() here will also raise.
            for future in concurrent.futures.as_completed(futures):
                future.result()

        except BaseException as e:
            thread_meeting.transcribe(
                "Exception in primary thread")
            baton.post(Message.QUIT.value, None)
            raise
