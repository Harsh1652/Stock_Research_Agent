# 📊 Stock Research Agent

A **multi-agent AI system** that analyzes any stock ticker (US or India) and generates a structured **BUY / HOLD / SELL** report in under 30 seconds.

Built using **LangGraph**, **OpenAI**, and real-time financial + news data.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2.28-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-teal)
![LangSmith](https://img.shields.io/badge/LangSmith-traced-orange)

---

## 🔥 Overview

Manual stock research takes hours — reading news, analyzing financials, and forming a view.

This system automates the entire workflow using **5 specialized AI agents running in parallel**, delivering an **analyst-grade report in seconds**.

---

## ⚙️ What It Does

Enter a ticker like `AAPL`, `TSLA`, `RELIANCE.NS`, or just `SUZLON` — the system will:

1. Detect the market (US / NSE / BSE) automatically
2. Fetch real-time news via Tavily Search
3. Pull live financial data via yfinance (price, P/E, market cap, 52-week range)
4. Score market sentiment using GPT-4o-mini
5. Synthesize a structured BUY / HOLD / SELL recommendation using GPT-4o

---

## 🧠 Agent Architecture

```
        START
          │
          ▼
     [Planner Agent]
     Normalizes ticker, detects market
          │
   ┌──────┴────────┐
   ▼               ▼
[News Agent]   [Financials Agent]
Tavily →       yfinance
gpt-4o-mini    (no LLM)
   │               │
   ▼               │
[Sentiment Agent]  │
gpt-4o-mini →      │
float 0.0–1.0      │
   │               │
   └──────┬────────┘
          ▼
   [Analyst Agent]
   gpt-4o → BUY/HOLD/SELL report
          │
          ▼
         END
```

News + Financials run in **parallel** (LangGraph superstep). Total latency ~25–35 seconds.

### Agent Breakdown

| Agent | Role |
|-------|------|
| **Planner** | Normalizes ticker, detects US vs India, fans out to parallel agents |
| **News** | Fetches + summarizes latest stock news via Tavily |
| **Financials** | Pulls structured financial data from yfinance (no LLM used) |
| **Sentiment** | Converts news summary → sentiment score between 0.0 and 1.0 |
| **Analyst** | Synthesizes all inputs into a final BUY / HOLD / SELL report |

---

## ⚡ Key Features

- ⚡ **Parallel Execution** — News and Financials agents run simultaneously, not sequentially
- 🧠 **Multi-Agent Architecture** — Each agent has a single responsibility, easy to extend
- 🌍 **Multi-Market Support** — US stocks, Indian NSE/BSE, with automatic market detection
- 💰 **Cost Optimized** — GPT-4o-mini for simple tasks, GPT-4o only for the final report
- 🔍 **Full Observability** — Every run traced in LangSmith with token counts + latency
- 📊 **Structured Output** — Consistent report format every time

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Agent Orchestration | LangGraph 0.2 (StateGraph) |
| LLMs | GPT-4o (analyst) + GPT-4o-mini (news, sentiment) |
| News Search | Tavily Search API |
| Financial Data | yfinance (free, no API key required) |
| Observability | LangSmith |
| Backend | FastAPI + Uvicorn |
| Frontend | HTML + Vanilla JS |
| Deployment | Railway (Procfile included) |

---

## 📁 Project Structure

```
stock-research-agent/
├── agents/
│   ├── planner.py          # ResearchState TypedDict + entry node
│   ├── news.py             # Tavily fetch + gpt-4o-mini summary
│   ├── financials.py       # yfinance data pull (no LLM)
│   ├── sentiment.py        # gpt-4o-mini → sentiment float
│   ├── analyst.py          # gpt-4o final synthesis
│   └── *.ipynb             # Notebook versions for demo
├── graph/
│   ├── workflow.py         # LangGraph StateGraph definition
│   └── workflow.ipynb      # Notebook version
├── tools/
│   ├── search.py           # Tavily wrapper
│   └── yfinance_tool.py    # yfinance with US → NSE → BSE fallback
├── api/
│   └── main.py             # FastAPI app — serves frontend + /research
├── frontend/
│   └── index.html          # Single-page UI
├── .env                    # API keys (never commit)
├── requirements.txt
└── Procfile                # Railway deployment config
```

---

## 🚀 Setup

### 1. Clone and install

```bash
git clone <repo-url>
cd stock-research-agent
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure `.env`

```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
LANGCHAIN_API_KEY=lsv2_pt_...
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=stock-research-agent
API_SECRET_KEY=any-random-string
```

| Variable | Where to get it |
|----------|----------------|
| `OPENAI_API_KEY` | platform.openai.com → API keys |
| `TAVILY_API_KEY` | tavily.com → API Keys (free tier: 1,000/month) |
| `LANGCHAIN_API_KEY` | smith.langchain.com → Settings → API Keys |

### 3. Run the API

```bash
uvicorn api.main:app --reload
```

Open 👉 **http://localhost:8000**

### 4. Run as Notebook (Optional)

```bash
jupyter notebook
```

Open `graph/workflow.ipynb` and run all cells for a full end-to-end demo.

---

## 📡 API

### `POST /research`

**Request:**
```json
{ "ticker": "AAPL" }
```

**Response:**
```json
{
  "ticker": "AAPL",
  "market": "US",
  "report": "## RECOMMENDATION\nBUY — Strong earnings momentum...",
  "sentiment_score": 0.72,
  "financials": {
    "current_price": 203.5,
    "pe_ratio": 28.4,
    "market_cap": 3100000000000,
    "52_week_high": 237.23,
    "52_week_low": 164.08
  },
  "news_summary": "Apple reported record Q1 revenue..."
}
```

### Supported Ticker Formats

| Input | Market | Notes |
|-------|--------|-------|
| `AAPL`, `TSLA`, `NVDA` | US | Direct lookup |
| `RELIANCE.NS`, `TCS.NS` | India NSE | Explicit NSE suffix |
| `RELIANCE.BO` | India BSE | Explicit BSE suffix |
| `SUZLON`, `ZOMATO` | India (auto) | Falls back US → NSE → BSE |

---

## 📊 Sample Output

```
## RECOMMENDATION
BUY — Strong earnings momentum and expanding AI services addressable market.

## PRICE TARGET
$240 over 12 months (18% upside from $203), based on 25x forward P/E
applied to $9.60 FY2026 EPS consensus.

## TOP 3 REASONS
1. Revenue grew 11% YoY to $124B in Q1 2025, beating estimates by $2.1B
2. Services segment (35% gross margin) now 28% of total revenue — structural mix shift
3. Apple Intelligence driving iPhone upgrade cycle; installed base at record 2.2B devices

## KEY RISKS
1. China revenue (-3% YoY) facing regulatory headwinds and local competition
2. Valuation at 28x earnings leaves limited margin of safety in a risk-off environment
3. EU Digital Markets Act compliance costs and potential fine exposure (~$38B cap)

## SUMMARY
Apple remains a high-quality compounder with durable cash flows and a strengthening
services flywheel. Maintain BUY with a 12-month target of $240.
```

---

## 💰 Cost Per Run

| Component | Model | Approx cost |
|-----------|-------|------------|
| News summary | gpt-4o-mini | ~$0.001 |
| Sentiment scoring | gpt-4o-mini | ~$0.0005 |
| Analyst report | gpt-4o | ~$0.02 |
| **Total** | | **~$0.02 per report** |

---

## 🔍 Observability (LangSmith)

Every run is fully traced at [smith.langchain.com](https://smith.langchain.com):

- Full prompt + completion for every LLM call
- Token usage and cost per agent
- End-to-end latency breakdown
- The complete 5-agent execution tree

---

## 🧠 Why This Project Matters

This is not a simple chatbot.

It demonstrates:

- **Multi-agent orchestration** — coordinating specialized agents with shared state
- **Parallel execution** — LangGraph supersteps for concurrent agent runs
- **Real-world data integration** — live news + financial APIs in a production pipeline
- **Cost-aware LLM design** — right model for the right task
- **Production-ready API** — FastAPI with input validation, error handling, CORS

---

## 📌 Future Improvements

- Streaming responses (real-time report generation in UI)
- Multi-stock comparison (portfolio view)
- Historical sentiment tracking over time
- Redis caching layer to avoid redundant API calls
- User watchlist with scheduled daily reports

---

## 👨‍💻 Author

**Harsh Gupta**
Software Engineer | AI Systems Builder

---

⭐ If you found this useful, give it a star — or build your own version!
