from dotenv import load_dotenv
from tools.yfinance_tool import get_stock_data

load_dotenv()


def financials_node(state: dict) -> dict:
    ticker = state["ticker"]
    print(f"[Financials] Pulling data for {ticker}...")
    data  = get_stock_data(ticker)
    price = data.get("current_price")
    pe    = data.get("pe_ratio")
    mcap  = data.get("market_cap")
    cur   = data.get("currency", "$")
    mcap_str = f"{cur}{mcap:,.0f}" if mcap else "N/A"
    print(f"[Financials] Price={cur}{price} | P/E={pe} | MktCap={mcap_str}")
    return {"financials": data}
