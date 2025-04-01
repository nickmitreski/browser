from langchain_openai import ChatOpenAI
from browser_use import Agent
import asyncio
from dotenv import load_dotenv
load_dotenv()

async def main():
    agent = Agent(
        task="Go to google.com and search for 'browser-use github'",
        llm=ChatOpenAI(model="gpt-4o"),
    )
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main()) 