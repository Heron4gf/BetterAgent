## Project Structure Overview

The project is organized into several key components, each serving specific roles:

### Main Project Directories
- **AgentsKnowledge**: Contains knowledge files and Python scripts relevant to agent functionality.
- **Debugger**: Contains debugging tools, including GUI components.
- **FlowAgents**: Manages different types of agents and their workflows.
- **IOMethods**: Handles input and output methods for agent interaction.
- **ToolsLoader**: Loads various tools that agents can use.

### Configuration Files
- **agents.yml**: Defines agents and their configurations, detailing inputs, outputs, capabilities, and subagents.
- **full_agent.py**: Contains the `FullAgent` class that manages interaction and orchestration for agents within the system.
- **load_config_agent.py**: Loads agent configurations from YAML files and manages relationships between agents.
- **main.py**: Entry point for the application, where agents are initialized and interactions are managed.

### Additional Files
- **.gitignore**: Specifies files and directories to be ignored by Git.
- **requirements.txt**: Lists Python package dependencies required for the project.

## Content Overview

### 2. **`agents.yml`**
   - This YAML file defines agent behaviors, interaction methods, knowledge, tools, and relationships among agents. For example:
     - **main_agent**: A handoff agent with subagents like `researcher_agent`, `project_documenter`, and `coder`.

### 3. **`full_agent.py`**
   - Defines the `FullAgent` class and its methods for managing interactions and responses based on input type.

### 4. **`load_config_agent.py`**
   - Responsible for loading agent configurations from `agents.yml` and creating instances of `FlowAgent` and `FullAgent`.

### 5. **`main.py`**
   - The main execution file where the application workflow is initiated. It loads agents and manages their interactions.

### 6. **`requirements.txt`**
   - Lists necessary dependencies for the project, such as `openai`, `pydantic`, and environment variable handling with `python-dotenv`.

### 7. **`__init__.py`**
   - Initializes the package and might include shared state or common functionality across modules.

## Example Subagent Configuration from `agents.yml`
```yaml
researcher_agent:
  model: gpt-4o
  system_prompt: You are a professional researcher that can help with the project
  description: "A professional researcher that can help with the project"
  knowledge:
    - "research_mastery"
  tools:
    - BROWSER_USE
```

This structured approach allows for a modular design where different components can be developed, tested, and maintained independently.