from enum import Enum
from IOMethods.output_methods import ConsoleOutputMethod

class OutputType(Enum):
    CONSOLE = ConsoleOutputMethod()
    NO = None

