from dotenv import load_dotenv
import os

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    groq,
    noise_cancellation,
    silero,
    cartesia,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from tools import get_information_from_web

load_dotenv()

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=AGENT_INSTRUCTION,tools=[get_information_from_web])


async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()
    
    llm = groq.LLM(
        model="llama3-70b-8192",
        api_key=os.getenv("GROQ_API_KEY"),
    )
    
    tts=cartesia.TTS(
        model="sonic-2", 
        voice="f786b574-daa5-4673-aa0c-cbe3e8534c02"
    )
    
    stt = groq.STT(
        model="whisper-large-v3-turbo",
        language="en",
    )
    
    session = AgentSession(
        llm=llm,
        tts=tts,
        stt= stt,
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await session.generate_reply(
        instructions=SESSION_INSTRUCTION
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
