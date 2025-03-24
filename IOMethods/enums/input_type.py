from enum import Enum
from IOMethods.input_methods import UserCLIInputMethod, FileInputMethod

class InputType(Enum):
    USER_CLI = UserCLIInputMethod("Ask the agent > ")
    NO = None
