from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from search import google_ai_mode_search
import os
import psycopg2
from datetime import date

app = FastAPI()
templates = Jinja2Templates(directory="templates")

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookmarks (
            id SERIAL PRIMARY KEY,
            query TEXT NOT NULL,
            answer TEXT NOT NULL,
            date TEXT NOT NULL
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()

class ChatRequest(BaseModel):
    message: str

class BookmarkRequest(BaseModel):
    query: str
    answer: str

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.post("/chat")
async def chat(req: ChatRequest):
    user_message = req.message.strip()
    if not user_message:
        return JSONResponse({"reply": "메시지를 입력해주세요."})
    reply = google_ai_mode_search(user_message)
    return JSONResponse({"reply": reply})

@app.get("/bookmarks")
async def get_bookmarks():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, query, answer, date FROM bookmarks ORDER BY id DESC LIMIT 20")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return JSONResponse([
        {"id": r[0], "query": r[1], "answer": r[2], "date": r[3]}
        for r in rows
    ])

@app.post("/bookmarks")
async def add_bookmark(req: BookmarkRequest):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO bookmarks (query, answer, date) VALUES (%s, %s, %s)",
        (req.query, req.answer, date.today().isoformat())
    )
    conn.commit()
    cur.close()
    conn.close()
    return JSONResponse({"status": "ok"})

@app.delete("/bookmarks/{bookmark_id}")
async def delete_bookmark(bookmark_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM bookmarks WHERE id = %s", (bookmark_id,))
    conn.commit()
    cur.close()
    conn.close()
    return JSONResponse({"status": "ok"})