from example.worker.base.worker import Worker
from example.worker.base.decorators import interruptable


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
        Process the start message.  We want to start running.
        :return: The on_run method.
        """
        return self.on_run

    @interruptable
    def on_run(self):
        try:
            while True:
                self.count += 1
        finally:
            self._debug("{}".format(int(self.count / 1000)))
