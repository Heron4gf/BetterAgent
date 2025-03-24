from load_config_agent import AgentsLoader
import asyncio

async def main():
    agents_loader = AgentsLoader("agents.yml")
    full_agents = agents_loader.load_agents()
    await full_agents[0].start()
    

if __name__ == "__main__":
    asyncio.run(main())
