# admin.py
import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse

app = FastAPI()

KEYS_FILE = "keys.txt"

# -------- storage helpers --------
def load_keys():
    try:
        with open(KEYS_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def save_keys(keys):
    with open(KEYS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(keys) + ("\n" if keys else ""))

# -------- template --------
HTML = """
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Панель</title>
  <style>
    body { background:#0f172a; color:#e2e8f0; font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Cantarell,Noto Sans,Helvetica,Arial; margin:0; padding:24px; }
    .wrap { max-width:820px; margin:0 auto; }
    h1 { font-size:22px; margin:0 0 16px; }
    .card { background:#111827; border:1px solid #1f2937; border-radius:14px; padding:16px; margin:12px 0; }
    input[type=text] { width:100%; padding:10px 12px; border-radius:10px; border:1px solid #374151; background:#0b1220; color:#e5e7eb; outline:none; }
    button { padding:10px 14px; border-radius:10px; border:0; background:#2563eb; color:#fff; cursor:pointer; }
    button.danger { background:#ef4444; }
    ul { list-style:none; padding-left:0; }
    li { display:flex; align-items:center; justify-content:space-between; padding:8px 0; border-bottom:1px solid #1f2937; }
    .muted { color:#9ca3af; font-size:13px; }
    a { color:#93c5fd; text-decoration:none; }
    .row { display:flex; gap:8px; }
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Панель управления</h1>

    <div class="card">
      <form method="post" action="/add">
        <div class="row">
          <input type="text" name="keys" placeholder="Вставь ключи через запятую или с новой строки" />
          <button type="submit">Добавить</button>
        </div>
        <p class="muted">Файл: <code>keys.txt</code></p>
      </form>
    </div>

    <div class="card">
      <h3>Список ключей</h3>
      <ul>
        {{items}}
      </ul>
      <p class="muted">Всего: {{count}}</p>
    </div>

    <div class="card">
      <a href="/health">/health</a>
    </div>
  </div>
</body>
</html>
"""

def render_index():
    keys = load_keys()
    items = "\n".join(
        f'<li><span>{k}</span><a href="/delete/{i}"><button class="danger">Удалить</button></a></li>'
        for i, k in enumerate(keys)
    ) or '<li class="muted">Пока пусто…</li>'
    return HTML.replace("{{items}}", items).replace("{{count}}", str(len(keys)))

# -------- routes --------
@app.get("/health")
def health():
    return {"ok": True}

# HEAD / — чтобы не было 405
@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
def index():
    return HTMLResponse(render_index())

@app.post("/add")
def add_keys(keys: str = Form(...)):
    existing = load_keys()
    for raw in keys.replace(",", "\n").splitlines():
        val = raw.strip()
        if val and val not in existing:
            existing.append(val)
    save_keys(existing)
    return RedirectResponse(url="/", status_code=303)

@app.get("/delete/{key_id}")
def delete_key(key_id: int):
    keys = load_keys()
    if 0 <= key_id < len(keys):
        keys.pop(key_id)
        save_keys(keys)
    return RedirectResponse(url="/", status_code=303)

# CATCH-ALL: любые пути → панель (и HEAD тоже)
@app.api_route("/{path:path}", methods=["GET", "HEAD"], response_class=HTMLResponse)
def catch_all(path: str):
    return HTMLResponse(render_index())

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
