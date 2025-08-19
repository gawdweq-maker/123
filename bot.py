import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# ВСТАВЬ СЮДА имя переменной окружения для токена
# На Render: добавь BOT_TOKEN в Environment Variables
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

KEYS_FILE = "keys.txt"

def load_keys():
    if not os.path.exists(KEYS_FILE):
        return []
    with open(KEYS_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def save_keys(keys):
    with open(KEYS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(keys))

@dp.message_handler()
async def send_keys(message: types.Message):
    try:
        amount = int(message.text.strip())
    except ValueError:
        return  # если не число — игнорируем

    keys = load_keys()

    if not keys:
        await message.answer("❌ Ключей больше нет!")
        return

    to_give = keys[:amount]   # выдаём N ключей
    keys = keys[amount:]      # удаляем их со склада
    save_keys(keys)

    await message.answer("\n".join(to_give))
    await message.answer(f"📦 Осталось на складе: {len(keys)}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
