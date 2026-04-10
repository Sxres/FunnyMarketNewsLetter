import os
import json
import finnhub
import yfinance as yf
from tavily import TavilyClient
from datetime import datetime, timezone
import logging
import warnings

logging.getLogger("yfinance").setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*utcnow.*")
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_supabase: Client | None = None
_finnhub = None
_tavily = None

def _get_supabase() -> Client:
    global _supabase
    if _supabase is None:
        _supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_API"))
    return _supabase

def _get_finnhub():
    global _finnhub
    if _finnhub is None:
        _finnhub = finnhub.Client(api_key=os.getenv("FINNHUB_API_KEY"))
    return _finnhub

def _get_tavily():
    global _tavily
    if _tavily is None:
        _tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    return _tavily

NEWS_CACHE_TTL_MINUTES = 60


# ── Claude tool definitions ────────────────────────────────────────────────────

TOOL_DEFINITIONS = [
    {
        "name": "search_web",
        "description": (
            "Search the web for any financial information, stock prices, market news, or research. "
            "Use this when other tools fail, when you need current price data for obscure or small-cap tickers, "
            "when the user asks a general market question not tied to a specific ticker, "
            "or when you need to look up anything not covered by the other tools."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query, e.g. 'CIFR stock price today' or 'Fed interest rate decision 2025'",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_financials",
        "description": (
            "Get key financial metrics for a stock: P/E ratio, revenue, earnings, profit margins, debt, "
            "and other fundamental data. Use this when the user asks about valuation, fundamentals, "
            "whether a stock is cheap or expensive, or wants a full company breakdown."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol, e.g. AAPL, TSLA, NVDA",
                }
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "get_insider_trades",
        "description": (
            "Get recent insider buying and selling activity for a stock. "
            "Use this when the user asks about insider activity, whether executives are buying or selling, "
            "or wants signals from people inside the company."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol, e.g. AAPL, TSLA, NVDA",
                }
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "get_analyst_ratings",
        "description": (
            "Get analyst consensus ratings, price targets, and recent upgrades/downgrades for a stock. "
            "Use this when the user asks what analysts think, about price targets, buy/sell ratings, "
            "or Wall Street sentiment."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol, e.g. AAPL, TSLA, NVDA",
                }
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "get_price",
        "description": (
            "Get the current stock price, change, volume, and key metrics for any ticker symbol. "
            "Use this whenever the user asks about a stock's price, performance, or market data."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol, e.g. AAPL, TSLA, NVDA",
                }
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "get_news",
        "description": (
            "Get recent news articles for a stock ticker. "
            "Use this whenever the user asks about news, sentiment, or recent events for a stock. "
            "Results are cached for 60 minutes to avoid redundant API calls."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol, e.g. AAPL, TSLA, NVDA",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max number of articles to return (default 10, max 25)",
                    "default": 10,
                },
            },
            "required": ["ticker"],
        },
    },
]


# ── Tool implementations ───────────────────────────────────────────────────────

def get_price(ticker: str) -> dict:
    ticker = ticker.upper().strip()
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="5d", interval="1d")

        if hist.empty:
            return {"error": f"No price data found for {ticker}"}

        hist = hist[["Close", "Volume"]].dropna()
        if hist.empty:
            return {"error": f"No valid price data for {ticker}"}

        current = float(hist["Close"].iloc[-1])
        prev = float(hist["Close"].iloc[-2]) if len(hist) > 1 else current
        change = current - prev
        change_pct = (change / prev) * 100 if prev else 0

        info = t.fast_info

        return {
            "ticker": ticker,
            "price": round(current, 2),
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "volume": int(hist["Volume"].iloc[-1]),
            "market_cap": getattr(info, "market_cap", None),
            "fifty_two_week_high": getattr(info, "year_high", None),
            "fifty_two_week_low": getattr(info, "year_low", None),
            "as_of": hist.index[-1].strftime("%Y-%m-%d"),
        }
    except Exception as e:
        return {"error": f"Failed to fetch price for {ticker}: {str(e)}"}


def get_news(ticker: str, limit: int = 10) -> dict:
    ticker = ticker.upper().strip()
    limit = min(limit, 25)

    # Check Supabase cache first
    cached = _get_cached_news(ticker)
    if cached:
        articles = cached[:limit]
        return {"ticker": ticker, "articles": articles, "source": "cache", "count": len(articles)}

    # Fetch from Finnhub
    try:
        from datetime import timedelta
        now = datetime.now(timezone.utc)
        from_date = (now - timedelta(days=7)).strftime("%Y-%m-%d")
        to_date = now.strftime("%Y-%m-%d")

        raw = _get_finnhub().company_news(ticker, _from=from_date, to=to_date)
        if not raw:
            return {"ticker": ticker, "articles": [], "count": 0, "note": "No recent news found"}

        articles = [
            {
                "headline": a.get("headline", ""),
                "summary": a.get("summary", ""),
                "source": a.get("source", ""),
                "url": a.get("url", ""),
                "published": datetime.fromtimestamp(a["datetime"], tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                if a.get("datetime") else "",
                "sentiment": a.get("sentiment", None),
            }
            for a in raw
        ]

        _cache_news(ticker, articles)
        return {"ticker": ticker, "articles": articles[:limit], "source": "finnhub", "count": len(articles[:limit])}

    except Exception as e:
        return {"error": f"Failed to fetch news for {ticker}: {str(e)}"}


def search_web(query: str) -> dict:
    try:
        response = _get_tavily().search(
            query=query,
            search_depth="basic",
            max_results=5,
            include_answer=True,
        )
        return {
            "answer": response.get("answer", ""),
            "results": [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("content", ""),
                    "published_date": r.get("published_date", ""),
                }
                for r in response.get("results", [])
            ],
        }
    except Exception as e:
        return {"error": f"Search failed: {str(e)}"}


def get_financials(ticker: str) -> dict:
    ticker = ticker.upper().strip()
    try:
        info = yf.Ticker(ticker).info
        if not info or info.get("trailingPE") is None and info.get("marketCap") is None:
            return {"error": f"No financial data found for {ticker}"}

        def fmt(v):
            if v is None: return None
            if isinstance(v, float): return round(v, 4)
            return v

        return {
            "ticker": ticker,
            "company_name": info.get("longName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "market_cap": info.get("marketCap"),
            "pe_ratio_trailing": fmt(info.get("trailingPE")),
            "pe_ratio_forward": fmt(info.get("forwardPE")),
            "peg_ratio": fmt(info.get("pegRatio")),
            "price_to_book": fmt(info.get("priceToBook")),
            "price_to_sales": fmt(info.get("priceToSalesTrailing12Months")),
            "revenue_ttm": info.get("totalRevenue"),
            "gross_margin": fmt(info.get("grossMargins")),
            "operating_margin": fmt(info.get("operatingMargins")),
            "profit_margin": fmt(info.get("profitMargins")),
            "eps_trailing": fmt(info.get("trailingEps")),
            "eps_forward": fmt(info.get("forwardEps")),
            "revenue_growth_yoy": fmt(info.get("revenueGrowth")),
            "earnings_growth_yoy": fmt(info.get("earningsGrowth")),
            "total_debt": info.get("totalDebt"),
            "total_cash": info.get("totalCash"),
            "debt_to_equity": fmt(info.get("debtToEquity")),
            "return_on_equity": fmt(info.get("returnOnEquity")),
            "return_on_assets": fmt(info.get("returnOnAssets")),
            "dividend_yield": fmt(info.get("dividendYield")),
            "beta": fmt(info.get("beta")),
            "short_float_pct": fmt(info.get("shortPercentOfFloat")),
        }
    except Exception as e:
        return {"error": f"Failed to fetch financials for {ticker}: {str(e)}"}


def get_insider_trades(ticker: str) -> dict:
    ticker = ticker.upper().strip()
    try:
        t = yf.Ticker(ticker)
        trades = t.insider_transactions

        if trades is None or trades.empty:
            return {"ticker": ticker, "trades": [], "note": "No recent insider transactions found"}

        recent = trades.head(15)
        result = []
        for _, row in recent.iterrows():
            result.append({
                "insider": str(row.get("Insider", "")),
                "title": str(row.get("Position", "")),
                "transaction": str(row.get("Transaction", "")),
                "shares": int(row["Shares"]) if row.get("Shares") is not None else None,
                "value": int(row["Value"]) if row.get("Value") is not None else None,
                "date": str(row.get("Start Date", "")),
            })

        buys = sum(1 for r in result if "buy" in r["transaction"].lower() or "purchase" in r["transaction"].lower())
        sells = sum(1 for r in result if "sell" in r["transaction"].lower() or "sale" in r["transaction"].lower())

        return {
            "ticker": ticker,
            "trades": result,
            "summary": {"buys": buys, "sells": sells, "total": len(result)},
        }
    except Exception as e:
        return {"error": f"Failed to fetch insider trades for {ticker}: {str(e)}"}


def get_analyst_ratings(ticker: str) -> dict:
    ticker = ticker.upper().strip()
    try:
        t = yf.Ticker(ticker)
        info = t.info

        # Consensus summary from info
        consensus = {
            "ticker": ticker,
            "recommendation": info.get("recommendationKey"),        # "buy", "hold", "sell"
            "recommendation_mean": info.get("recommendationMean"),  # 1=Strong Buy, 5=Sell
            "number_of_analysts": info.get("numberOfAnalystOpinions"),
            "target_price_mean": info.get("targetMeanPrice"),
            "target_price_high": info.get("targetHighPrice"),
            "target_price_low": info.get("targetLowPrice"),
            "current_price": info.get("currentPrice"),
        }

        # Recent upgrades/downgrades
        upgrades_df = t.upgrades_downgrades
        recent_actions = []
        if upgrades_df is not None and not upgrades_df.empty:
            upgrades_df = upgrades_df.sort_index(ascending=False).head(10)
            for date, row in upgrades_df.iterrows():
                recent_actions.append({
                    "date": str(date)[:10],
                    "firm": str(row.get("Firm", "")),
                    "action": str(row.get("Action", "")),
                    "from_grade": str(row.get("FromGrade", "")),
                    "to_grade": str(row.get("ToGrade", "")),
                })

        consensus["recent_actions"] = recent_actions
        return consensus
    except Exception as e:
        return {"error": f"Failed to fetch analyst ratings for {ticker}: {str(e)}"}


# ── Cache helpers ──────────────────────────────────────────────────────────────

def _get_cached_news(ticker: str) -> list | None:
    try:
        result = (
            _get_supabase().table("news_cache")
            .select("articles, fetched_at")
            .eq("ticker", ticker)
            .order("fetched_at", desc=True)
            .limit(1)
            .execute()
        )
        if not result.data:
            return None

        row = result.data[0]
        fetched_at = datetime.fromisoformat(row["fetched_at"].replace("Z", "+00:00"))
        age_minutes = (datetime.now(timezone.utc) - fetched_at).total_seconds() / 60

        if age_minutes > NEWS_CACHE_TTL_MINUTES:
            return None

        return row["articles"]
    except Exception:
        return None


def _cache_news(ticker: str, articles: list) -> None:
    try:
        _get_supabase().table("news_cache").upsert(
            {
                "ticker": ticker,
                "articles": articles,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            },
            on_conflict="ticker",
        ).execute()
    except Exception:
        pass  # cache write failure is non-fatal


# ── Dispatcher called by agent loop ───────────────────────────────────────────

def execute_tool(name: str, inputs: dict) -> str:
    if name == "get_price":
        result = get_price(inputs["ticker"])
    elif name == "get_news":
        result = get_news(inputs.get("ticker"), inputs.get("limit", 10))
    elif name == "get_financials":
        result = get_financials(inputs["ticker"])
    elif name == "get_insider_trades":
        result = get_insider_trades(inputs["ticker"])
    elif name == "get_analyst_ratings":
        result = get_analyst_ratings(inputs["ticker"])
    elif name == "search_web":
        result = search_web(inputs["query"])
    else:
        result = {"error": f"Unknown tool: {name}"}

    return json.dumps(result)
