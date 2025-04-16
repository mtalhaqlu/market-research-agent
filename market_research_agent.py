from typing import List
from dotenv import load_dotenv
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langchain.schema import SystemMessage, HumanMessage
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool

load_dotenv()

search = DuckDuckGoSearchRun()
yfinance = YahooFinanceNewsTool()
tools = [search, yfinance]

model = init_chat_model("qwen-qwq-32b", model_provider="groq")
model_with_tools = model.bind_tools(tools)

agent_executor = create_react_agent(model, tools)

COLLECTOR_PROMPT = """You are an intent clarification agent.

Your role is to collect **clear and complete intent** from the user before any further processing of their query. You are not allowed to use any tools, perform searches, or provide answers. Your only goal is to ask clarifying questions to understand the user’s true intent.

Only when:
- You have complete clarity, respond with: **"Thank you. I now have enough information."**
- The user explicitly asks you to assume things, respond with: **"Thank you. I now have enough information by assuming the following things:"** followed by the assumptions.

Keep responses short, precise, and focused on uncovering ambiguities or missing details.

---

### One-Shot Example

**User Query**:  
"Tell me about demand for organic in fast fashion and sales trends."

**Your Clarifying Response**:  
"Could you clarify the following:
1. Are you interested in a specific region or global trends?
2. Should the analysis cover a specific time range (e.g., past 3–5 years)?
3. Do you want data on consumer demand, brand adoption, or both?"

If the user responds with:  
"Just assume it's about the EU and last 3 years."

**Your Final Response**:  
"Thank you. I now have enough information by assuming the following things:
1. The focus is on the EU region.
2. The timeframe is the past 3 years.
3. Both consumer demand and brand sales trends are of interest."
"""


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
    SESSION_STORE[session_id].append(HumanMessage(content=last_response))

    is_complete = "i now have enough information" in last_response.lower()
    return {"response": last_response, "done": is_complete}

def user_reply(session_id: str, user_input: str):
    """Handle user reply to the LLM."""
    SESSION_STORE[session_id].append(HumanMessage(content=user_input))
    return step_conversation(session_id)

def get_conversation(session_id: str):
    return SESSION_STORE.get(session_id, [])

PLANNER_PROMPT  = """You are a planner agent. Your task is to break down the user's query into a clear, actionable research or analysis plan. Focus only on understanding what steps are necessary to fully address the query. The output should be a structured list of steps, not the answer itself.

Example 1:
User Query: "What is the current market landscape for electric vehicles in Germany?"
Plan:
- Step 1: Research current EV market share in Germany
- Step 2: Identify top EV manufacturers and popular models in the German market
- Step 3: Gather information on government incentives and regulations
- Step 4: Investigate the status and growth of charging infrastructure
- Step 5: Analyze trends in consumer adoption and preferences

Example 2:
User Query: "What is the market positioning of major soft drink brands in India?"
Plan:
- Step 1: Identify key players in the Indian soft drink market
- Step 2: Analyze branding, pricing, and product strategies of each brand
- Step 3: Review sales data and market share for major soft drink brands
- Step 4: Explore consumer perception and brand loyalty trends
- Step 5: Evaluate marketing campaigns and distribution strategies

Your output must only be like this pattern nothing more
Plan:
- Step 1:
- Step 2:
...

"""


def generate_plan(clarified_query: str) -> str:
    messages: List = [
        SystemMessage(content=PLANNER_PROMPT),
        HumanMessage(content=clarified_query)
    ]
    response = model.invoke(messages)
    return response.content.split("</think>\n", 1)[1]


EXECUTOR_PROMPT = """You are an executor and researcher agent.
Think of yourself as a researcher who has received a series of steps.
Your task is to reason through and *execute* the following action steps to fulfill the user’s query.
For each step:
1. Reason through the task and decide the best approach: Available Tools Duck Duck Go, Yahoo Finance News, LLM itself
2. Then actually perform the action using the chosen approach.
3. Report the outcome of each step
4. Do not merge or synthesize the outcomes of each

Follow this format:
Step {n}:
- Action: <step description>
- Reasoning: <why this approach/tool is appropriate>
- Tool Used: <tool name or "LLM">
- Output: <result or gathered data>

Steps:
{steps}

Now begin executing each step one by one, reasoning and performing the action, and providing the output.
"""


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

SYNTHESIS_PROMPT = """You are a synthesis agent tasked with interpreting research data to produce clear, insightful, and actionable summaries.

You will receive:
1. A summary of the user's original queries and intentions.
2. A collection of researched information from multiple sources.

Your job is to:
- Understand the user's intent and needs based on their query.
- Analyze the collected information critically.
- Identify patterns, insights, and connections that address the user's query.
- Resolve any contradictions or ambiguities if present.
- Deliver a well-reasoned synthesis that clearly answers the user's question or supports their decision-making.
- In your synthesis do not refer to things like step 5 or 4 rather use proper referecnes 

Be concise but informative. Focus on relevance, accuracy, and clarity. Think like a human analyst writing an executive-level brief.

If there are uncertainties or differing perspectives in the data, acknowledge them and suggest what could help clarify.

Begin your synthesis below:
"""

def synthesize_information(steps: str) -> str:
    messages: List = [
        SystemMessage(content=SYNTHESIS_PROMPT),
        HumanMessage(content=steps)
    ]
    response = model.invoke(messages)
    return response.content




