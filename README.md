# Project Documentation for BetterAgents

## Table of Contents
1. [Overview](#overview)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Components](#components)
   - [Flow Agents](#flow-agents)
   - [Knowledge Management](#knowledge-management)
   - [I/O Methods](#io-methods)
   - [Debugging Tools](#debugging-tools)
6. [Usage](#usage)
7. [Contributing](#contributing)
8. [License](#license)

## Overview
BetterAgents is a modular open-source framework designed to facilitate the development and management of AI agents. Each agent can leverage a set of skills and tools appropriate for various tasks, making it adaptable for different projects.

## Installation
To get started, clone the repository and install required dependencies:

```bash
git clone https://github.com/Heron4gf/BetterAgent
cd BetterAgents
pip install -r requirements.txt
```

## Configuration
Configuration settings for agents are managed in the `agents.yml` file. This file specifies input/output methods, agents, and their sub-agents and tools.

Example configuration:
```yaml
input: USER_CLI
output: CONSOLE
agents:
  main_agent:
    model: gpt-4o-mini
    ...
```

## Components

### Flow Agents
Flow agents are responsible for managing a conversation and can delegate tasks to specialized sub-agents. Each agent can have its own system prompt, model, tools, and knowledge base.

### Knowledge Management
Knowledge files are managed in `AgentsKnowledge`. Each knowledge file can enhance an agent's capabilities depending on the specified tasks and objectives.

### I/O Methods
The framework supports various input/output methods, including console input and file-based methods, which allow flexibility in how agents receive and send messages.

### Debugging Tools
The `Debugger` module includes a graphical user interface (GUI) that facilitates the monitoring and testing of agents. This helps in verifying agent responses and behavior in real-time.

## Usage
To run the main agent, use the following command:

```bash
python main.py
```

Follow the prompts in the console to interact with the agent. The GUI will also become available to visualize debugging information about the agents' interactions.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes. Make sure to follow the contributing guidelines.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.