# bot.py
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import os

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 1932862650
# Лучше брать URL из переменной окружения, чтобы было удобно на Render
WEBAPP_URL = os.getenv("PANEL_URL", "https://your-service.onrender.com/")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    # сразу показываем кнопку открытия панели (без текста)
    await send_webapp_button(message)

@dp.message_handler(commands=['panel'])
async def open_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ У вас нет доступа к панели")
    await send_webapp_button(message)

async def send_webapp_button(message: types.Message):
    """
    Делает то самое поведение как на скрине:
    - Отправляем сервисное сообщение с ReplyKeyboard (web_app кнопка)
    - Сразу удаляем сообщение => в чате ничего не остаётся,
      а кнопка «Open» появляется в поле ввода рядом со скрепкой.
    """
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    btn = types.KeyboardButton(
        text="Открыть панель",  # текст на самой кнопке не критичен, в UI всё равно будет «Open»
        web_app=types.WebAppInfo(url=WEBAPP_URL)
    )
    kb.add(btn)

    msg = await message.answer(" ", reply_markup=kb)  # минимальный текст
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
    except Exception:
        # На всякий случай, если удаление не удалось — просто игнорим.
        pass

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
