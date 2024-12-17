from fastapi import FastAPI, UploadFile, File, HTTPException
import whisper
import openai
import os
import uuid
import aiofiles

app = FastAPI()

# 初始化 Whisper 模型
try:
    whisper_model = whisper.load_model("base")
    print("Whisper model loaded successfully.")
except Exception as e:
    print(f"Error loading Whisper model: {e}")
    raise RuntimeError("Failed to load Whisper model.")

# 設置 OpenAI API Key
openai.api_key = ""  # 使用你的有效 OpenAI API Key

# 輸出目錄
output_dir = "outputs"
os.makedirs(output_dir, exist_ok=True)

@app.post("/process/audio")
async def process_audio(file: UploadFile = File(...)):

    try:
         # 獨立的文件名，避免並發冲突
        unique_id = uuid.uuid4()
        file_path = os.path.join(output_dir, f"{unique_id}_{file.filename}")

        # 保存上傳的文件到本地
        file_path = os.path.join(output_dir, f"{uuid.uuid4()}_{file.filename}")
        #with open(file_path, "wb") as f:
        #    f.write(await file.read())
        #print(f"File saved to: {file_path}")
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)
        print(f"File saved: {file_path}")

        # 使用 Whisper 進行轉錄
        print("Starting transcription with Whisper...")
        result = whisper_model.transcribe(file_path)
        transcript = result.get("text", "No transcription available")
        if not transcript.strip():
            raise ValueError("Transcription result is empty.")

        # 限制摘要輸入長度，避免超出 GPT 模型限制
        max_input_length = 3000
        if len(transcript) > max_input_length:
            transcript = transcript[:max_input_length] + "..."

        # 使用 OpenAI GPT 進行摘要
        print("Starting summarization with OpenAI GPT...")
        response = await loop.run_in_executor(
            None,
            lambda: openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Summarize the following text:\n{transcript}"}
                ],
                max_tokens=100  # 調整 max_tokens 控制摘要長度
            )
        )
        summary = response["choices"][0]["message"]["content"]
        print("Summarization completed successfully.")

        # 返回轉錄和摘要結果
        return {"transcript": transcript, "summary": summary}

    except openai.error.InvalidRequestError as e:
        print(f"OpenAI API error: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"OpenAI API error: {str(e)}"
        )
    except ValueError as ve:
        print(f"Transcription error: {ve}")
        raise HTTPException(
            status_code=400,
            detail=f"Transcription error: {str(ve)}"
        )
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing audio: {str(e)}"
        )