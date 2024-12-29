from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi import FastAPI
#from services.audio_service import process_audio_file
from backend.services.audio_service import process_audio_file
from backend.config import OUTPUT_DIR
import uuid
import aiofiles
import os

router = APIRouter()
app = FastAPI()

@router.post("/process/audio", response_description="Process the uploaded audio file")
async def process_audio(file: UploadFile = File(...), language: str = Form(None)):
    """
    Process an uploaded audio file, generate transcription and summary.
    
    - **file**: The audio file to be processed (in MP3 or WAV format).
    - **language**: (Optional) The language of the audio file for transcription.
    
    Returns a transcript and a summary of the audio content.
    """
    try:
        unique_id = str(uuid.uuid4())
        file_path = os.path.join(OUTPUT_DIR, f"{unique_id}_{file.filename}")

        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)

        transcript, summary = await process_audio_file(file_path, language, unique_id)

        return JSONResponse(
            content={
                "transcript": transcript,
                "summary": summary,
                "download_url": f"/download/{unique_id}_result.txt"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")
