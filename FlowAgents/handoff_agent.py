from typing import List
from agents import Tool
from .flow_agent import FlowAgent
from .conversation_flow.importance_message import ImportanceRequest, ImportanceResponse
from IOMethods.output_methods import OutputMethod, ConsoleOutputMethod

from .handoff_utility import HandoffManager

class HandoffAgent(FlowAgent):
    def __init__(
        self,
        name: str,
        model: str = "gpt-4o-mini",
        system_prompt: str = (
            "You are a handoff agent with a set of subagents you can delegate tasks to"
        ),
        tools: List[Tool] = [],
        output_method: OutputMethod = ConsoleOutputMethod()
    ):
        super().__init__(
            name=name,
            model=model,
            system_prompt=system_prompt,
            tools=tools,
            output_method=output_method
        )
        self.handoff_manager = None
        self.subagents = []


    async def run(self, importance_request: ImportanceRequest) -> ImportanceResponse:
        self.handoff_manager.check_completed_tasks()
        response = await super().run(importance_request)

        clean_message, handoffs = self.handoff_manager.extract_handoffs(response.message)
        response.message = clean_message

        for handoff_data in handoffs:
            self.handoff_manager.start_handoff(handoff_data)

        return response

    def set_subagents(self, subagents: List[FlowAgent]):
        self.handoff_manager = HandoffManager(self, subagents)
        subagent_list_str = ", ".join([f"'{s.name}'" for s in subagents])
        self.add_developer_message(
            message=f"You can delegate tasks to these subagents: {subagent_list_str}"
        )
        self.add_developer_message(
            message=(
                "To delegate a task, include this JSON anywhere in your response: "
                '{"handoff": {"subagent": "NAME_OF_SUBAGENT", "prompt": "TASK_PROMPT"}}'
            )
        )

    def get_subagents(self):
        return self.subagents

    def list_subagents(self):
        return self.handoff_manager.list_subagents()