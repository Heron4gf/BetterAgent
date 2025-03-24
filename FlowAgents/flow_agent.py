from .conversation_flow.chat_flow_manager import ChatFlowManager
from agents import Agent, Runner
from .conversation_flow.importance_message import DeveloperMessage, ImportanceRequest, ImportanceResponse
from agents import Tool
from typing import List
from .load_client import load_client, isClientLoaded
from IOMethods.output_methods import OutputMethod, ConsoleOutputMethod

DEFAULT_INPUT = "Continue working on the request"

class FlowAgent():

    def __init__(self, 
                 name : str, 
                 model : str = "gpt-4o-mini", 
                 system_prompt : str = "", 
                 tools : List[Tool] = [], 
                 output_method : OutputMethod = ConsoleOutputMethod()):
        """
        Initialize the flow agent
        @param name: the name of the agent
        @param model: the model to use
        @param system_prompt: the system prompt to use
        @param tools: the tools to use
        """
        self.name = name
        self.tools = tools
        self.model = model
        self.chat_flow_manager = ChatFlowManager()  
        self.add_developer_message(message=system_prompt)
        self.output_method = output_method
        self.output_method.output(f"Agent {self.name} initialized")

    def add_user_message(self, importance : int, message : str):
        """
        Add a user message to the chat flow manager
        @param importance: the importance of the message
        @param message: the message to add
        """
        self.chat_flow_manager.add_message(ImportanceRequest(importance=importance, message=message))

    def add_developer_message(self, message : str):
        """
        Add a developer message to the chat flow manager
        @param message: the message to add
        """
        self.chat_flow_manager.add_message(DeveloperMessage(message=message))
    
    def add_system_message(self, importance : int, message : str):
        """
        Add a system message to the chat flow manager
        @param importance: the importance of the message
        @param message: the message to add
        """
        self.chat_flow_manager.add_message(ImportanceResponse(importance=importance, message=message))

    async def run(self, importance_request : ImportanceRequest) -> ImportanceResponse:
        """
        Runs the agent
        @param input: the input of the agent
        """
        
        instructions = self.chat_flow_manager.serialize()

        if not isClientLoaded():
            load_client()
        agent = Agent(
            name=self.name,
            instructions=instructions,
            model=self.model,
            tools=self.tools
        )
        
        if(importance_request.message is None):
            importance_request.message = DEFAULT_INPUT
        
        self.chat_flow_manager.add_message(importance_request)
        result = await Runner.run(agent, importance_request.message)
        response = ImportanceResponse(message=result.final_output)
        self.output_method.output(f"{self.name}: {response.message}")

        self.chat_flow_manager.add_message(response)
        return response

        
