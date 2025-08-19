from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import os

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 1932862650
WEBAPP_URL = "https://твой-сервис.onrender.com"  # сюда Render выдаст ссылку

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# 📦 обработчик запроса ключей (оставляем твой прошлый функционал)
@dp.message_handler(lambda m: m.text.isdigit())
async def give_keys(message: types.Message):
    count = int(message.text)
    try:
        with open("keys.txt", "r", encoding="utf-8") as f:
            keys = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        keys = []

    if count <= 0:
        return await message.answer("❌ Неверное количество")

    if len(keys) < count:
        return await message.answer("❌ Недостаточно товара на складе")

    # выдаём ключи
    to_send = keys[:count]
    keys = keys[count:]

    with open("keys.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(keys))

    await message.answer("\n".join(to_send))
    await message.answer(f"📦 Остаток на складе: {len(keys)}")

# 🔑 команда для открытия панели (только для админа)
@dp.message_handler(commands=["panel"])
async def open_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ У вас нет доступа к панели")

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton(
        text="Открыть панель",
        web_app=types.WebAppInfo(url=WEBAPP_URL)
    )
    keyboard.add(button)
    await message.answer("Открой панель управления 👇", reply_markup=keyboard)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
