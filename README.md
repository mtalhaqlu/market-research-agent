# 🧠 Multi-Agent Market Research System

A modular multi-agent system for market research tasks. It clarifies user intent, plans research steps, executes searches, and synthesizes findings into a coherent, transparent response.

Built with **LangChain** for reasoning traceability, stateful sessions, and tool integration.

---

## 🔧 Features

- **Intent Clarification**: Conversationally extracts missing info (e.g. region, timeframe, metrics).
- **Planner**: Breaks clarified query into actionable research steps.
- **Executor/Researcher**: Executes each step via DuckDuckGo, Yahoo Finance, or LLM.
- **Synthesis**: Merges findings, resolves contradictions, and generates final insights.
- **Transparency**: Full breakdown of planning, execution, and synthesis steps in response.

---

## 🛠️ Stack

- **LLM**: `Qwen-qwq-32b`
- **Framework**: `LangChain`
- **Search Tools**: DuckDuckGo, Yahoo Finance

---

## 📁 Installation

```bash
git clone https://github.com/mtalhaqlu/market-research-agent.git
cd market-research-agent
touch .env                # Add your GROQ_API_KEY inside
pip install -r requirements.txt
uvicorn server:app

## Making Requests

```bash
curl -X POST http://127.0.0.1:8000/start \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "129",
    "query": "What is the market for electric vehicles in Germany?"
  }'

