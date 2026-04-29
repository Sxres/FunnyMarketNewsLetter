# dimas

An AI stock research assistant that pulls live prices, news, fundamentals, and insider trades on demand, then streams an analyst-style answer back to you in real time. Pick a **professional** tone (Bloomberg-style) or a **WSB** tone (degen energy) and chat with any ticker on the market.

<img width="1920" height="919" alt="Moonanimation3" src="https://github.com/user-attachments/assets/c3198b4a-388f-4328-85ae-7812b96d8c2c" />
<img width="1920" height="927" alt="Chat" src="https://github.com/user-attachments/assets/e359d7c0-75d6-4049-8994-40f886bb975b" />
<img width="1920" height="927" alt="Tools" src="https://github.com/user-attachments/assets/b375714c-d1ab-4f8c-8e31-2bd2f88ede00" />

## How it feels

Type *"what's going on with NVDA?"* and within a second you're watching live cards populate. The price ticks in, news headlines slide into a feed, fundamentals fill out a stat block, and insider trades fan out as a buy/sell breakdown. While all of that is rendering, Claude is already writing its analysis on top, tokens streaming in like a research note being typed in front of you.

No watchlists. No pre-ingested tickers. No "sorry, I don't have data for that." Ask about anything that trades and it just works.

## Under the hood

Claude (`claude-sonnet-4-6`) is handed four tools and told to call every single one before it speaks. That means every answer is grounded in the same fresh dataset, with no hallucinated prices and no stale numbers.

| Tool | Source | Returns |
|---|---|---|
| `get_price` | yfinance → Finnhub fallback | Live price, change %, volume, 52-week high/low |
| `get_news` | Finnhub (cached 60 min) | Company news, 7-day window |
| `get_financials` | Finnhub | P/E, revenue, margins, debt, ROE, beta, short interest |
| `get_insider_trades` | Finnhub | 90-day insider transactions, buy/sell summary |

The agent loop runs until Claude says it's done, which means it can chain tool calls, re-check a number, or pull more context mid-thought. Every tool event (`tool_start`, `tool_done`, `token`) is pushed over SSE so the UI stays in sync with what the model is actually doing.

## Two personalities, one brain

- **Professional.** Reads like a Bloomberg terminal. Measured, numbers-first, opinionated only where the data supports it.
- **WSB.** Reads like the top-voted comment on r/wallstreetbets at 3am. Same data, different vibe.

Same tools, same retrieval layer, completely different voice, swapped with one click.

## Stack

- **Backend.** FastAPI, Anthropic SDK, yfinance, Finnhub, Supabase (auth + chat history + news cache), slowapi rate limiting
- **Frontend.** SvelteKit 2, Svelte 5, TypeScript, Vite
- **Auth.** Supabase JWT verified against JWKS, every chat scoped to a user
- **Infra.** Docker, Google Cloud Run

## Things I'm proud of

- **No pre-ingestion pipeline.** Claude fetches everything on demand, so the app works for any ticker the instant it's typed.
- **Streaming-first UI.** Tool cards render the moment each tool finishes. You watch the research assemble itself, you don't stare at a spinner.
- **Graceful degradation.** yfinance is primary; three retries with exponential backoff, then automatic Finnhub failover. The user never sees the seams.
- **Cached where it matters.** News gets a 60-minute Supabase cache so repeat ticker questions don't hammer the API or the user's patience.
- **Per-user memory.** Conversations persist across sessions, scoped to the authenticated user, so context carries over between visits.
