from .worker import Worker


class Counter(Worker):
    def __init__(self):
        """
        A worker that counts and checks for messages.
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

    def on_run(self):
        while self._no_messages():
            for i in range(1000):
                self.count += 1
        self._debug("{}".format(int(self.count / 1000)))
