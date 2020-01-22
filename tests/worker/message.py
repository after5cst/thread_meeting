from enum import Enum


# Each enum value maps to a on_(value) method in the worker class.
# The base Worker class requires the following messages:
# START and QUIT.  More messages can be added as needed.
class Message(Enum):
    START = 'start'
    QUIT = 'quit'
