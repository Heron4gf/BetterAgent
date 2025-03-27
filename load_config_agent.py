from FlowAgents.flow_agent import FlowAgent
from typing import List, Dict, Any
from IOMethods.enums.input_type import InputType
from IOMethods.enums.output_type import OutputType
from IOMethods.input_methods import InputMethod
from IOMethods.output_methods import OutputMethod
from full_agent import FullAgent
from FlowAgents.handoff_agent import HandoffAgent

import yaml

class AgentsLoader:
    def __init__(self, path: str):
        self.path = path
        with open(path, "r") as file:
            config = yaml.safe_load(file)
        self.config = config

    def load_agents(self) -> List[FlowAgent]:
        agents = []
        
        # Process all top-level agents
        for agent_name, agent_config in self.config.get("agents", {}).items():
            agent_config['name'] = agent_name

            # First agent is a FullAgent, others are HandoffAgents
            if len(agents) == 0:
                agent = self._load_agent(agent_config, is_full=True)
            else:
                agent = self._load_agent(agent_config)
            
            # Recursively load subagents for this agent
            self._load_agents_recursively(agent_config, agent)
            
            agents.append(agent)
        
        return agents

    def _load_agents_recursively(self, config: Dict[str, Any], parent_agent: FlowAgent) -> None:
        subagents = []
        
        # Load all subagents
        for subagent_name, subagent_config in config.get("subagents", {}).items():
            subagent_config['name'] = subagent_name
            subagent = self._load_agent(subagent_config)
            
            # Recursively process any nested subagents
            self._load_agents_recursively(subagent_config, subagent)
            
            subagents.append(subagent)
        
        # Set the subagents on the parent agent
        parent_agent.set_subagents(subagents)

    def _load_agent(self, config: Dict[str, Any], is_full: bool = False) -> FlowAgent:
        name = config.get('name', 'unnamed_agent')
        model = config.get('model', 'gpt-4o-mini')
        system_prompt = config.get('system_prompt', '')
        
        # Process knowledge files/folders if any
        knowledge = config.get('knowledge', [])
        # In a real implementation, we'd load and process these knowledge files here
        
        # Process tools if any
        tools = []
        for tool_name in config.get('tools', []):
            # In a real implementation, we'd load actual tool objects based on names
            pass
        
        output_method = self.load_output_method()
        
        if is_full:
            # Create a FullAgent with input and output methods
            input_method = self.load_input_method()
            agent = FullAgent(
                name=name,
                model=model,
                system_prompt=system_prompt,
                tools=tools,
                output_method=output_method,
                input_method=input_method
            )
        else:
            # Create a HandoffAgent with just the output method
            agent = HandoffAgent(
                name=name,
                model=model,
                system_prompt=system_prompt,
                tools=tools,
                output_method=output_method
            )
            
        # If there's knowledge, add it as developer messages
        for k in knowledge:
            agent.add_developer_message(message=f"Knowledge from {k}")
            
        return agent

    def load_input_method(self) -> InputMethod:
        return InputType[self.config["input"]].value

    def load_output_method(self) -> OutputMethod:
        return OutputType[self.config["output"]].value
