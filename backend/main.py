import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from backend.agent import run_agent, run_agent_stream, get_history, list_sessions, delete_session
from backend.tools import get_price

load_dotenv()

app = FastAPI(title="FunnyMarketNews API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request/Response models ────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    session_id: str
    personality: str = "professional"  # "professional" | "wsb"


class ChatResponse(BaseModel):
    reply: str
    tool_calls: list


# ── API routes ─────────────────────────────────────────────────────────────────

@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    if req.personality not in ("professional", "wsb"):
        raise HTTPException(status_code=400, detail="personality must be 'professional' or 'wsb'")

    return StreamingResponse(
        run_agent_stream(req.message, req.session_id, req.personality),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    if req.personality not in ("professional", "wsb"):
        raise HTTPException(status_code=400, detail="personality must be 'professional' or 'wsb'")

    result = await run_agent(req.message, req.session_id, req.personality)
    return ChatResponse(**result)


@app.get("/api/history/{session_id}")
def history(session_id: str):
    messages = get_history(session_id)
    return {"session_id": session_id, "messages": messages}


@app.get("/api/stocks/price/{ticker}")
async def stock_price(ticker: str):
    result = get_price(ticker.upper())
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@app.get("/api/sessions")
def sessions():
    return {"sessions": list_sessions()}


@app.delete("/api/sessions/{session_id}")
def remove_session(session_id: str):
    delete_session(session_id)
    return {"deleted": session_id}


@app.get("/health")
def health():
    return {"status": "ok"}


# ── Serve frontend ─────────────────────────────────────────────────────────────

frontend_dir = os.path.join(os.path.dirname(__file__), "..", "svelte-frontend", "dist")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
