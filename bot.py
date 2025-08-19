# bot.py
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("Env var BOT_TOKEN is not set")

def norm(url: str) -> str:
    return url if url.endswith("/") else url + "/"

BASE = norm(os.getenv("PANEL_URL") or os.getenv("RENDER_EXTERNAL_URL") or "http://localhost:8000/")
WEBAPP_URL = BASE + "twa"   # <<< открываем специальный путь

KEYS_FILE = "keys.txt"

# ---- storage helpers ----
def load_keys():
    try:
        with open(KEYS_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def save_keys(keys):
    with open(KEYS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(keys) + ("\n" if keys else ""))

def pop_keys(n: int):
    keys = load_keys()
    take = min(n, len(keys))
    out = keys[:take]
    rest = keys[take:]
    save_keys(rest)
    return out, len(keys)

# ---- bot ----
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'panel'])
async def start(message: types.Message):
    await send_webapp_button(message)

async def send_webapp_button(message: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    kb.add(types.KeyboardButton(text="Открыть панель", web_app=types.WebAppInfo(url=WEBAPP_URL)))
    try:
        await message.answer("\u200E", reply_markup=kb)  # непустой текст
    except Exception:
        await message.answer(".", reply_markup=kb)

# Пополнение: !k1/k2/k3
@dp.message_handler(lambda m: m.text and m.text.startswith("!"))
async def add_keys(message: types.Message):
    raw = message.text[1:]
    parts = [p.strip() for p in raw.replace("\n", "/").split("/") if p.strip()]
    if not parts:
        return await message.answer("⚠️ Не найдено ключей.")
    existing = load_keys()
    added = 0
    for key in parts:
        if key not in existing:
            existing.append(key)
            added += 1
    save_keys(existing)
    await message.answer(f"✅ Добавлено: {added}. Всего на складе: {len(existing)}.")

# Выдача по числу N
@dp.message_handler(lambda m: m.text and m.text.isdigit())
async def give_keys(message: types.Message):
    n = int(message.text)
    if n <= 0:
        return await message.answer("Введите положительное число.")
    taken, total_before = pop_keys(n)
    if not taken:
        return await message.answer("😕 Ключей нет в наличии.")
    total_after = total_before - len(taken)
    text = "Ваши ключи:\n" + "\n".join(taken) + f"\n\nОстаток на складе: {total_after}"
    await message.answer(text)

# Проверка остатка
@dp.message_handler(commands=['stock'])
async def stock(message: types.Message):
    keys = load_keys()
    total = len(keys)
    if total == 0:
        return await message.answer("📦 Склад пуст.")
    preview = "\n".join(keys[:10])
    more = f"\n...и ещё {total-10}" if total > 10 else ""
    await message.answer(f"📦 На складе {total} ключей.\n\nПримеры:\n{preview}{more}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
