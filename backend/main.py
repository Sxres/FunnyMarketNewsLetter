import os
import jwt
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from dotenv import load_dotenv
from backend.agent import run_agent, run_agent_stream, get_history, list_sessions, delete_session
from backend.tools import get_price

load_dotenv()

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="FunnyMarketNews API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda req, exc: JSONResponse(status_code=429, content={"detail": "Rate limit exceeded. Slow down."}))
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Auth ──────────────────────────────────────────────────────────────────────

_bearer = HTTPBearer()
_supabase_url = os.getenv("SUPABASE_URL", "").rstrip("/")
_jwks_client = jwt.PyJWKClient(f"{_supabase_url}/auth/v1/.well-known/jwks.json")


def get_user_id(creds: HTTPAuthorizationCredentials = Depends(_bearer)) -> str:
    """Verify Supabase JWT and return the user's ID."""
    try:
        signing_key = _jwks_client.get_signing_key_from_jwt(creds.credentials)
        payload = jwt.decode(
            creds.credentials,
            signing_key.key,
            algorithms=["ES256"],
            audience="authenticated",
        )
        user_id = payload.get("sub", "")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: no sub claim")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")


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
@limiter.limit("5/minute")
async def chat_stream(request: Request, req: ChatRequest, user_id: str = Depends(get_user_id)):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    if req.personality not in ("professional", "wsb"):
        raise HTTPException(status_code=400, detail="personality must be 'professional' or 'wsb'")

    return StreamingResponse(
        run_agent_stream(req.message, req.session_id, req.personality, user_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/api/chat", response_model=ChatResponse)
@limiter.limit("5/minute")
async def chat(request: Request, req: ChatRequest, user_id: str = Depends(get_user_id)):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    if req.personality not in ("professional", "wsb"):
        raise HTTPException(status_code=400, detail="personality must be 'professional' or 'wsb'")

    result = await run_agent(req.message, req.session_id, req.personality, user_id)
    return ChatResponse(**result)


@app.get("/api/history/{session_id}")
def history(session_id: str, user_id: str = Depends(get_user_id)):
    messages = get_history(session_id, user_id)
    return {"session_id": session_id, "messages": messages}


@app.get("/api/stocks/price/{ticker}")
async def stock_price(ticker: str):
    result = get_price(ticker.upper())
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@app.get("/api/sessions")
def sessions(user_id: str = Depends(get_user_id)):
    return {"sessions": list_sessions(user_id)}


@app.delete("/api/sessions/{session_id}")
def remove_session(session_id: str, user_id: str = Depends(get_user_id)):
    delete_session(session_id)
    return {"deleted": session_id}


@app.get("/health")
def health():
    return {"status": "ok"}


# ── Serve frontend ─────────────────────────────────────────────────────────────

frontend_dir = os.path.join(os.path.dirname(__file__), "..", "svelte-frontend", "dist")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
