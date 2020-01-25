from .worker import Worker, FuncAndData


class IdleUntilQuit(Worker):

    def on_start(self):
        """
        Handle start message.
        This simple example just returns to IDLE state.
        :return:
        """
        return self.on_idle
