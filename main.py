import asyncio
import uvicorn
from multiprocessing import Process
from bot import dp, bot
from aiogram.utils import executor
from admin import app

def start_bot():
    executor.start_polling(dp, skip_updates=True)

def start_admin():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    # запускаем оба процесса параллельно
    p1 = Process(target=start_bot)
    p2 = Process(target=start_admin)

    p1.start()
    p2.start()

    p1.join()
    p2.join()
