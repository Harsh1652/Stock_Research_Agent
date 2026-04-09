import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()


def tavily_search(query: str, max_results: int = 5) -> list[dict]:
    """Fetch recent news articles using Tavily Search API."""
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    response = client.search(
        query=query,
        search_depth="advanced",
        max_results=max_results,
        include_answer=False,
    )
    return response.get("results", [])
