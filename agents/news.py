import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from tools.search import tavily_search

load_dotenv()

_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

_KNOWN_INDIA_TICKERS = {
    "RELIANCE", "TCS", "INFY", "INFOSYS", "WIPRO", "HDFCBANK", "ICICIBANK",
    "SBIN", "AXISBANK", "KOTAKBANK", "LT", "BAJFINANCE", "BHARTIARTL",
    "ASIANPAINT", "MARUTI", "SUNPHARMA", "TITAN", "NESTLEIND", "TATAMOTORS",
    "TATASTEEL", "POWERGRID", "NTPC", "ONGC", "COALINDIA", "ADANIENT",
    "ADANIPORTS", "HINDUNILVR", "ULTRACEMCO", "TECHM", "HCLTECH",
    "SUZLON", "ZOMATO", "PAYTM", "NYKAA", "POLICYBZR", "DMART",
    "IRCTC", "HAL", "BEL", "BHEL", "GAIL", "IOC", "BPCL",
}


def _build_search_query(ticker: str) -> str:
    t = ticker.upper().strip()
    if t.endswith(".NS"):
        return f"{t[:-3]} NSE India stock news earnings results 2025"
    if t.endswith(".BO"):
        return f"{t[:-3]} BSE India stock news earnings results 2025"
    if t in _KNOWN_INDIA_TICKERS:
        return f"{t} India NSE stock news earnings results 2025"
    return f"{t} stock news earnings revenue 2025"


def news_node(state: dict) -> dict:
    ticker = state["ticker"]
    query  = _build_search_query(ticker)
    print(f"[News] Query: '{query}'")

    articles = tavily_search(query, max_results=5)

    articles_text = "\n\n".join([
        f"Title: {a.get('title', 'N/A')}\n"
        f"URL: {a.get('url', 'N/A')}\n"
        f"Content: {a.get('content', '')[:600]}"
        for a in articles
    ])

    is_india = ticker.upper().endswith((".NS", ".BO")) or ticker.upper() in _KNOWN_INDIA_TICKERS
    market_context = "Indian stock (NSE/BSE)" if is_india else "stock"

    prompt = (
        f"Summarize the following news articles about {ticker} {market_context} into "
        f"exactly 3 bullet points. Focus on business impact, earnings, and market sentiment.\n\n"
        f"Articles:\n{articles_text}\n\n"
        f"Return exactly 3 bullet points starting with the • character."
    )

    response = _llm.invoke([HumanMessage(content=prompt)])
    summary  = response.content.strip()
    print(f"[News] Summary ready ({len(summary)} chars)")
    return {"news_articles": articles, "news_summary": summary}
