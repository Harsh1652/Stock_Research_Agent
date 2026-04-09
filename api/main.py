"""
Stock Research Agent — FastAPI (open public API, no auth).
Supports US tickers (AAPL) and Indian tickers (RELIANCE.NS, SUZLON).
"""

import os
import re
import sys

# Ensure project root is importable (agents, graph, tools packages)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from graph.workflow import graph  # pure Python — no nbimporter needed

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Stock Research Agent",
    description="Multi-agent AI system for US and Indian stock research via LangGraph.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Ticker validation
# ---------------------------------------------------------------------------

_TICKER_RE = re.compile(r"^[A-Z]{1,10}(\.(NS|BO))?$")


def _validate_ticker(raw: str) -> str:
    ticker = raw.upper().strip()
    if not _TICKER_RE.match(ticker):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Invalid ticker. Use US format (AAPL) or Indian format "
                "(RELIANCE.NS / TCS.BO). Bare names like SUZLON also work."
            ),
        )
    return ticker

# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class ResearchRequest(BaseModel):
    ticker: str


class ResearchResponse(BaseModel):
    ticker:          str
    market:          str
    report:          str
    sentiment_score: float | None
    financials:      dict | None
    news_summary:    str | None

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.post("/research", response_model=ResearchResponse)
async def research_stock(request: ResearchRequest):
    """
    Run the 5-agent LangGraph pipeline for any stock ticker.
    Typical latency: 15–30 seconds.
    """
    ticker = _validate_ticker(request.ticker)

    if ticker.endswith(".NS"):
        market = "India (NSE)"
    elif ticker.endswith(".BO"):
        market = "India (BSE)"
    else:
        market = "US"

    try:
        result = graph.invoke({"ticker": ticker})
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline failed: {str(exc)}",
        )

    # If yfinance auto-resolved bare ticker to NSE/BSE, update market label
    fin = result.get("financials") or {}
    if market == "US" and fin.get("market") == "India":
        market = "India (NSE/BSE — auto-detected)"

    return ResearchResponse(
        ticker=result["ticker"],
        market=market,
        report=result["report"],
        sentiment_score=result.get("sentiment_score"),
        financials=fin,
        news_summary=result.get("news_summary"),
    )


@app.get("/health")
async def health():
    return {"status": "ok", "service": "stock-research-agent"}


# ---------------------------------------------------------------------------
# Serve frontend
# ---------------------------------------------------------------------------

_frontend_dir = os.path.join(_PROJECT_ROOT, "frontend")
if os.path.isdir(_frontend_dir):
    app.mount("/", StaticFiles(directory=_frontend_dir, html=True), name="static")

# ---------------------------------------------------------------------------
# Dev entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
