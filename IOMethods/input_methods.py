from abc import ABC, abstractmethod

class InputMethod(ABC):

    def __init__(self):
        self.open = True

    def has_next(self) -> bool:
        return self.open

    def next(self) -> str:
        if not self.has_next():
            raise Exception("No more input")
        return self._input()
    
    def close(self):
        self.open = False

    @abstractmethod
    def _input(self) -> str:
        pass

class UserCLIInputMethod(InputMethod):

    def __init__(self, request_message: str):
        super().__init__()
        self.request_message = request_message

    def _input(self) -> str:
        return input(self.request_message)

class FileInputMethod(InputMethod):

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        self.line = 0

    def _input(self) -> str:
        with open(self.file_path, "r") as file:
            lines = file.readlines()
            if self.line >= len(lines):
                self.close()
                return None
            line = lines[self.line]
            self.line += 1
            return line