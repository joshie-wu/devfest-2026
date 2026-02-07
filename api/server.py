import asyncio
from dedalus_labs import AsyncDedalus, DedalusRunner
from dotenv import load_dotenv

load_dotenv()

async def main():
    client = AsyncDedalus()
    runner = DedalusRunner(client)

    response = await runner.run(
        input="Here is a list of regulations on the NYC website: https://nyc-business.nyc.gov/nycbusiness/index. Please summarize a list of regulations and certifications that would be important to an owner of a gym",
        model="anthropic/claude-opus-4-6",
    )

    print(response.final_output)

if __name__ == "__main__":
    asyncio.run(main())