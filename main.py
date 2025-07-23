from dotenv import load_dotenv
import os

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    groq,
    noise_cancellation,
    silero,
)
from livekit.agents import stt
from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION

load_dotenv()

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=AGENT_INSTRUCTION)


async def entrypoint(ctx: agents.JobContext):
    llm = groq.LLM(
        model="llama3-70b-8192",
        api_key=os.getenv("GROQ_API_KEY"),
    )
    
    tts = groq.TTS(
        model="playai-tts",
        voice="Arista-PlayAI",
    )
    stt = groq.STT(
        model="whisper-large-v3-turbo",
        language="en",
    )
    
    session = AgentSession(
        llm=llm,
        tts=tts,
        stt= stt
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
            video_enabled=True,
        ),
    )

    await session.generate_reply(
        instructions=SESSION_INSTRUCTION
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))