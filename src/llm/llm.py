import asyncio
import time

import litellm

from audio import tts as tts_module
from llm import prompt as prompt_module


async def stream_completion(prompt):
    response = await litellm.acompletion(
        model="ollama/llama3.2:latest",
        messages=[
            {"role": "system", "content": prompt_module.system_prompt},
            {"role": "user", "content": prompt},
        ],
        stream=True,
    )

    buffer = ""
    async for chunk in response:
        delta = chunk["choices"][0].get("delta", {}).get("content", "")
        if delta:
            buffer += delta
            if buffer.endswith((".", "!", "?")):
                tts_module.synthesize_and_play(buffer.strip())
                buffer = ""
