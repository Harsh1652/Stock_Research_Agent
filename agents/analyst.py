import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

load_dotenv()

_llm = ChatOpenAI(model="gpt-4o", temperature=0.1)


def _sentiment_label(score: float) -> str:
    if score is None: return "Unknown"
    if score < 0.2:   return "Very Bearish"
    if score < 0.4:   return "Bearish"
    if score < 0.6:   return "Neutral"
    if score < 0.8:   return "Bullish"
    return "Very Bullish"


def analyst_node(state: dict) -> dict:
    ticker          = state["ticker"]
    news_summary    = state.get("news_summary")    or "No news available."
    financials      = state.get("financials")      or {}
    sentiment_score = state.get("sentiment_score") or 0.5

    print(f"[Analyst] Synthesizing report for {ticker}...")

    label   = _sentiment_label(sentiment_score)
    fin_str = json.dumps(financials, indent=2, default=str)

    prompt = f"""You are a senior equity research analyst at a top-tier investment bank.
Generate a structured investment report based on the data below.

TICKER: {ticker}

NEWS SUMMARY:
{news_summary}

FINANCIAL DATA:
{fin_str}

SENTIMENT SCORE: {sentiment_score:.2f} / 1.00 ({label})

Generate the report with EXACTLY these sections and headers:

## RECOMMENDATION
BUY / HOLD / SELL  (pick one, explain in one sentence)

## PRICE TARGET
12-month price target with brief valuation justification (1-2 sentences)

## TOP 3 REASONS
1. [Reason with specific data point]
2. [Reason with specific data point]
3. [Reason with specific data point]

## KEY RISKS
1. [Risk 1]
2. [Risk 2]
3. [Risk 3]

## SUMMARY
[2-3 sentence executive summary for a busy portfolio manager]

Be specific, cite numbers from the financial data, and maintain a professional analyst tone."""

    response = _llm.invoke([HumanMessage(content=prompt)])
    report   = response.content.strip()
    print(f"[Analyst] Report generated ({len(report)} chars)")
    return {"report": report}
