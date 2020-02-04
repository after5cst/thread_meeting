from example.worker.base.worker import Worker


class IdleUntilQuit(Worker):
    """
    This worker just tries to stay idle until a Quit message is received.
    """
    def __init__(self):
        super().__init__()
        self.timeout = 2  # We should respond to messages in < 2 seconds.

