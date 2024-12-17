from openai import ChatCompletion
import whisper
from config import OPENAI_API_KEY
import aiofiles

whisper_model = whisper.load_model("base")

async def process_audio_file(file_path, language, unique_id):
    try:
        result = whisper_model.transcribe(file_path, language=language)
        transcript = result.get("text", "").strip()

        if not transcript:
            raise ValueError("No discernible content found in audio")

        max_input_length = 3000
        if len(transcript) > max_input_length:
            transcript = transcript[:max_input_length] + "..."

        # 使用 OpenAI 生成摘要
        response = ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Summarize the following transcription."},
                {"role": "user", "content": f"{transcript}"}
            ],
            max_tokens=100
        )

        summary = response["choices"][0]["message"]["content"]

        output_filename = f"{unique_id}_result.txt"
        output_filepath = f"{OUTPUT_DIR}/{output_filename}"

        async with aiofiles.open(output_filepath, "w") as f:
            await f.write("Transcription:\n")
            await f.write(transcript + "\n\n")
            await f.write("Summary:\n")
            await f.write(summary)

        return transcript, summary

    except Exception as e:
        return str(e), "Failed to process"