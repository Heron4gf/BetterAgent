from .flow_agent import FlowAgent
from typing import List
from agents import function_tool, Tool
from .conversation_flow.importance_message import ImportanceRequest, ImportanceResponse
from IOMethods.output_methods import OutputMethod, ConsoleOutputMethod
import json
from typing import Dict


_subagents : List[FlowAgent] = []

class HandoffAgent(FlowAgent):

    HANDOFF_JSON_FORMAT = """
    {"handoff":
        {
            "subagent": "subagent_name",
            "prompt": "prompt"
        }
    }
    """

    async def handoffAndOutPutInConversation(self, subagent: str, prompt: str) -> str:
        """
        Handoff the conversation to the given subagent and output the response in the conversation
        @param subagent: the name of the subagent to handoff to
        @param prompt: the prompt to handoff
        """
        self.add_system_message(importance=1, message="Handoff to " + subagent + " with prompt: " + prompt)
        response = await self.handoffToSubagent(subagent, prompt)
        response.message = "Response from " + subagent + ": " + response.message
        self.add_system_message(importance=15, message=response.message)

    async def handoffToSubagent(self, subagent: str, prompt: str) -> str:
        """
        Handoff the conversation to the given subagent
        @param subagent: the name of the subagent to handoff to
        @param prompt: the prompt to handoff
        """
        for sub in _subagents:
            if sub.name == subagent:
                response = await sub.run(ImportanceRequest(importance=1, message=prompt))
                return response.message
        return "Subagent not found"
    
    def __init__(self, 
                 name : str, 
                 model : str = "gpt-4o-mini", 
                 system_prompt : str = "You are an handoff agent with a set of subagents you can handoff to using the handoffToSubagent tool", 
                 subagents : List[FlowAgent] = [], 
                 tools : List[Tool] = [],
                 output_method : OutputMethod = ConsoleOutputMethod()):
        """
        Initialize the handoff agent
        @param name: the name of the agent
        @param model: the model to use
        @param system_prompt: the system prompt to use
        @param subagents: the subagents to use
        """
        super().__init__(name=name, model=model, system_prompt=system_prompt, tools=tools, output_method=output_method)
        self.subagents = subagents
        global _subagents
        for sub in self.subagents:
            _subagents.append(sub)
        self.add_developer_message(message="Subagents: " + ", ".join(self.list_subagents()))
        self.add_developer_message(message="Notice you may handoff to the same subagent multiple times at once to have multiple instances of it working on a different prompt")
        self.add_developer_message(message="On each interaction you will receive an update of the handed off subagents working, and you will eventually receive the output of them")
        self.add_developer_message(message="You may handoff to a subagent (or multiple in the same message) using the following format: " + self.HANDOFF_JSON_FORMAT)

    async def run(self, importance_request : ImportanceRequest) -> ImportanceResponse:
        """
        Runs the agent
        @param input: the input of the agent
        """
        response = await super().run(importance_request)    
        handoffs = self._parse_handoffs(response.message)
        for handoff in handoffs:
            if handoff["subagent"] in self.list_subagents():
                # run the handoff
                self.handoffAndOutPutInConversation(handoff["subagent"], handoff["prompt"])
       
        response.message = self._strip_handoffs(response.message)


        return response

    def _strip_handoffs(self, message : str) -> str:
        """
        Strip the handoffs from the message
        @param message: the message to strip
        """
        return message.replace(self.HANDOFF_JSON_FORMAT, "")

    def _parse_handoffs(self, message : str) -> List[Dict[str, str]]:
        """
        Parse the handoffs from the message (which may contain multiple handoffs and also a message to not parse)
        @param message: the message to parse
        """
        # check if the message contains a handoff
        if self.HANDOFF_JSON_FORMAT in message:
            # parse the handoffs
            return json.loads(message)
        else:
            return [{"subagent": "self", "prompt": message}]

    def list_subagents(self):
        """
        List all subagents
        """
        return [sub.name for sub in self.subagents]
