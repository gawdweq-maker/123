# --- ВЕРХ ФАЙЛА БЕЗ ИЗМЕНЕНИЙ ---

HTML = """
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Панель</title>
  <style>
    body { background:#0f172a; color:#e2e8f0; font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Cantarell, Noto Sans, Helvetica, Arial, Apple Color Emoji, Segoe UI Emoji; margin:0; padding:24px; }
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
    html = HTML.replace("{{items}}", items).replace("{{count}}", str(len(keys)))
    return html

@app.get("/health")
def health():
    return {"ok": True}

# полезно: HEAD /, чтобы в логах не было 405
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse

@app.head("/", response_class=PlainTextResponse)
def head_root():
    return PlainTextResponse("", status_code=200)

@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(render_index())

# ...остальные маршруты без изменений...

# CATCH-ALL
@app.get("/{path:path}", response_class=HTMLResponse)
def catch_all(path: str):
    return HTMLResponse(render_index())
