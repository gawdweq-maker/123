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

BASE_WEBAPP_URL = os.getenv("PANEL_URL") or os.getenv("RENDER_EXTERNAL_URL") or "http://localhost:8000/"
WEBAPP_URL = BASE_WEBAPP_URL  # без uid

# Файл склада
KEYS_FILE = "keys.txt"

# ===== helpers =====
def load_keys():
    try:
        with open(KEYS_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def save_keys(keys):
    with open(KEYS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(keys) + ("\n" if keys else ""))

def pop_keys(n):
    keys = load_keys()
    take = min(n, len(keys))
    out = keys[:take]
    rest = keys[take:]
    save_keys(rest)
    return out, len(keys)

# ===== bot =====
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await send_webapp_button(message)

@dp.message_handler(commands=['panel'])
async def open_panel(message: types.Message):
    await send_webapp_button(message)

async def send_webapp_button(message: types.Message):
    """
    Устойчивая web_app кнопка внизу чата (как на скрине).
    Сообщение не удаляем, чтобы кнопка не исчезала.
    """
    kb = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=False,
        selective=False,
        is_persistent=True
    )
    kb.add(types.KeyboardButton(
        text="Открыть панель",
        web_app=types.WebAppInfo(url=WEBAPP_URL)
    ))

    INVISIBLE = "\u200E"  # LRM
    try:
        await message.answer(INVISIBLE, reply_markup=kb)
    except Exception:
        await message.answer(".", reply_markup=kb)

# --- Пополнение склада: !k1/k2/k3 (доступно всем) ---
@dp.message_handler(lambda m: bool(m.text) and m.text.startswith("!"))
async def add_keys(message: types.Message):
    raw = message.text[1:]
    parts = [p.strip() for p in raw.replace("\n", "/").split("/") if p.strip()]
    if not parts:
        return await message.answer("⚠️ Не найдено ключей в сообщении.")
    existing = load_keys()
    added = 0
    for key in parts:
        if key not in existing:
            existing.append(key)
            added += 1
    save_keys(existing)
    await message.answer(f"✅ Добавлено: {added}. Всего на складе: {len(existing)}.")

# --- Выдача ключей по числу N (для всех) ---
@dp.message_handler(lambda m: bool(m.text) and m.text.isdigit())
async def give_keys(message: types.Message):
    n = int(message.text)
    if n <= 0:
        return await message.answer("Введите положительное число.")
    taken, total_before = pop_keys(n)
    if not taken:
        return await message.answer("😕 Ключей нет в наличии.")
    text = "Ваши ключи:\n" + "\n".join(taken)
    total_after = total_before - len(taken)
    await message.answer(f"{text}\n\nОстаток на складе: {total_after}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
