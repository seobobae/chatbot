from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from search import google_ai_mode_search
import json
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")

BOOKMARK_FILE = "bookmarks.json"

def load_bookmarks():
    if os.path.exists(BOOKMARK_FILE):
        with open(BOOKMARK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_bookmarks(bookmarks):
    with open(BOOKMARK_FILE, "w", encoding="utf-8") as f:
        json.dump(bookmarks, f, ensure_ascii=False, indent=2)

class ChatRequest(BaseModel):
    message: str

class BookmarkRequest(BaseModel):
    query: str
    answer: str

class BookmarkDeleteRequest(BaseModel):
    index: int

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
    return JSONResponse(load_bookmarks())

@app.post("/bookmarks")
async def add_bookmark(req: BookmarkRequest):
    bookmarks = load_bookmarks()
    bookmarks.insert(0, {
        "query": req.query,
        "answer": req.answer,
        "date": __import__("datetime").date.today().isoformat()
    })
    if len(bookmarks) > 20:
        bookmarks = bookmarks[:20]
    save_bookmarks(bookmarks)
    return JSONResponse({"status": "ok"})

@app.delete("/bookmarks/{index}")
async def delete_bookmark(index: int):
    bookmarks = load_bookmarks()
    if 0 <= index < len(bookmarks):
        bookmarks.pop(index)
        save_bookmarks(bookmarks)
    return JSONResponse({"status": "ok"})