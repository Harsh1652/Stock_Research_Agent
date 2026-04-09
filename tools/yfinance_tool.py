import yfinance as yf
from dotenv import load_dotenv

load_dotenv()


def _safe(info: dict, key: str):
    """Return None if value is missing, zero, or 'N/A'."""
    val = info.get(key)
    return None if val in (None, "N/A", "", 0, "None") else val


def _fetch_yf(symbol: str) -> dict:
    """Single yfinance call — returns parsed metrics dict."""
    try:
        ticker = yf.Ticker(symbol)
        info   = ticker.info

        # yfinance returns {"trailingPE": 28.5} directly — no raw/fmt wrapper
        return {
            "ticker":               symbol.upper(),
            "company_name":         _safe(info, "longName") or _safe(info, "shortName"),
            "current_price":        _safe(info, "currentPrice") or _safe(info, "regularMarketPrice"),
            "previous_close":       _safe(info, "previousClose"),
            "pe_ratio":             _safe(info, "trailingPE"),
            "forward_pe":           _safe(info, "forwardPE"),
            "price_to_book":        _safe(info, "priceToBook"),
            "revenue_growth":       _safe(info, "revenueGrowth"),
            "earnings_growth":      _safe(info, "earningsGrowth"),
            "market_cap":           _safe(info, "marketCap"),
            "52_week_high":         _safe(info, "fiftyTwoWeekHigh"),
            "52_week_low":          _safe(info, "fiftyTwoWeekLow"),
            "dividend_yield":       _safe(info, "dividendYield"),
            "beta":                 _safe(info, "beta"),
            "sector":               _safe(info, "sector"),
            "industry":             _safe(info, "industry"),
            "analyst_target_price": _safe(info, "targetMeanPrice"),
            "recommendation":       _safe(info, "recommendationKey"),
        }
    except Exception as exc:
        print(f"[yfinance] fetch failed for {symbol}: {exc}")
        return {}


def _is_india(symbol: str) -> bool:
    return symbol.upper().endswith((".NS", ".BO"))


def get_stock_data(ticker: str) -> dict:
    """
    Fetch financial metrics via yfinance (free, no API key needed).

    Auto-fallback for bare Indian tickers:
      SUZLON → try US → try SUZLON.NS → try SUZLON.BO

    Supported formats:
      AAPL          US stock
      RELIANCE.NS   India NSE
      TCS.BO        India BSE
      SUZLON        auto-detected as India NSE
    """
    t = ticker.upper().strip()

    # Explicit Indian suffix → fetch directly
    if t.endswith(".NS") or t.endswith(".BO"):
        data = _fetch_yf(t)
        data["market"]   = "India"
        data["currency"] = "₹"
        return data

    # No suffix → try US first
    print(f"[yfinance] Trying US for '{t}'...")
    us_data = _fetch_yf(t)
    if us_data.get("current_price"):
        print(f"[yfinance] Found '{t}' on US market")
        us_data["market"]   = "US"
        us_data["currency"] = "$"
        return us_data

    # US failed → try India NSE
    ns = f"{t}.NS"
    print(f"[yfinance] Not found on US, trying {ns} (India NSE)...")
    ns_data = _fetch_yf(ns)
    if ns_data.get("current_price"):
        print(f"[yfinance] Found '{ns}'")
        ns_data["market"]   = "India"
        ns_data["currency"] = "₹"
        return ns_data

    # NSE failed → try India BSE
    bo = f"{t}.BO"
    print(f"[yfinance] Trying {bo} (India BSE)...")
    bo_data = _fetch_yf(bo)
    if bo_data.get("current_price"):
        print(f"[yfinance] Found '{bo}'")
        bo_data["market"]   = "India"
        bo_data["currency"] = "₹"
        return bo_data

    print(f"[yfinance] WARNING: no data found for '{t}'")
    us_data["market"]   = "US"
    us_data["currency"] = "$"
    return us_data
