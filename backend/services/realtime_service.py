from fastapi.responses import JSONResponse
from fastapi import WebSocket, WebSocketDisconnect
import aiofiles
import whisper
import torch
import wave
from typing import Dict
import io
from pydub import AudioSegment
from io import BytesIO

# Load the Whisper model globally
whisper_model = whisper.load_model("base")

# Dictionary to track active meeting WAV files
meetings: Dict[str, wave.Wave_write] = {}

async def handle_realtime_transcription(websocket: WebSocket, meeting_id: str, output_dir: str):
    filepath = f"{output_dir}/{meeting_id}.wav"
    #buffer = bytes()  # Temporary buffer for audio data
    transcript = ""  # To store the transcription
    buffer = bytearray()  # Temporary buffer for audio data

    # Open the WAV file for writing
    try:
        #Initialize WAV file for writing
        meetings[meeting_id] = wave.open(filepath, 'wb')
        meetings[meeting_id].setnchannels(1)
        meetings[meeting_id].setsampwidth(2)  # Assuming 16-bit PCM
        meetings[meeting_id].setframerate(16000)

        while True:
            #Receive MP3 audio data from WebSocket
            data = await websocket.receive_bytes()
            buffer.extend(data)  # Append data to buffer

            # Decode the MP3 data into an AudioSegment
            audio = AudioSegment.from_mp3(BytesIO(data))

            # Convert to 16kHz, mono channel, 16-bit PCM
            audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

            # Extract the raw sample data and normalize it
            raw_samples = audio.get_array_of_samples()

            # Convert to float32 and normalize the samples manually
            audio_data = [sample / 32768.0 for sample in raw_samples]

            # Perform transcription using Whisper
            transcription_result = whisper_model.transcribe(audio_data, fp16=torch.cuda.is_available())
            partial_text = transcription_result.get("text", "")

            if partial_text:
                transcript += partial_text
                await websocket.send_text(f"Partial Transcription: {partial_text}")

    except WebSocketDisconnect:
        # Handle WebSocket disconnection
        await finalize_meeting(meeting_id, transcript, output_dir)
        return JSONResponse(content={"message": "WebSocket disconnected. Transcript saved."}, status_code=200)

    except Exception as e:
        # Handle unexpected exceptions
        await finalize_meeting(meeting_id, transcript, output_dir, error=str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
async def finalize_meeting(meeting_id: str, transcript: str, output_dir: str, error: str = None):
    """
   # Finalizes the meeting by closing the WAV file and saving the transcript.

    #Args:
     #   meeting_id (str): Unique identifier for the meeting.
      #  transcript (str): Transcribed text to save.
       # output_dir (str): Directory to save the transcript.
        #error (str, optional): Error message if an exception occurred.
    """
    if meeting_id in meetings:
        meetings[meeting_id].close()
        del meetings[meeting_id]  # Remove from active meetings

    transcript_filepath = f"{output_dir}/{meeting_id}_transcript.txt"
    async with aiofiles.open(transcript_filepath, "w") as f:
        await f.write(transcript)

    if error:
        print(f"Meeting {meeting_id} ended with error: {error}")
    else:
        print(f"Meeting {meeting_id} finalized successfully.")

