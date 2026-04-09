from typing import TypedDict, Optional
from dotenv import load_dotenv

load_dotenv()


class ResearchState(TypedDict):
    ticker:          str
    news_articles:   Optional[list]
    news_summary:    Optional[str]
    financials:      Optional[dict]
    sentiment_score: Optional[float]
    report:          Optional[str]


def planner_node(state: ResearchState) -> dict:
    ticker = state["ticker"].upper().strip()
    if ticker.endswith(".NS"):
        market = "India NSE"
    elif ticker.endswith(".BO"):
        market = "India BSE"
    else:
        market = "US"
    print(f"[Planner] Starting pipeline — {ticker} ({market})")
    return {
        "ticker":          ticker,
        "news_articles":   None,
        "news_summary":    None,
        "financials":      None,
        "sentiment_score": None,
        "report":          None,
    }
