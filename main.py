from fastapi import FastAPI
from backend.routes.audio import router as audio_router
from backend.routes.realtime import router as realtime_router
#from backend import services as aud_service  #1227
from backend.config import OUTPUT_DIR
from backend.services.audio_service import process_audio_file   #1227
from backend.services.realtime_service import handle_realtime_transcription #1227
import os

app = FastAPI()

# 確保輸出目錄存在
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 註冊路由
app.include_router(audio_router)
app.include_router(realtime_router)

# 啟動應用程序
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)