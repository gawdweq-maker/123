# bot.py
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("Env var BOT_TOKEN is not set")

KEYS_FILE = "keys.txt"


# ---------- storage ----------
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
    take = min(max(n, 0), len(keys))
    out = keys[:take]
    rest = keys[take:]
    save_keys(rest)
    return out


# ---------- bot ----------
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    # Никаких лишних сообщений — просто короткая подсказка один раз
    await message.answer("Отправь число — выдам столько ключей. Пополнение: !KEY1\\KEY2\\KEY3")


# Пополнение: !k1\k2\k3  (также поддерживаются / , перевод строки ,)
@dp.message_handler(lambda m: m.text and m.text.startswith("!"))
async def restock(message: types.Message):
    raw = message.text[1:]
    # поддержка разных разделителей: \ / , перенос строки
    for ch in ["\\", "/", ","]:
        raw = raw.replace(ch, "\n")
    parts = [p.strip() for p in raw.splitlines() if p.strip()]

    if not parts:
        return await message.answer("Не найдено ключей для добавления.")

    existing = load_keys()
    # без «умных» проверок — просто добавляем в конец (дубликаты допускаются)
    existing.extend(parts)
    save_keys(existing)

    await message.answer(f"Добавлено: {len(parts)}\nВсего на складе: {len(existing)}")


# Выдача по числу N (только одно сообщение с ключами)
@dp.message_handler(lambda m: m.text and m.text.isdigit())
async def give(message: types.Message):
    n = int(message.text)
    if n <= 0:
        return  # никаких сообщений

    issued = pop_keys(n)
    if not issued:
        return await message.answer("Ключей нет в наличии.")

    # Только сами ключи, по одному в строке
    await message.answer("\n".join(issued))


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
