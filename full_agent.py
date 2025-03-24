from FlowAgents.handoff_agent import HandoffAgent, FlowAgent, ImportanceRequest
from IOMethods.output_methods import OutputMethod, ConsoleOutputMethod
from IOMethods.input_methods import InputMethod, UserCLIInputMethod
from typing import List
from agents import Tool

class FullAgent(HandoffAgent):
    def __init__(self, 
                 name: str, 
                 model: str = "gpt-4o-mini", 
                 system_prompt: str = "", 
                 subagents: List[FlowAgent] = [], 
                 tools: List[Tool] = [], 
                 output_method: OutputMethod = ConsoleOutputMethod(), 
                 input_method: InputMethod = UserCLIInputMethod("Ask the agent > "),
                 top_level_agents: List[FlowAgent] = []):
        super().__init__(name, model, system_prompt, subagents, tools, output_method)
        self.input_method = input_method
        self.top_level_agents = top_level_agents


    async def start(self):
        while self.input_method.has_next():
            request = ImportanceRequest(message=self.input_method.next())
            response = await self.run(request)
            if self.top_level_agents is not None and len(self.top_level_agents) > 0:
                for agent in self.top_level_agents:
                    response = await agent.run(ImportanceRequest(importance=1, message=self.chat_flow_manager.serialize()))
                    if response.message is not None and response.message != "":
                        self.add_system_message(importance=1, message=response.message)
            self.output_method.output(response.message)


