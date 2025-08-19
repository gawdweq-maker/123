# bot.py
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

logging.basicConfig(level=logging.INFO)

# === ENV ===
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("Env var BOT_TOKEN is not set")

# URL панели (Render / локально)
BASE_WEBAPP_URL = os.getenv("PANEL_URL") or os.getenv("RENDER_EXTERNAL_URL") or "http://localhost:8000/"

# Разрешённый админ ID
ADMIN_ID = 1932862650

# Финальный URL с uid для проверки на сервере
WEBAPP_URL = f"{BASE_WEBAPP_URL}?uid={ADMIN_ID}"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ У вас нет доступа к панели")
    await send_webapp_button(message)


@dp.message_handler(commands=['panel'])
async def open_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ У вас нет доступа к панели")
    await send_webapp_button(message)


@dp.message_handler(lambda m: m.text and m.text.startswith("!"))
async def add_keys(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    raw = message.text[1:]  # убираем "!"
    parts = [p.strip() for p in raw.replace("\n", "/").split("/") if p.strip()]

    if not parts:
        return await message.answer("⚠️ Не удалось найти ключи в сообщении.")

    existing = load_keys()
    added = []
    for key in parts:
        if key not in existing:
            added.append(key)
            existing.append(key)

    save_keys(existing)

    if added:
        await message.answer(f"✅ Добавлено {len(added)} новых ключей.")
    else:
        await message.answer("ℹ️ Все эти ключи уже есть в базе.")


# ===== работа с keys.txt =====
KEYS_FILE = "keys.txt"


def load_keys():
    try:
        with open(KEYS_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []


def save_keys(keys):
    with open(KEYS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(keys) + ("\n" if keys else ""))


# ===== WebApp кнопка =====
async def send_webapp_button(message: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    kb.add(
        types.KeyboardButton(
            text="Открыть панель",
            web_app=types.WebAppInfo(url=WEBAPP_URL)
        )
    )

    # Telegram требует НЕпустой текст → отправляем "." и удаляем
    msg = await message.answer(".", reply_markup=kb)
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
    except Exception:
        pass


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
