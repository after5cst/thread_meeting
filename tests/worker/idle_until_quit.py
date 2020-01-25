from .worker import FuncAndData, Worker, WorkerState
from .message import Message

from overrides import overrides
from typing import Optional


class IdleUntilQuit(Worker):
    """
    This worker just tries to stay idle until a Quit message is received.
    """
    pass

