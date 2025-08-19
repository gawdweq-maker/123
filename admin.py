import uvicorn
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse

KEYS_FILE = "keys.txt"

app = FastAPI()

def load_keys():
    try:
        with open(KEYS_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def save_keys(keys):
    with open(KEYS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(keys))

@app.get("/", response_class=HTMLResponse)
def index():
    keys = load_keys()
    html = "<h2>📦 Склад ключей</h2>"
    html += f"<p>Всего: {len(keys)} шт.</p><ul>"
    for i, key in enumerate(keys):
        html += f"<li>{key} <a href='/delete/{i}'>❌ удалить</a></li>"
    html += "</ul>"

    html += """
    <h3>➕ Добавить ключи</h3>
    <form method="post" action="/add">
        <textarea name="new_keys" rows="5" cols="40" placeholder="AAA111\nBBB222\nCCC333"></textarea><br>
        <button type="submit">Добавить</button>
    </form>
    """
    return html

@app.post("/add")
def add_keys(new_keys: str = Form(...)):
    keys = load_keys()
    added = [k.strip() for k in new_keys.splitlines() if k.strip()]
    keys.extend(added)
    save_keys(keys)
    return RedirectResponse(url="/", status_code=303)

@app.get("/delete/{key_id}")
def delete_key(key_id: int):
    keys = load_keys()
    if 0 <= key_id < len(keys):
        keys.pop(key_id)
        save_keys(keys)
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
