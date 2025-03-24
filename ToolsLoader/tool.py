from typing import List, Callable
from agents import Tool

class BaseTool(Tool):
    def __init__(self, name: str, description: str, author: str, version: str, functions: List[Callable]):
        self.name = name
        self.description = description
        self.author = author
        self.version = version
