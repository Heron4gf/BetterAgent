from load_config_agent import AgentsLoader
import asyncio
from Debugger.debugger_gui import create_debug_gui


async def main():
    agents_loader = AgentsLoader("agents.yml")
    agents = agents_loader.load_agents()


    gui = create_debug_gui(agents[0])

    while agents[0].input_method.has_next():
        await agents[0].next_interaction()
        gui.refresh()
    

if __name__ == "__main__":
    asyncio.run(main())
