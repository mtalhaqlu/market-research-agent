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

## Starting Conversation

curl -X POST http://127.0.0.1:8000/start \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "129",
    "query": "What is the market for electric vehicles in Germany?"
  }'

## Subsequent Reply Requests from User if inquired by the Chat Agent

curl -X POST http://127.0.0.1:8000/reply \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "129",
    "message": "Focus on market size and growth projections for the next 5 years"
  }'

curl -X POST http://127.0.0.1:8000/reply \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "129",
    "message": "Give Comparative Analysis also of different manufacturers and assume remaining things"
  }'
