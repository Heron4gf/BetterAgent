from .flow_agent import FlowAgent
from typing import List, Dict, Any
from agents import Tool
from .conversation_flow.importance_message import ImportanceRequest, ImportanceResponse
from IOMethods.output_methods import OutputMethod, ConsoleOutputMethod
import json
import re
import asyncio

class HandoffAgent(FlowAgent):
    def __init__(self, 
                 name: str, 
                 model: str = "gpt-4o-mini", 
                 system_prompt: str = "You are a handoff agent with a set of subagents you can delegate tasks to", 
                 subagents: List[FlowAgent] = [], 
                 tools: List[Tool] = [],
                 output_method: OutputMethod = ConsoleOutputMethod()):
        """Initialize the handoff agent"""
        super().__init__(name=name, model=model, system_prompt=system_prompt, 
                         tools=tools, output_method=output_method)
        self.subagents = subagents
        self.pending_tasks = {}  # Store task objects
        self.handoff_results = {}  # Store completed results
        
        # Instructions about handoff capabilities
        subagent_list = ", ".join([f"'{sub.name}'" for sub in self.subagents])
        self.add_developer_message(
            message=f"You can delegate tasks to these subagents: {subagent_list}"
        )
        self.add_developer_message(
            message="To delegate a task, include this JSON anywhere in your response: {\"handoff\": {\"subagent\": \"name\", \"prompt\": \"task\"}}"
        )

    async def run(self, importance_request: ImportanceRequest) -> ImportanceResponse:
        """Process the request and handle handoffs"""
        # First check for completed tasks from previous handoffs
        self._check_completed_tasks()
        
        # Run the main agent
        response = await super().run(importance_request)
        
        # Process any handoffs in the response
        clean_message, handoffs = self._extract_handoffs(response.message)
        response.message = clean_message
        
        # Start any new handoffs (without awaiting them)
        for handoff in handoffs:
            self._start_handoff(handoff)
        
        return response

    def _start_handoff(self, handoff: Dict[str, str]) -> None:
        """Start a handoff without awaiting completion"""
        subagent_name = handoff.get("subagent")
        prompt = handoff.get("prompt")
        
        # Validate inputs
        if not subagent_name or not prompt:
            self.add_system_message(importance=5, message="Invalid handoff format")
            return
            
        # Find the target subagent
        subagent = None
        for sub in self.subagents:
            if sub.name == subagent_name:
                subagent = sub
                break
                
        if not subagent:
            self.add_system_message(
                importance=5, 
                message=f"Subagent '{subagent_name}' not found. Available: {', '.join(self.list_subagents())}"
            )
            return
        
        # Create a unique ID for this task
        task_id = f"task_{len(self.pending_tasks) + len(self.handoff_results) + 1}"
        
        # Immediate confirmation message
        self.add_system_message(
            importance=8,
            message=f"Task delegated to {subagent_name}: \"{prompt[:50]}...\""
        )
        
        # Create the task but DO NOT await it
        task = asyncio.create_task(self._execute_handoff(task_id, subagent, prompt))
        
        # Store the task for later checking
        self.pending_tasks[task_id] = {
            "task": task,
            "subagent": subagent_name,
            "prompt": prompt
        }

    async def _execute_handoff(self, task_id: str, subagent: FlowAgent, prompt: str) -> None:
        """Execute the handoff and store the result"""
        try:
            # Run the subagent with the prompt
            result = await subagent.run(ImportanceRequest(importance=10, message=prompt))
            
            # Store the successful result
            self.handoff_results[task_id] = {
                "subagent": subagent.name,
                "result": result.message,
                "status": "completed"
            }
        except Exception as e:
            # Store the error
            self.handoff_results[task_id] = {
                "subagent": subagent.name,
                "result": f"Error: {str(e)}",
                "status": "failed"
            }
        finally:
            # Remove from pending tasks
            if task_id in self.pending_tasks:
                del self.pending_tasks[task_id]

    def _check_completed_tasks(self) -> None:
        """Check for completed tasks and deliver results"""
        # First report on any pending tasks
        if self.pending_tasks:
            pending_msg = "Currently processing:\n"
            for info in self.pending_tasks.values():
                pending_msg += f"- Task for {info['subagent']}: \"{info['prompt'][:30]}...\"\n"
            self.add_system_message(importance=3, message=pending_msg)
        
        # Then deliver any completed results
        for task_id, info in list(self.handoff_results.items()):
            if info["status"] == "completed":
                # Add as developer message for visibility
                self.add_developer_message(
                    message=f"Response from {info['subagent']}:\n{info['result']}"
                )
            else:
                # Add error as system message
                self.add_system_message(
                    importance=10,
                    message=f"Task for {info['subagent']} failed: {info['result']}"
                )
                
            # Remove the delivered result
            del self.handoff_results[task_id]

    def _extract_handoffs(self, message: str) -> tuple[str, List[Dict[str, str]]]:
        """Extract handoff JSON objects from the message"""
        handoffs = []
        positions = []
        
        # Find potential JSON objects with handoff format
        i = 0
        while i < len(message):
            if message[i:i+10].find('{"handoff"') != -1:
                # Found potential start of handoff JSON
                start = message.find('{"handoff"', i)
                if start == -1:
                    break
                
                # Try to find valid JSON from this position
                brace_count = 0
                found_valid = False
                for j in range(start, len(message)):
                    if message[j] == '{':
                        brace_count += 1
                    elif message[j] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            # Found complete JSON object
                            json_str = message[start:j+1]
                            try:
                                data = json.loads(json_str)
                                if "handoff" in data and isinstance(data["handoff"], dict):
                                    handoffs.append(data["handoff"])
                                    positions.append((start, j+1))
                                    found_valid = True
                            except json.JSONDecodeError:
                                pass
                            break
                
                i = j + 1 if found_valid else start + 1
            else:
                i += 1
        
        # Remove handoff JSON objects from the message
        if positions:
            cleaned_message = ""
            last_end = 0
            
            for start, end in sorted(positions):
                cleaned_message += message[last_end:start]
                last_end = end
                
            cleaned_message += message[last_end:]
            
            # Clean up excessive whitespace
            cleaned_message = re.sub(r'\s+', ' ', cleaned_message.strip())
        else:
            cleaned_message = message
            
        return cleaned_message, handoffs

    def list_subagents(self) -> List[str]:
        """List all available subagent names"""
        return [sub.name for sub in self.subagents]
