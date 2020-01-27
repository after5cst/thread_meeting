from .worker import Worker
from .decorators import interruptable


class InterruptableCounter(Worker):
    def __init__(self):
        """
        A worker that counts while not interrupted.
        """
        super().__init__()
        self.count = 0
        self.timeout = 2  # We should respond to messages in < 2 seconds.

    def on_start(self):
        """
        Go IDLE on start.
        :return: The next function to run.
        """
        return self.on_run

    @interruptable
    def on_run(self):
        try:
            while True:
                self.count += 1
        finally:
            self._debug("{}".format(int(self.count / 1000)))
