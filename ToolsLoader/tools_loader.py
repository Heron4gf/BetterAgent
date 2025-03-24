from ToolsLoader.tool_mapper import ToolMapper
from ToolsLoader.tool import BaseTool
from typing import List

class ToolsLoader:
    def __init__(self, path: str):
        self.path = path
        self.tool_mapper = ToolMapper()

    def load_tools(self) -> List[BaseTool]:
        pass

