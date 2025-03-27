from typing import List, Dict, Any, Tuple
import json
import re
import asyncio

from .flow_agent import FlowAgent
from .conversation_flow.importance_message import ImportanceRequest, ImportanceResponse

class HandoffManager:
    def __init__(self, parent_agent: FlowAgent, subagents: List[FlowAgent]):
        self.parent_agent = parent_agent
        self.subagents = subagents
        self.pending_tasks: Dict[str, Dict[str, Any]] = {}
        self.handoff_results: Dict[str, Dict[str, Any]] = {}

    def extract_handoffs(self, message: str) -> Tuple[str, List[Dict[str, str]]]:
        handoffs = []
        positions = []
        i = 0
        while i < len(message):
            possible_start = message[i:i+10].find('{"handoff"')
            if possible_start != -1:
                start = message.find('{"handoff"', i)
                if start == -1:
                    break

                brace_count = 0
                found_valid = False
                for j in range(start, len(message)):
                    if message[j] == '{':
                        brace_count += 1
                    elif message[j] == '}':
                        brace_count -= 1
                        if brace_count == 0:
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

        if positions:
            cleaned_message = ""
            last_end = 0
            for start, end in sorted(positions):
                cleaned_message += message[last_end:start]
                last_end = end
            cleaned_message += message[last_end:]
            cleaned_message = re.sub(r'\s+', ' ', cleaned_message.strip())
        else:
            cleaned_message = message

        return cleaned_message, handoffs

    async def execute_handoff(self, task_id: str, subagent: FlowAgent, prompt: str) -> None:
        try:
            result = await subagent.run(ImportanceRequest(importance=10, message=prompt))
            self.handoff_results[task_id] = {
                "subagent": subagent.name,
                "result": result.message,
                "status": "completed"
            }
        except Exception as e:
            self.handoff_results[task_id] = {
                "subagent": subagent.name,
                "result": f"Error: {str(e)}",
                "status": "failed"
            }
        finally:
            if task_id in self.pending_tasks:
                del self.pending_tasks[task_id]

    def start_handoff(self, handoff: Dict[str, str]) -> None:
        subagent_name = handoff.get("subagent")
        prompt = handoff.get("prompt")

        if not subagent_name or not prompt:
            self.parent_agent.add_system_message(
                importance=5, 
                message="Invalid handoff format; missing 'subagent' or 'prompt'."
            )
            return

        subagent = None
        for s in self.subagents:
            if s.name == subagent_name:
                subagent = s
                break

        if not subagent:
            self.parent_agent.add_system_message(
                importance=5,
                message=(
                    f"Subagent '{subagent_name}' not found. "
                    f"Available: {', '.join(self.list_subagents())}"
                )
            )
            return

        task_id = f"task_{len(self.pending_tasks) + len(self.handoff_results) + 1}"
        self.parent_agent.add_system_message(
            importance=2,
            message=f"Task successfully delegated to {subagent_name}: \"{prompt[:50]}...\""
        )
        
        task = asyncio.create_task(
            self.execute_handoff(task_id, subagent, prompt)
        )

        self.pending_tasks[task_id] = {
            "task": task,
            "subagent": subagent_name,
            "prompt": prompt
        }

    def check_completed_tasks(self) -> None:
        if self.pending_tasks:
            pending_msg = "Currently processing:\n"
            for info in self.pending_tasks.values():
                pending_msg += f"- Task for {info['subagent']}: \"{info['prompt'][:30]}...\"\n"
            self.parent_agent.add_system_message(importance=1, message=pending_msg)

        for task_id, info in list(self.handoff_results.items()):
            if info["status"] == "completed":
                self.parent_agent.add_developer_message(
                    message=f"Response from {info['subagent']}:\n{info['result']}"
                )
            else:
                self.parent_agent.add_system_message(
                    importance=5,
                    message=(
                        f"Task for {info['subagent']} failed: {info['result']}"
                    )
                )
            del self.handoff_results[task_id]

    def list_subagents(self) -> List[str]:
        return [s.name for s in self.subagents]