# main.py
import os
import threading
import uvicorn

from admin import app          # FastAPI
from bot import dp, executor   # aiogram

def run_bot():
    executor.start_polling(dp, skip_updates=True)

def run_api():
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)), log_level="info")

if __name__ == "__main__":
    t = threading.Thread(target=run_bot, daemon=True)
    t.start()
    run_api()
