import os
import json
import time
import finnhub
import yfinance as yf
from datetime import datetime, timezone, timedelta
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

NEWS_CACHE_TTL_MINUTES = 60
YF_MAX_RETRIES = 3
YF_BACKOFF_SECONDS = 0.6




# ── Claude tool definitions ────────────────────────────────────────────────────

TOOL_DEFINITIONS = [
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
    last_yf_error = ""

    for attempt in range(YF_MAX_RETRIES):
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="5d", interval="1d")

            if not hist.empty:
                hist = hist[["Close", "Volume"]].dropna()
                if not hist.empty:
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
                        "source": "yfinance",
                    }

            last_yf_error = "No price data returned from Yahoo"
        except Exception as e:
            last_yf_error = str(e)

        if attempt < YF_MAX_RETRIES - 1:
            time.sleep(YF_BACKOFF_SECONDS * (2 ** attempt))

    # Fallback: Finnhub quote endpoint is more stable under Yahoo throttling.
    try:
        quote = _get_finnhub().quote(ticker)
        current = float(quote.get("c") or 0)
        if current <= 0:
            return {"error": f"No price data found for {ticker} (Yahoo + Finnhub unavailable)"}

        prev_close = float(quote.get("pc") or current)
        change = float(quote.get("d") or (current - prev_close))
        change_pct = float(quote.get("dp") or ((change / prev_close) * 100 if prev_close else 0))
        high = quote.get("h")
        low = quote.get("l")
        ts = quote.get("t")

        return {
            "ticker": ticker,
            "price": round(current, 2),
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "volume": None,
            "market_cap": None,
            "fifty_two_week_high": round(float(high), 2) if isinstance(high, (int, float)) and high > 0 else None,
            "fifty_two_week_low": round(float(low), 2) if isinstance(low, (int, float)) and low > 0 else None,
            "as_of": datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d") if ts else datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "source": "finnhub",
            "note": "Yahoo data temporarily unavailable; used Finnhub fallback",
        }
    except Exception as e:
        details = last_yf_error or "unknown Yahoo failure"
        return {"error": f"Failed to fetch price for {ticker}: Yahoo error ({details}); Finnhub error ({str(e)})"}


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


def get_financials(ticker: str) -> dict:
    ticker = ticker.upper().strip()
    try:
        fh = _get_finnhub()
        profile = fh.company_profile2(symbol=ticker)
        basics = fh.company_basic_financials(ticker, 'all')
        metric = basics.get("metric", {}) if basics else {}

        if not metric and not profile:
            return {"ticker": ticker, "error": f"No financial data available for {ticker}"}

        def fmt(v):
            if v is None: return None
            if isinstance(v, (int, float)): return round(float(v), 4)
            return v

        return {
            "ticker": ticker,
            "company_name": profile.get("name"),
            "sector": profile.get("finnhubIndustry"),
            "industry": profile.get("finnhubIndustry"),
            "market_cap": round(profile["marketCapitalization"] * 1_000_000) if profile.get("marketCapitalization") else None,
            "pe_ratio_trailing": fmt(metric.get("peBasicExclExtraTTM")),
            "pe_ratio_forward": fmt(metric.get("peExclExtraForward")),
            "peg_ratio": fmt(metric.get("pegRatioTTM")),
            "price_to_book": fmt(metric.get("pbQuarterly")),
            "price_to_sales": fmt(metric.get("psTTM")),
            "revenue_ttm": metric.get("revenueTTM"),
            "gross_margin": fmt(metric.get("grossMarginTTM")),
            "operating_margin": fmt(metric.get("operatingMarginTTM")),
            "profit_margin": fmt(metric.get("netProfitMarginTTM")),
            "eps_trailing": fmt(metric.get("epsBasicExclExtraItemsTTM")),
            "eps_forward": fmt(metric.get("epsForward")),
            "revenue_growth_yoy": fmt(metric.get("revenueGrowthQuarterlyYoy")),
            "earnings_growth_yoy": fmt(metric.get("epsGrowthQuarterlyYoy")),
            "total_debt": metric.get("totalDebtTTM"),
            "total_cash": metric.get("cashAndShortTermInvestments"),
            "debt_to_equity": fmt(metric.get("totalDebt/totalEquityQuarterly")),
            "return_on_equity": fmt(metric.get("roeTTM")),
            "return_on_assets": fmt(metric.get("roaTTM")),
            "dividend_yield": fmt(metric.get("dividendYieldIndicatedAnnual")),
            "beta": fmt(metric.get("beta")),
            "short_float_pct": fmt(metric.get("shortInterestPercentOfFloat")),
        }
    except Exception as e:
        return {"ticker": ticker, "error": f"Financial data unavailable for {ticker}"}


def get_insider_trades(ticker: str) -> dict:
    ticker = ticker.upper().strip()
    try:
        fh = _get_finnhub()
        now = datetime.now(timezone.utc)
        from_date = (now - timedelta(days=90)).strftime("%Y-%m-%d")
        to_date = now.strftime("%Y-%m-%d")

        data = fh.stock_insider_transactions(ticker, from_date, to_date)
        raw = data.get("data", []) if data else []

        if not raw:
            return {"ticker": ticker, "trades": [], "summary": {"buys": 0, "sells": 0, "total": 0}, "note": "No recent insider transactions found"}

        # transactionCode: P=Purchase, S=Sale, A=Grant/Award, M=Exercise, G=Gift, etc.
        _CODE_LABELS = {"P": "Purchase", "S": "Sale", "A": "Award", "M": "Exercise", "G": "Gift", "F": "Tax Withhold"}

        result = []
        for t in raw[:15]:
            code = t.get("transactionCode", "") or ""
            label = _CODE_LABELS.get(code, t.get("transactionType") or code or "Unknown")
            shares = abs(t.get("change", 0)) if t.get("change") else t.get("share")
            result.append({
                "insider": t.get("name", ""),
                "title": "",
                "transaction": label,
                "shares": shares,
                "value": round(abs(t.get("change", 0)) * t.get("transactionPrice", 0)) if t.get("change") and t.get("transactionPrice") else None,
                "date": t.get("transactionDate", ""),
            })

        buys = sum(1 for r in result if r["transaction"] in ("Purchase",))
        sells = sum(1 for r in result if r["transaction"] in ("Sale",))

        return {
            "ticker": ticker,
            "trades": result,
            "summary": {"buys": buys, "sells": sells, "total": len(result)},
        }
    except Exception as e:
        return {"ticker": ticker, "error": f"Insider trade data unavailable for {ticker}"}


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
    else:
        result = {"error": f"Unknown tool: {name}"}

    return json.dumps(result)
