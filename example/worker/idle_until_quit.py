from example.worker.base.worker import Worker


class IdleUntilQuit(Worker):
    """
    This worker just tries to stay idle until a Quit message is received.
    """
    pass
