from fastapi import FastAPI, UploadFile, File, HTTPException
import whisper
import openai
import os
import uuid

app = FastAPI()

# 初始化 Whisper 模型
whisper_model = whisper.load_model("base")

# 設置 OpenAI API Key
openai.api_key = "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"

# 輸出目錄
output_dir = "outputs"
os.makedirs(output_dir, exist_ok=True)


@app.post("/process/audio")
async def process_audio(file: UploadFile = File(...)):

    allowed_types = ["audio/wav", "audio/mpeg"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}. Allowed types are: {allowed_types}")
    try:
        # 保存上傳的文件到本地
        file_path = os.path.join(output_dir, f"{uuid.uuid4()}_{file.filename}")
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # 使用 Whisper 進行轉錄
        print("Starting transcription...")
        result = whisper_model.transcribe(file_path)
        transcript = result.get("text", "No transcription available")

        # 使用 OpenAI GPT 進行摘要
        openai.api_key = "your_openai_api_key"
        print("Starting summarization...")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Summarize the following text:\n{transcript}"}
            ],
            max_tokens=100
        )
        summary = response["choices"][0]["message"]["content"]

        # 返回轉錄和摘要結果
        return {"transcript": transcript, "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")