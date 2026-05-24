from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from search import google_ai_mode_search

app = FastAPI()
templates = Jinja2Templates(directory="templates")

class ChatRequest(BaseModel):
    message: str

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