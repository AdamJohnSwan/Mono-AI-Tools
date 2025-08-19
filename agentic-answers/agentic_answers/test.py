
import asyncio
from .agent_workflow import AgentWorkflow
from dotenv import load_dotenv


async def test():
    load_dotenv() 
    test_prompt = "Write me a story I will like"
    agent_workflow = AgentWorkflow(test_prompt)
    async for event in agent_workflow.run_workflow():
        print(event)

asyncio.run(test())