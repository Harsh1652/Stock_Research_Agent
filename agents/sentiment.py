from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

load_dotenv()

_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def _score_to_label(score: float) -> str:
    if score < 0.2:  return "Very Bearish"
    if score < 0.4:  return "Bearish"
    if score < 0.6:  return "Neutral"
    if score < 0.8:  return "Bullish"
    return "Very Bullish"


def sentiment_node(state: dict) -> dict:
    ticker       = state["ticker"]
    news_summary = state.get("news_summary") or "No recent news available."
    print(f"[Sentiment] Scoring for {ticker}...")

    prompt = (
        f"You are a quantitative analyst. Analyze the sentiment of these news bullets "
        f"about {ticker} stock and return a single decimal number between 0.0 and 1.0.\n\n"
        f"Scale: 0.0=Very Bearish, 0.25=Bearish, 0.5=Neutral, 0.75=Bullish, 1.0=Very Bullish\n\n"
        f"News:\n{news_summary}\n\n"
        f"Return ONLY the decimal number — nothing else."
    )

    response = _llm.invoke([HumanMessage(content=prompt)])
    try:
        score = float(response.content.strip())
        score = max(0.0, min(1.0, score))
    except (ValueError, AttributeError):
        score = 0.5

    print(f"[Sentiment] Score: {score:.2f} ({_score_to_label(score)})")
    return {"sentiment_score": score}
