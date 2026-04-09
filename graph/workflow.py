from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

load_dotenv()

from agents.planner    import ResearchState, planner_node
from agents.news       import news_node
from agents.financials import financials_node
from agents.sentiment  import sentiment_node
from agents.analyst    import analyst_node


def build_graph():
    builder = StateGraph(ResearchState)

    # Node names must NOT match ResearchState field names.
    # "financials" is a state key → renamed to "fetch_financials"
    builder.add_node("planner",          planner_node)
    builder.add_node("news",             news_node)
    builder.add_node("fetch_financials", financials_node)
    builder.add_node("sentiment",        sentiment_node)
    builder.add_node("analyst",          analyst_node)

    builder.add_edge(START,              "planner")
    builder.add_edge("planner",          "news")
    builder.add_edge("planner",          "fetch_financials")
    builder.add_edge("news",             "sentiment")
    builder.add_edge("sentiment",        "analyst")
    builder.add_edge("fetch_financials", "analyst")
    builder.add_edge("analyst",          END)

    return builder.compile()


graph = build_graph()
print("[Workflow] Graph compiled successfully")
