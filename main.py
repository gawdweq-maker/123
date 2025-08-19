# main.py
import os
import threading
import uvicorn

from admin import app
from bot import dp, executor

def run_api():
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

if __name__ == "__main__":
    # API фоном, чтобы Render видел health
    t = threading.Thread(target=run_api, daemon=True)
    t.start()

    # Бот в главном потоке — у aiogram будет event loop
    executor.start_polling(dp, skip_updates=True)
