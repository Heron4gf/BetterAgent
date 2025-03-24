from abc import ABC, abstractmethod

class OutputMethod(ABC):
    @abstractmethod
    def output(self, message: str):
        pass

class ConsoleOutputMethod(OutputMethod):
    def output(self, message: str):
        print(message)

class FileOutputMethod(OutputMethod):
    def __init__(self, file_path: str):
        self.file_path = file_path  

    def output(self, message: str):
        with open(self.file_path, "a") as file:
            file.write(message + "\n")
