import gradio as gr
import requests

# 後端 API 地址
BACKEND_URL = "http://127.0.0.1:8000/process/audio"

# 音頻處理函數
def process_audio(file_path):
    if file_path is None or not file_path.strip():
        return "No transcript available", "No summary available"

    try:
        # 發送音訊文件到後端
        with open(file_path, "rb") as audio_file:
            response = requests.post(
                BACKEND_URL,
                files={"file": audio_file}
            )
        
        # 處理後端返回的結果
        if response.status_code == 200:
            result = response.json()
            if "error" in result:
                return "Error during processing", result["error"]
            return result["transcript"], result["summary"]
        else:
            return "Failed to process audio", f"Status Code: {response.status_code}"
    except Exception as e:
        return "An error occurred", str(e)

# Gradio 前端介面
with gr.Blocks() as demo:
    gr.Markdown("## Audio Transcription and Summarization")
    
    with gr.Row():
        upload_button = gr.File(label="Upload Audio File", type="filepath")  # 設置為 `filepath`
    
    with gr.Row():
        transcription_box = gr.Textbox(label="Transcription", lines=10)
        summary_box = gr.Textbox(label="Summary", lines=10)

    # 上傳並處理音訊
    upload_button.change(process_audio, inputs=upload_button, outputs=[transcription_box, summary_box])

demo.launch(server_name="127.0.0.1", server_port=7860, share=True)