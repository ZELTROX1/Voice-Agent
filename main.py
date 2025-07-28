from dotenv import load_dotenv
import os
import json
import logging

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    groq,
    noise_cancellation,
    silero,
    cartesia,
    azure,
    deepgram
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from prompts import AGENT_INSTRUCTION, get_session_instruction
from tools import (
    get_all_products,
    get_user_wishlist,
    get_product_recommendations,
    submit_product_feedback,
    create_product_order,
    get_user_info
)
from livekit.plugins import elevenlabs
from livekit.plugins.elevenlabs import VoiceSettings

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class Assistant(Agent):
    def __init__(self,user_id:str) -> None:
        customer_instructions = f"The user ID is {user_id}.And the user informaiton is in session instructions"+AGENT_INSTRUCTION
        super().__init__(
            instructions=customer_instructions,
            tools=[
                get_all_products,
                get_user_wishlist,
                get_product_recommendations,
                submit_product_feedback,
                create_product_order,
                get_user_info
            ]
        )


async def get_participant_metadata(ctx: agents.JobContext) -> dict:
    default_metadata = {
        'user_id': 'new_user_001'
    }
    
    try:
        participants = list(ctx.room.remote_participants.values())
        if not participants:
            logger.info("No remote participants found, using default metadata")
            return default_metadata
            
        participant = participants[0]
        logger.info(f"Processing participant: {participant.identity}")
        
        # Check if metadata exists and is valid
        if not hasattr(participant, 'metadata') or not participant.metadata:
            logger.info("No metadata found, using defaults")
            return default_metadata
            
        metadata_raw = participant.metadata
        
        # Type check - ensure it's a string
        if not isinstance(metadata_raw, str):
            logger.warning(f"Metadata is not a string, got {type(metadata_raw)}")
            return default_metadata
            
        # Parse JSON
        parsed_metadata = json.loads(metadata_raw)
        logger.info(f"Successfully parsed metadata: {parsed_metadata}")
        
        # Merge with defaults to ensure all required fields exist
        final_metadata = {**default_metadata, **parsed_metadata}
        return final_metadata
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse metadata JSON: {e}")
        return default_metadata
    except Exception as e:
        logger.error(f"Error extracting metadata: {e}")
        return default_metadata


async def create_llm_session(user_id: str):
    try:
        llm = groq.LLM(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            api_key=os.getenv("GROQ_API_KEY"),
        )
        
        # tts = cartesia.TTS(
        #     model="sonic-2", 
        #     voice="95d51f79-c397-46f9-b49a-23763d3eaa2d",
        #     speed=1.0,
        # )
        # tts = elevenlabs.TTS(
        #     voice_id="ODq5zmih8GrVes37Dizd",
        #     model="eleven_multilingual_v2",
        #     voice_settings=VoiceSettings(
        #         stability=0.3,
        #         similarity_boost=0.75,
        #         style=0.0,
        #         use_speaker_boost=True,
        #         speed=1.0,
        #     )
        # )
        
        tts=azure.TTS(
        speech_key=os.getenv("AZURE_SPEECH_KEY"),
        speech_region=os.getenv("AZURE_SPEECH_REGION"),
        voice="hi-IN-AnanyaNeural",
        language="hi-IN",
        )

        # Initialize STT
        # stt = groq.STT(
        #     model="whisper-large-v3-turbo",
        #     language="en",
        # )
        stt=deepgram.STT(model="nova-3", language="multi")
        session = AgentSession(
            llm=llm,
            tts=tts,
            stt=stt,
            vad=silero.VAD.load(),
            turn_detection=MultilingualModel(),
        )
        
        return session
        
    except Exception as e:
        logger.error(f"Failed to create LLM session: {e}")
        raise


async def entrypoint(ctx: agents.JobContext):
    try:
        logger.info("Agent starting...")
        await ctx.connect()
        logger.info("Connected to room successfully")
        
        metadata = await get_participant_metadata(ctx)
        user_id = metadata.get('user_id', 'new_user_001')
        
        logger.info(f"Agent configured for user_id: {user_id}")
        
        session = await create_llm_session(user_id)
        
        await session.start(
            room=ctx.room,
            agent=Assistant(user_id=user_id),
            room_input_options=RoomInputOptions(
                noise_cancellation=noise_cancellation.BVC(),
            ),
        )
        session_instruction = await get_session_instruction(user_id)
        logger.info(f"Session instruction: {session_instruction}")
        
        await session.generate_reply(instructions=session_instruction)
        
        logger.info("Agent session started successfully")
        
    except Exception as e:
        logger.error(f"Error in agent entrypoint: {e}")
        raise


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    required_env_vars = ['GROQ_API_KEY', 'LIVEKIT_API_KEY', 'LIVEKIT_API_SECRET', 'LIVEKIT_URL','AZURE_SPEECH_KEY']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        exit(1)
    
    logger.info("Starting LiveKit agent worker...")
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))