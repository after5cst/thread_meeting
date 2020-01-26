from .worker import Worker
from .decorators import interruptable
import time


class InterruptableCounter(Worker):
    """
    This worker just tries to stay idle until a Quit message is received.
    """

    def __init__(self):
        """
        A worker that counts while not interrupted.
        """
        super().__init__()
        self.count = 0

    def on_start(self):
        """
        Go IDLE on start.
        :return: The next function to run.
        """
        return self.on_run

    @interruptable
    def on_run(self):
        while True:
            self.count += 1
            time.sleep(0.1)

