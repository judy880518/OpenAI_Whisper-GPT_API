import wave
from fastapi.responses import JSONResponse

async def handle_realtime_transcription(websocket, meeting_id, output_dir):
    filepath = f"{output_dir}/{meeting_id}.wav"
    meetings = {}

    meetings[meeting_id] = wave.open(filepath, 'wb')
    meetings[meeting_id].setnchannels(1)
    meetings[meeting_id].setsampwidth(2)
    meetings[meeting_id].setframerate(16000)

    transcript = ""

    try:
        while True:
            data = await websocket.receive_bytes()
            meetings[meeting_id].writeframes(data)

            partial_transcription = whisper_model.transcribe(data)
            partial_text = partial_transcription.get("text", "")

            if partial_text:
                transcript += partial_text
                await websocket.send_text(f"Partial Transcription: {partial_text}")

    except WebSocketDisconnect:
        meetings[meeting_id].close()

        async with aiofiles.open(filepath, "w") as f:
            await f.write(transcript)
