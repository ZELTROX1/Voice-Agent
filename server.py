from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dataclasses import dataclass
from pydantic import BaseModel,Field,EmailStr
from typing import Optional
import uuid
from dotenv import load_dotenv
load_dotenv()

from livekit.api import ListRoomsRequest,LiveKitAPI,AccessToken
from livekit import api
import os


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@dataclass
class TockenRequest(BaseModel):
    name:str = Field(...,description="userid for the room token")
    room_id:Optional[str] = Field(...,description="room_id if avalable")
    email:EmailStr = Field(...,description="Email of the user")
    number:Optional[str] = Field(None,description="Phone number of the user")

@app.post("/getToken")
async def get_tocken(request:TockenRequest):
    name = request.name
    room_id = request.room_id if request.room_id else None
    if not room_id:
        room_id = await generate_room_name()
    token = api.AccessToken(os.getenv('LIVEKIT_API_KEY'), os.getenv('LIVEKIT_API_SECRET')) \
        .with_identity(name) \
        .with_name(name) \
        .with_metadata({"user_id":name,"email":request.email,"number":request.number}) \
        .with_grants(api.VideoGrants(
            room_join=True,
            room="my-room",
    ))
    return token.to_jwt()


async def generate_room_name():
    name = "room-"+str(uuid.uuid4())[:8]
    rooms = await get_rooms()
    while name in rooms:
        name = "room-"+str(uuid.uuid4())[:8]
    return name


async def get_rooms():
    lkapi = LiveKitAPI()
    rooms = await lkapi.room.list_rooms(ListRoomsRequest())
    await lkapi.aclose()
    return [room.name for room in rooms]