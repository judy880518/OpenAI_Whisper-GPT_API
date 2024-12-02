# OpenAI_Whisper-GPT_API
簡單描述項目及其目的 (Briefly describe the project and its purpose):
該專案旨在提供一個簡單且高效的音訊處理工具，允許使用者上傳音訊文件，自動進行轉錄和總結，最終將結果顯示在前端介面。適用於多種場景，如會議記錄、訪談整理或多語言音訊處理。

架構 (Architecture)
系統組件 (Diagram or description of the system's components):

主要組件:
Gradio 前端: 提供使用者互動介面，用於音訊上傳和結果顯示。
FastAPI 後端: 提供 API 支持，包括音訊處理和資料傳輸。
Whisper 模型: 用於多語言音訊轉錄（由 OpenAI 提供）。
GPT API: 用於根據轉錄內容產生摘要或執行其他語言處理任務。

系統架構圖
+----------------+          +----------------+
| Gradio Frontend|          | FastAPI Backend|
| (frontend.py)  |          | (backend.py)   |
|                |          |                |
| 1. Upload File |          |                |
|     ------>    | HTTP POST|                |
|                |          | 2. Process     |
|                |          | Audio          |
|                |<---------|                |
| 3. Display     | HTTP Resp|                |
|    Results     |          |                |
+----------------+          +----------------+

工作流程 (Workflow)
端對端流程解釋 (Explain the end-to-end process):
音訊上傳: 使用者透過 Gradio 前端上傳音訊檔案（支援特定格式）。
轉錄處理: 後端透過 Whisper 模型對音訊檔案進行語音轉文字處理。
內容摘要: 使用 GPT API 對轉錄內容產生簡要總結。
結果展示: 將轉錄文字和摘要返回 Gradio 前端，並顯示給用戶。

設定說明:
1. 可使用Source tree clone 檔案下載到本地端。
2. Clone完成後使用Visual Studio Code 開啟專案資料夾。
3. 需要安裝使用的相關環境，資料夾裡有個requirements.txt的檔案，透過cmd 進到資料夾的路徑後須先安裝虛擬環境指令為 :python -m venv venv，並開啟虛擬環境 : .\venv\Scripts\activate，再安裝Requirements.txt內寫入有使用到的相關 指令為 : pip install -r requirements.txt
4. 下載後先需進入後端 打開 cmd 進到資料夾的路徑後，直接開啟虛擬環境(前面有安裝過就無需再安裝) .\venv\Scripts\activate，輸入指令 : uvicorn backend.main:app --host 127.0.0.1 --port 8000
   確認有出現下面這幾行 就算連線成功
   INFO:     Started server process [27616]
   INFO:     Waiting for application startup.
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
6. 再來回到前端資料夾有個 frontend.py 的檔案，打開後按右鍵，選 "Run Python" => "Run Python File in Terminal，執行後會跳出 Running on local URL:  http://127.0.0.1:7860 複製後就可以看到網頁了

API文件：
POST /upload 功能: 接收使用者上傳的音訊檔案並啟動轉錄流程。
請求格式:
{
  "file": "<audio_file>"
}

功能特點
多語言支援: Whisper 模型支援多語言語音轉錄。

未來改進 
模型優化: 整合更有效率的轉錄和摘要模型，提升效能和速度。
進階功能: 新增語音情緒分析和關鍵字擷取功能。
UI 改進: 提供更直覺的使用者介面設計，增加拖放上傳和進度條顯示功能。
雲端儲存整合: 新增雲端儲存選項，如 AWS S3 或 Google Cloud Storage，以支援更大的音訊檔案處理需求。

