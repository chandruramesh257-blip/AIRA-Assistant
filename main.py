from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from aira_brain import get_aira_reply
from database import init_db

load_dotenv()

app = FastAPI(title="AIRA — Personal & Business AI Assistant")

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


class ChatRequest(BaseModel):
    message: str


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.post("/chat")
def chat(request: ChatRequest):
    try:
        reply = get_aira_reply(request.message)
        return {"reply": reply}
    except Exception as error:
        return {"reply": f"AIRA encountered an error: {error}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
