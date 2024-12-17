# backend/main.py
from fastapi import FastAPI
from routes.audio import router as audio_router
from routes.realtime import router as realtime_router
from config import OUTPUT_DIR
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