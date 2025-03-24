from ToolsLoader.tool import BaseTool
from typing import List

class ToolMapper:
    """
    A class that maps tool names to tool classes
    """
    def __init__(self):
        self.tool_map = {}

    def add_tool(self, base_tool: BaseTool):
        self.tool_map[base_tool.name] = base_tool

    def get_tool(self, tool_name: str) -> BaseTool:
        return self.tool_map[tool_name]

    def get_all_tools(self) -> List[BaseTool]:
        return list(self.tool_map.values())
