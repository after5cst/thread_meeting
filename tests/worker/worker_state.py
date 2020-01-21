from enum import Enum

class WorkerState(Enum):
    INIT = 'Init'     # Worker has just been created
    IDLE = 'Idle'     # Worker is waiting for a message.
    BATON = 'Baton'   # Worker has the baton, can send to others.
    BUSY = 'Busy'     # Worker is doing something, will check for messages.
    WORK = 'Work'     # Worker is doing something, can be 'raised'
    FINAL = 'Final'   # Worker is complete.
