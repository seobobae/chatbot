from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from search import google_ai_mode_search
import os
import asyncpg
from datetime import date

app = FastAPI()
templates = Jinja2Templates(directory="templates")

DATABASE_URL = os.getenv("DATABASE_URL")

async def get_conn():
    return await asyncpg.connect(DATABASE_URL)

@app.on_event("startup")
async def startup():
    conn = await get_conn()
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS bookmarks (
            id SERIAL PRIMARY KEY,
            query TEXT NOT NULL,
            answer TEXT NOT NULL,
            date TEXT NOT NULL
        )
    """)
    await conn.close()

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
    conn = await get_conn()
    rows = await conn.fetch(
        "SELECT id, query, answer, date FROM bookmarks ORDER BY id DESC LIMIT 20"
    )
    await conn.close()
    return JSONResponse([dict(r) for r in rows])

@app.post("/bookmarks")
async def add_bookmark(req: BookmarkRequest):
    conn = await get_conn()
    await conn.execute(
        "INSERT INTO bookmarks (query, answer, date) VALUES ($1, $2, $3)",
        req.query, req.answer, date.today().isoformat()
    )
    await conn.close()
    return JSONResponse({"status": "ok"})

@app.delete("/bookmarks/{bookmark_id}")
async def delete_bookmark(bookmark_id: int):
    conn = await get_conn()
    await conn.execute("DELETE FROM bookmarks WHERE id = $1", bookmark_id)
    await conn.close()
    return JSONResponse({"status": "ok"})