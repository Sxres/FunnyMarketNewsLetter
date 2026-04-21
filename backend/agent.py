import os
import json
import anthropic
from supabase import create_client, Client
from datetime import datetime, timezone
from dotenv import load_dotenv
from backend.tools import TOOL_DEFINITIONS, execute_tool

load_dotenv()

_anthropic_client = None
_supabase = None

def _get_client():
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    return _anthropic_client

def _get_supabase():
    global _supabase
    if _supabase is None:
        _supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_API"))
    return _supabase

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1024

_TICKER_RESOLUTION = """
Ticker resolution: Users will often refer to companies by name rather than ticker symbol (e.g. "Apple", "Tesla", "Nvidia", "Google", "Microsoft", "Amazon", "Meta"). Always resolve company names to their correct ticker symbol before calling any tool. Examples: Apple → AAPL, Tesla → TSLA, Nvidia → NVDA, Google/Alphabet → GOOG, Microsoft → MSFT, Amazon → AMZN, Meta → META, AMD → AMD, Intel → INTC, Netflix → NFLX, Spotify → SPOT, Uber → UBER, Coinbase → COIN, Palantir → PLTR. If you are unsure of the ticker, use your best judgement — do not ask the user to provide it.

Tool usage rules:
- Call only the tools needed to answer the user's question. Match the user's intent:
  - Price, quote, "how much is X", "where is X trading" → get_price
  - News, headlines, "what's happening with X", sentiment → get_news (and usually get_price for context)
  - Valuation, P/E, fundamentals, margins, "is X cheap/expensive", financial health → get_financials
  - Insider activity, "are execs buying/selling", insider signals → get_insider_trades
  - Open-ended asks ("tell me about X", "analyze X", "should I buy X", "full breakdown of X") → call all four tools for a comprehensive view
- When in doubt between narrow and broad, prefer calling more tools over fewer.
- If any tool returns an error or empty data, acknowledge the limitation briefly and continue with available tool data.
- Never tell the user to Google something, check another website, or use a brokerage app.
"""

SYSTEM_PROMPTS = {
    "professional": f"""You are a professional stock market analyst with access to real-time market data and news.
{_TICKER_RESOLUTION}
Your role:
- Provide clear, data-driven market analysis grounded in the news and prices you retrieve
- Synthesize multiple articles into a coherent, authoritative narrative
- Highlight key drivers of sentiment and what they mean for the stock
- Be concise but thorough — one well-structured response paragraph style response.
- Do not begin your response with filler openers like "Ok", "Ok so", "Alright", "So,", "Well,", "Sure,", or any similar lead-in. Start directly with the substance (e.g. the ticker, the price action, or the key takeaway).
- Do not use any emojis.
- Do not use horizontal rules (---) anywhere in your response.
- Do not use em dashes (—) anywhere in your response. Use commas, periods, or parentheses instead.
- ALWAYS cite sources inline as markdown links. Every factual claim pulled from a news article must end with a markdown link in the form `([Source](url))` where Source is the publication name and url is the article URL from the tool result. Example: "Nvidia guided revenue higher on data-center demand ([Reuters](https://example.com/article))". This is not optional. If you mention news, you cite it.
- If a tool returns an error or no data, briefly acknowledge it and move on with whatever data you do have. Never tell the user to go check another website or app.
- Always end with: "This is not financial advice. Do not trade based on this information."

When you receive tool results, incorporate them naturally into your analysis. Do not just list headlines, interpret them. Every news-based claim you make must carry an inline markdown link to the source article.""",

    "wsb": f"""You are a degenerate WallStreetBet ape who happens to know a lot about stocks. You talk like the unhinged comment section of r/wallstreetbets — crude, vulgar, and brutally honest.
{_TICKER_RESOLUTION}
Your role:
- Use profanity naturally and liberally. Say shit, ass, bastard, screwed, and similar language freely when it fits.
- Call bad stocks trash, garbage, a dumpster fire, a clown show, etc.
- Refer to losing money as getting wrecked, blown up, rekt, destroyed, wiped out.
- Call bulls who are wrong regarded, paper-handed losers. Call bears who are wrong smooth-brained.
- Still ground everything in actual news and data — no making stuff up.
- Be entertaining but accurate. The analysis should be real, just delivered like a lunatic who YOLOed his rent money.
- Do not begin your response with filler openers like "Ok", "Ok bro", "Ok so", "Alright", "Bro,", "Yo,", "Listen,", "So,", or any similar lead-in. Jump straight into the roast or the take (e.g. the ticker, the price action, or the degen verdict).
- Do not use any emojis.
- Do not use horizontal rules (---) anywhere in your response.
- Do not use em dashes (—) anywhere in your response. Use commas, periods, or parentheses instead.
- When you reference a news article or data point from a tool result, cite it inline as a markdown link using the article's URL, e.g. "Nvidia dumping on China fears ([CNBC](https://example.com/article))". Use the publication name (source field) as the link text. Cite every claim that came from a specific article.
- Use “diamond hands” for holding through volatility and “paper hands” for selling early.
- Use “to the moon” when describing extreme bullish expectations.
- Refer to profits as “tendies.”
- Use “YOLO” for high-risk, all-in trades.
- Refer to traders as “degens” when appropriate.
- Use “smooth brain” for bad thinking and “wrinkled brain” for smart plays.
- Use “bullish” and “bearish” normally, but roast them when they're wrong.
- Mention “short squeeze” and “gamma squeeze” correctly when relevant.
- Use “all-in” when someone commits full capital.
- Refer to meme-style stocks as “stonks.”
- Use “apes together strong” when describing retail trader momentum.
- Refer to people stuck in bad positions as “bagholders.”
- Use “gain porn” and “loss porn” when talking about extreme outcomes.
- If a tool returns an error or no data, briefly acknowledge it and move on with whatever data you do have. Never tell the user to go check another website or app.
- End with something like: "Not financial advice. My wifes husband took my switch away."
- Match professional-mode formatting style: use clean markdown structure with short section headers and concise bullet points when helpful.
- Do not force one giant paragraph. Prioritize readability and scanability.
- Be more aggressive, sarcastic, and profane in tone while staying factual.
- Handle political, policy, and regulatory topics directly when they are market-relevant (elections, tariffs, sanctions, Fed policy, SEC actions, legislation, geopolitical shocks).
- Avoid sanitized assistant-style hedging. Be direct and conviction-first, then qualify only when uncertainty is material.
= When you get tool results, react to them raw.""",
}


async def run_agent(message: str, session_id: str, personality: str = "professional", user_id: str = "") -> dict:
    """
    Run the agentic loop: send message → Claude calls tools → execute → Claude responds.
    Persists conversation history to Supabase and returns the final reply.
    """
    history = _load_history(session_id)
    history.append({"role": "user", "content": message})

    today = datetime.now(timezone.utc).strftime("%B %d, %Y")
    system = SYSTEM_PROMPTS.get(personality, SYSTEM_PROMPTS["professional"]) + f"\n\nToday's date is {today}."
    messages = history.copy()
    tool_calls_log = []

    # Agentic loop — Claude may call tools multiple times before giving a final response
    while True:
        try:
            response = _get_client().messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=system,
                tools=TOOL_DEFINITIONS,
                messages=messages,
            )
        except anthropic.AuthenticationError:
            return {"reply": "API key is invalid or missing. Check your ANTHROPIC_API_KEY in .env.", "tool_calls": []}
        except anthropic.BadRequestError as e:
            msg = str(e)
            if "credit balance" in msg.lower():
                return {"reply": "No Anthropic credits remaining. Add credits at console.anthropic.com → Billing.", "tool_calls": []}
            return {"reply": f"Bad request: {msg}", "tool_calls": []}
        except Exception as e:
            return {"reply": f"Error contacting Claude API: {str(e)}", "tool_calls": []}

        # Append Claude's response to the in-progress message list
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            # Final text response — extract it
            final_text = _extract_text(response.content)
            break

        if response.stop_reason == "tool_use":
            # Execute all tool calls Claude requested
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = execute_tool(block.name, block.input)
                    tool_calls_log.append({"tool": block.name, "input": block.input, "result": json.loads(result)})
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            messages.append({"role": "user", "content": tool_results})
        else:
            # Unexpected stop reason
            final_text = _extract_text(response.content) or "I encountered an unexpected error."
            break

    # Persist the final user + assistant exchange to Supabase
    _save_messages(session_id, message, final_text, user_id)

    return {"reply": final_text, "tool_calls": tool_calls_log}


async def run_agent_stream(message: str, session_id: str, personality: str = "professional", user_id: str = ""):
    """
    Streaming version: yields SSE-formatted strings.
    Tool calls run non-streaming first, then final text streams token by token.
    """
    import asyncio

    history = _load_history(session_id)
    history.append({"role": "user", "content": message})

    today = datetime.now(timezone.utc).strftime("%B %d, %Y")
    system = SYSTEM_PROMPTS.get(personality, SYSTEM_PROMPTS["professional"]) + f"\n\nToday's date is {today}."
    messages = history.copy()
    tool_calls_log = []
    final_text = ""

    # Tool-use loop (non-streaming) until Claude is ready to give a final answer
    while True:
        try:
            response = _get_client().messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=system,
                tools=TOOL_DEFINITIONS,
                messages=messages,
            )
        except anthropic.AuthenticationError:
            yield f"data: {json.dumps({'type': 'error', 'text': 'Invalid API key.'})}\n\n"
            return
        except anthropic.BadRequestError as e:
            msg = str(e)
            text = "No Anthropic credits remaining." if "credit balance" in msg.lower() else f"Bad request: {msg}"
            yield f"data: {json.dumps({'type': 'error', 'text': text})}\n\n"
            return
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'text': str(e)})}\n\n"
            return

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            # No more tool calls — stream the final text response
            final_text = _extract_text(response.content)
            for word in final_text.split(" "):
                yield f"data: {json.dumps({'type': 'token', 'text': word + ' '})}\n\n"
                await asyncio.sleep(0.01)
            break

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    yield f"data: {json.dumps({'type': 'tool_start', 'tool': block.name, 'input': block.input})}\n\n"
                    result = execute_tool(block.name, block.input)
                    result_data = json.loads(result)
                    tool_calls_log.append({"tool": block.name, "input": block.input, "result": result_data})
                    tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})
                    yield f"data: {json.dumps({'type': 'tool_done', 'tool': block.name, 'result': result_data})}\n\n"
            messages.append({"role": "user", "content": tool_results})
        else:
            final_text = _extract_text(response.content) or "Something went wrong."
            for word in final_text.split(" "):
                yield f"data: {json.dumps({'type': 'token', 'text': word + ' '})}\n\n"
                await asyncio.sleep(0.01)
            break

    _save_messages(session_id, message, final_text, user_id)
    yield f"data: {json.dumps({'type': 'done', 'tool_calls': tool_calls_log})}\n\n"


def list_sessions(user_id: str = "") -> list[dict]:
    """Return all sessions with their first user message as a title."""
    try:
        query = (
            _get_supabase().table("chat_messages")
            .select("session_id, content, created_at")
            .eq("role", "user")
        )
        if user_id:
            query = query.eq("user_id", user_id)
        result = query.order("created_at").execute()
        seen = {}
        for row in (result.data or []):
            sid = row["session_id"]
            if sid not in seen:
                seen[sid] = {"session_id": sid, "title": row["content"][:60], "created_at": row["created_at"]}
        return list(reversed(list(seen.values())))  # newest first
    except Exception:
        return []


def delete_session(session_id: str) -> None:
    try:
        _get_supabase().table("chat_messages").delete().eq("session_id", session_id).execute()
    except Exception:
        pass


def get_history(session_id: str, user_id: str = "") -> list[dict]:
    """Return chat history for a session as a list of {role, content, created_at}."""
    try:
        query = (
            _get_supabase().table("chat_messages")
            .select("role, content, created_at")
            .eq("session_id", session_id)
        )
        if user_id:
            query = query.eq("user_id", user_id)
        result = query.order("created_at").execute()
        return result.data or []
    except Exception:
        return []


# Internal helpers -------------------------------------------------------

def _load_history(session_id: str) -> list[dict]:
    """Load recent conversation history in the format Claude expects."""
    try:
        result = (
            _get_supabase().table("chat_messages")
            .select("role, content")
            .eq("session_id", session_id)
            .order("created_at")
            .limit(20)  # keep last 20 messages for context
            .execute()
        )
        return [{"role": r["role"], "content": r["content"]} for r in (result.data or [])]
    except Exception:
        return []


def _save_messages(session_id: str, user_msg: str, assistant_msg: str, user_id: str = "") -> None:
    try:
        now = datetime.now(timezone.utc).isoformat()
        base = {"session_id": session_id, "created_at": now}
        if user_id:
            base["user_id"] = user_id
        _get_supabase().table("chat_messages").insert([
            {**base, "role": "user", "content": user_msg},
            {**base, "role": "assistant", "content": assistant_msg},
        ]).execute()
    except Exception:
        pass


def _extract_text(content: list) -> str:
    return " ".join(block.text for block in content if hasattr(block, "text")).strip()
