from enum import Enum


class WorkerState(Enum):
    INIT = 'Init'     # Worker has just been created
    IDLE = 'Idle'     # Worker is waiting for a message.
    BUSY = 'Busy'     # Worker has a message in the queue or is processing it.
    FINAL = 'Final'   # Worker is complete.
