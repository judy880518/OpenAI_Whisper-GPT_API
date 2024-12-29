import gradio as gr
import requests
import os
import shutil

# 後端 API 基本地址
BASE_URL = "http://127.0.0.1:8000"

# 音頻處理函數，用於處理上傳的音頻檔案
def process_audio_file(file_path, save_directory="saved_audio"):
    """處理音頻檔案，發送至後端並返回轉錄與摘要結果。"""
    if not file_path or not file_path.strip():
        return "無法取得轉錄內容", "無法取得摘要內容"

    try:
        # 確保保存目錄存在
        os.makedirs(save_directory, exist_ok=True)

        # 將檔案複製到保存目錄，避免檔案被占用問題
        saved_path = os.path.join(save_directory, os.path.basename(file_path))
        shutil.copy(file_path, saved_path)
        print(f"音頻已保存至本地：{saved_path}")

        # 發送音頻檔案到後端 API
        endpoint = f"{BASE_URL}/process/audio"
        with open(saved_path, "rb") as audio_file:
            response = requests.post(
                endpoint,
                files={"file": audio_file}
            )

        # 處理後端返回的結果
        if response.status_code == 200:
            result = response.json()
            return result.get("transcript", "無法取得轉錄內容"), result.get("summary", "無法取得摘要內容")
        else:
            return f"錯誤：狀態碼 {response.status_code}", None
    except Exception as e:
        return f"發生錯誤：{e}", None

# Gradio 前端介面
with gr.Blocks() as demo:
    gr.Markdown("## 音頻轉錄與摘要")

    with gr.Tab("上傳或錄製音頻檔案"):
        audio_input = gr.Audio(type="filepath", label="上傳或錄製 MP3 檔案")
        transcription_box = gr.Textbox(label="轉錄結果", lines=10)
        summary_box = gr.Textbox(label="摘要", lines=10)
        audio_input.change(
            fn=process_audio_file,
            inputs=audio_input,
            outputs=[transcription_box, summary_box]
        )

# 啟動服務
demo.launch(server_name="127.0.0.1", server_port=7860, share=True)