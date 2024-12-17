from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from services.audio_service import process_audio_file
from config import OUTPUT_DIR
import uuid
import aiofiles
import os

router = APIRouter()

@router.post("/process/audio")
async def process_audio(file: UploadFile = File(...), language: str = Form(None)):
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
