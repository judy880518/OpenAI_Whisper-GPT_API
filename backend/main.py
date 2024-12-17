from fastapi import FastAPI, UploadFile, File, HTTPException, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
import whisper
import openai
import os
import uuid
import aiofiles
import wave
import asyncio

app = FastAPI()

# 初始化 Whisper 模型
try:
    whisper_model = whisper.load_model("base")
    print("Whisper model loaded successfully.")
except Exception as e:
    print(f"Error loading Whisper model: {e}")
    raise RuntimeError("Failed to load Whisper model.")

# 設置 OpenAI API Key
openai.api_key = ""  # 在此填入你的 OpenAI API Key

# 輸出目錄
output_dir = "outputs"
os.makedirs(output_dir, exist_ok=True)

# 暫存會議錄音文件和即時轉錄結果
meetings = {}

@app.websocket("/realtime/meeting/{meeting_id}")
async def realtime_meeting(websocket: WebSocket, meeting_id: str):
    """
    接收即時語音流，並進行邊錄製邊處理。
    """
    await websocket.accept()
    meeting_file_path = os.path.join(output_dir, f"{meeting_id}.wav")
    meetings[meeting_id] = wave.open(meeting_file_path, 'wb')
    meetings[meeting_id].setnchannels(1)  # 單聲道
    meetings[meeting_id].setsampwidth(2)  # 每個樣本 2 字節 (16 位)
    meetings[meeting_id].setframerate(16000)  # 16 kHz 頻率

    transcript = ""  # 累積轉錄內容
    try:
        while True:
            data = await websocket.receive_bytes()
            meetings[meeting_id].writeframes(data)

            # 即時轉錄
            partial_transcription = whisper_model.transcribe(data, fp16=False)
            partial_text = partial_transcription.get("text", "").strip()
            if partial_text:
                transcript += partial_text
                await websocket.send_text(f"Partial Transcription: {partial_text}")
    except WebSocketDisconnect:
        print(f"Meeting {meeting_id} ended.")
        meetings[meeting_id].close()
        del meetings[meeting_id]

        # 保存最終轉錄內容
        result_filename = os.path.join(output_dir, f"{meeting_id}_transcript.txt")
        async with aiofiles.open(result_filename, "w") as f:
            await f.write(transcript)
        print(f"Final transcription saved for meeting {meeting_id}.")

@app.post("/process/audio")
async def process_audio(file: UploadFile = File(...), language: str = Form(None)):
    """
    處理上傳的音訊文件，進行轉錄和摘要處理，並返回結果和下載鏈接。
    """
    try:
        # 生成唯一文件名以避免並發衝突
        unique_id = uuid.uuid4()
        file_path = os.path.join(output_dir, f"{unique_id}_{file.filename}")

        # 保存上傳的文件到本地
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)
        print(f"File saved: {file_path}")

        # 使用 Whisper 進行音訊轉錄
        print("Starting transcription with Whisper...")
        result = whisper_model.transcribe(file_path, language=language)
        transcript = result.get("text", "").strip()

        # 檢測空白音訊或無有效內容
        if not transcript:
            raise ValueError("The uploaded audio contains no discernible content or is silent.")

        # 限制摘要的輸入長度
        max_input_length = 3000
        if len(transcript) > max_input_length:
            transcript = transcript[:max_input_length] + "..."

        # 使用 OpenAI GPT 模型進行摘要
        print("Starting summarization with OpenAI GPT...")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a helpful assistant for {language or 'multi-language'} transcription."},
                {"role": "user", "content": f"Summarize the following text:\n{transcript}"}
            ],
            max_tokens=100  # 控制摘要的長度
        )
        summary = response["choices"][0]["message"]["content"]
        print("Summarization completed successfully.")

        # 將轉錄結果和摘要寫入文件
        output_filename = os.path.join(output_dir, f"{unique_id}_result.txt")
        async with aiofiles.open(output_filename, "w") as f:
            await f.write("Transcription:\n")
            await f.write(transcript + "\n\n")
            await f.write("Summary:\n")
            await f.write(summary)

        # 返回 JSON 結果和文件下載鏈接
        return JSONResponse(
            content={
                "transcript": transcript,
                "summary": summary,
                "download_url": f"/download/{unique_id}_result.txt"
            }
        )

    except openai.error.InvalidRequestError as e:
        print(f"OpenAI API error: {e}")
        raise HTTPException(status_code=400, detail=f"OpenAI API error: {str(e)}")

    except ValueError as ve:
        print(f"Transcription error: {ve}")
        raise HTTPException(status_code=400, detail=f"Transcription error: {str(ve)}")

    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")


@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    提供生成的結果文件供下載。
    """
    file_path = os.path.join(output_dir, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(file_path, media_type="text/plain", filename=filename)