from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.realtime_service import handle_realtime_transcription
from config import OUTPUT_DIR
import os

router = APIRouter()

@router.websocket("/realtime/meeting/{meeting_id}")
async def realtime_meeting(websocket: WebSocket, meeting_id: str):
    await handle_realtime_transcription(websocket, meeting_id, OUTPUT_DIR)