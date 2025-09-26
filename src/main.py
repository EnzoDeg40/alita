import asyncio

from llm.llm import stream_completion

if __name__ == "__main__":
    asyncio.run(stream_completion("On joue a outer wilds ?"))
