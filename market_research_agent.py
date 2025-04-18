from typing import List
from dotenv import load_dotenv
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
from prompts import COLLECTOR_PROMPT, PLANNER_PROMPT, EXECUTOR_PROMPT, SYNTHESIS_PROMPT

load_dotenv()

# Tools
search = DuckDuckGoSearchRun()
yfinance = YahooFinanceNewsTool()
tools = [search, yfinance]

# Model and Model Binding
model = init_chat_model("qwen-qwq-32b", model_provider="groq")
model_with_tools = model.bind_tools(tools)

agent_executor = create_react_agent(model, tools)

# In-memory session store
SESSION_STORE = {}

def start_conversation(session_id: str, user_query: str):
    """Initialize a conversation session."""
    messages = [
        SystemMessage(content=COLLECTOR_PROMPT),
        HumanMessage(content=user_query)
    ]
    SESSION_STORE[session_id] = messages
    return step_conversation(session_id)

def step_conversation(session_id: str):
    """Run LLM on current session history and get its response."""
    messages = SESSION_STORE[session_id]
    steps = agent_executor.stream({"messages": messages}, stream_mode="values")

    last_response = None
    for step in steps:
        last_response = step["messages"][-1].content

    # Append LLM's latest reply to session
    SESSION_STORE[session_id].append(AIMessage(content=last_response))

    is_complete = "i now have enough information" in last_response.lower()
    return {"response": last_response, "done": is_complete}

def user_reply(session_id: str, user_input: str):
    """Handle user reply to the LLM."""
    SESSION_STORE[session_id].append(HumanMessage(content=user_input))
    return step_conversation(session_id)

def get_conversation(session_id: str):
    return SESSION_STORE.get(session_id, [])

def generate_plan(clarified_query: str) -> str:
    messages: List = [
        SystemMessage(content=PLANNER_PROMPT),
        HumanMessage(content=clarified_query)
    ]
    response = model.invoke(messages)

    if "</think>" in response.content:
        return response.content.split("</think>", 1)[1].strip()
    else:
        return response.content.strip()

def execute_plan(steps: str) -> str:
    """Executes the steps provided by the planner agent."""
    # Prepare the input for the model
    messages: List = [
        SystemMessage(content=EXECUTOR_PROMPT),
        HumanMessage(content=steps)
    ]

    response = agent_executor.invoke({"messages": messages})
    
    # Return the result of the execution
    return response

def synthesize_information(steps: str) -> str:
    messages: List = [
        SystemMessage(content=SYNTHESIS_PROMPT),
        HumanMessage(content=steps)
    ]
    response = model.invoke(messages)
    return response.content




