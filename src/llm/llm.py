import asyncio
import time

import litellm

from audio import tts as tts_module
from llm import prompt as prompt_module

conversation_history = []


async def stream_completion(prompt):
    global conversation_history
    conversation_history.append({"role": "user", "content": prompt})
    if len(conversation_history) > 25:
        conversation_history = conversation_history[-25:]
    response = await litellm.acompletion(
        model="ollama/llama3.2:latest",
        messages=[
            {"role": "system", "content": prompt_module.system_prompt},
            *conversation_history,
        ],
        stream=True,
    )

    buffer = ""
    llm_message = ""
    async for chunk in response:
        delta = chunk["choices"][0].get("delta", {}).get("content", "")
        if delta:
            buffer += delta
            llm_message += delta
            if buffer.endswith((".", "!", "?")):
                tts_module.synthesize_and_play(buffer.strip())
                buffer = ""
    if llm_message:
        conversation_history.append(
            {"role": "assistant", "content": llm_message.strip()}
        )
