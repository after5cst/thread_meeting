from .base.worker import Worker


class RaiseOnStart(Worker):
    def __init__(self):
        """
        A worker that raises an uncaught exception in on_start.
        """
        super().__init__()
        self.count = 0
        self.timeout = 2  # We should respond to messages in < 2 seconds.

    def on_start(self):
        """
        Raise an exception.  Useful for unit testing.
        """
        raise RuntimeError("I crashed (on purpose)")
