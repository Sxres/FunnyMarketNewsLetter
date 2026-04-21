# FunnyMarketNewsLetter

An AI stock research assistant that pulls live prices, news, fundamentals, and insider trades on demand, then streams an analyst-style answer back to you. Pick a **professional** tone (Bloomberg-style) or a **WSB** tone (degen energy) and chat with any ticker.

<img width="1904" height="926" alt="Home" src=<img width="1894" height="929" alt="Moonanimation" src="https://github.com/user-attachments/assets/7f380886-f1f2-4944-aeee-ae8bfce292b9" />
<img width="1920" height="927" alt="Chat" src="https://github.com/user-attachments/assets/e359d7c0-75d6-4049-8994-40f886bb975b" />
<img width="1920" height="927" alt="Tools" src="https://github.com/user-attachments/assets/b375714c-d1ab-4f8c-8e31-2bd2f88ede00" />

## What it does

Ask about any stock. Claude (`claude-sonnet-4-6`) is given four tools and always calls all of them before replying:

| Tool | Source | Returns |
|---|---|---|
| `get_price` | yfinance → Finnhub fallback | Live price, change %, volume, 52-week high/low |
| `get_news` | Finnhub (cached 60 min in Supabase) | Company news, 7-day window |
| `get_financials` | Finnhub | P/E, revenue, margins, debt, ROE, beta, short interest |
| `get_insider_trades` | Finnhub | 90-day insider transactions, buy/sell summary |

Tool calls stream to the UI as live cards (`PriceCard`, `NewsCard`, `FinancialsCard`, `InsiderCard`) while Claude is still thinking, then the synthesized answer tokens in after.

## Stack

- **Backend** — FastAPI, Anthropic SDK, yfinance, Finnhub, Supabase (auth + chat history + news cache), slowapi for rate limiting
- **Frontend** — SvelteKit 2 + Svelte 5, TypeScript, Vite, `@supabase/supabase-js` for auth
- **Infra** — Docker / Google Cloud Run

## Setup

Requires `uv`, Node 20+, and a Supabase project.

```bash
# 1. Install Python deps
uv sync

# 2. Copy env template and fill in keys
cp .env.example .env
# ANTHROPIC_API_KEY, SUPABASE_URL, SUPABASE_API, FINNHUB_API_KEY

# 3. Create the Supabase tables (see SQL below)

# 4. Build the Svelte frontend
cd svelte-frontend
npm install
npm run build    # outputs to svelte-frontend/dist/
cd ..

# 5. Run the backend (serves API + built frontend)
uv run uvicorn backend.main:app --reload
# → http://localhost:8000
```

For frontend-only development, run `npm run dev` inside `svelte-frontend/` and point it at the backend.

### Supabase schema

```sql
CREATE TABLE news_cache (
  ticker TEXT PRIMARY KEY,
  articles JSONB,
  fetched_at TIMESTAMPTZ
);

CREATE TABLE chat_messages (
  id BIGSERIAL PRIMARY KEY,
  session_id UUID,
  user_id TEXT,
  role TEXT,
  content TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX ON chat_messages (session_id, created_at);
CREATE INDEX ON chat_messages (user_id, created_at);
```

## API

All chat endpoints require a Supabase JWT Bearer token.

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/api/chat/stream` | JWT | SSE stream — emits `tool_start`, `tool_done`, `token`, `done`, `error` |
| `POST` | `/api/chat` | JWT | Non-streaming fallback |
| `GET` | `/api/history/{session_id}` | JWT | Session history |
| `GET` | `/api/sessions` | JWT | List user sessions |
| `DELETE` | `/api/sessions/{session_id}` | JWT | Delete a session |
| `GET` | `/api/stocks/price/{ticker}` | Public | yfinance/Finnhub quote |
| `GET` | `/health` | Public | Health check |

Rate limit: **5 req/min** per IP on `/api/chat` and `/api/chat/stream`. Messages are capped at 2000 chars with HTML stripped and escaped.

## Frontend routes

`/` landing · `/login` · `/signup` · `/chat` · `/market` · `/portfolio` · `/watchlist` · `/settings`

## Design notes

- **No pre-ingestion pipeline.** Claude fetches everything on demand — works for any ticker with no watchlist config.
- **Always-call-all-four.** The system prompt forces Claude to call every tool per stock question so answers are grounded in the same dataset every time.
- **yfinance first, Finnhub fallback.** Three retries with exponential backoff before failover.
- **Streaming first.** Tool cards render as tools complete; tokens stream via SSE.
