# bot.py
import os
import logging
from typing import List, Tuple

import psycopg2
import psycopg2.extras

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("Env var BOT_TOKEN is not set")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("Env var DATABASE_URL is not set (e.g. postgres://user:pass@host:port/db)")

# --- DB helpers (простые и надёжные) ---

def get_conn():
    # Render обычно требует SSL
    return psycopg2.connect(DATABASE_URL, sslmode="require")

def init_db():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS keys_store (
                id BIGSERIAL PRIMARY KEY,
                value TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)
        conn.commit()

def insert_many(keys: List[str]) -> int:
    if not keys:
        return 0
    with get_conn() as conn, conn.cursor() as cur:
        psycopg2.extras.execute_values(
            cur,
            "INSERT INTO keys_store (value) VALUES %s",
            [(k,) for k in keys]
        )
        conn.commit()
        return len(keys)

def pop_n(n: int) -> List[str]:
    if n <= 0:
        return []
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Берём n самых старых строк атомарно и удаляем
            cur.execute("""
                WITH picked AS (
                    SELECT id, value
                    FROM keys_store
                    ORDER BY id ASC
                    FOR UPDATE SKIP LOCKED
                    LIMIT %s
                )
                DELETE FROM keys_store
                USING picked
                WHERE keys_store.id = picked.id
                RETURNING picked.value;
            """, (n,))
            rows = cur.fetchall()
        conn.commit()
    return [r[0] for r in rows]

def count_all() -> int:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM keys_store;")
        (cnt,) = cur.fetchone()
        return int(cnt)

# Инициализируем таблицу при импорте
init_db()

# --- BOT ---

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    # Короткая подсказка, без «умных» вещей
    await message.answer("Отправь число — выдам столько ключей.\nПополнение: !KEY1\\KEY2\\KEY3")

# Пополнение: !k1\k2\k3  (поддержка также / , и переносов)
@dp.message_handler(lambda m: m.text and m.text.startswith("!"))
async def restock(message: types.Message):
    raw = message.text[1:]
    for ch in ["\\", "/", ","]:
        raw = raw.replace(ch, "\n")
    parts = [p.strip() for p in raw.splitlines() if p.strip()]

    if not parts:
        return await message.answer("Не найдено ключей для добавления.")

    added = insert_many(parts)
    total = count_all()
    # Уведомления: после пополнения показать добавлено и общее количество
    await message.answer(f"Добавлено: {added}\nВсего на складе: {total}")

# Выдача по числу N — ответ ТОЛЬКО ключами (или сообщение о пустом складе)
@dp.message_handler(lambda m: m.text and m.text.isdigit())
async def give(message: types.Message):
    n = int(message.text)
    if n <= 0:
        return  # никаких сообщений

    issued = pop_n(n)
    if not issued:
        return await message.answer("Ключей нет в наличии.")

    # Только сами ключи, по одному в строке (никаких лишних сообщений)
    await message.answer("\n".join(issued))

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
