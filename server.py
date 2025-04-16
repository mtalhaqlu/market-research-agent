from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from market_research_agent import start_conversation, user_reply, get_conversation, generate_plan, execute_plan, synthesize_information
from utils import clean_output, extract_actions_with_tools
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain_core.messages.tool import ToolMessage

app = FastAPI()

class QueryRequest(BaseModel):
    session_id: str
    query: str

class ReplyRequest(BaseModel):
    session_id: str
    message: str

@app.post("/start")
def start(query: QueryRequest):
    response = start_conversation(query.session_id, query.query)
    return response

@app.post("/reply")
def reply(data: ReplyRequest):
    convo = get_conversation(data.session_id)
    if not convo:
        raise HTTPException(status_code=404, detail="Session not found")
    response = user_reply(data.session_id, data.message)

    if response["done"]:
        response = {}

        full_query = get_combined_conversation(data.session_id)
        plan = generate_plan(full_query)
        response["plan"] = clean_output(plan)

        execution = execute_plan(plan)
        response["execution"] = extract_actions_with_tools(execution["messages"][2].content)

        collected_information = ""
        for output in execution["messages"]:
            if isinstance(output, AIMessage) or isinstance(output, ToolMessage):
                collected_information += " "
                collected_information += str(output.content)

        human_query_summary = get_human_conversation(data.session_id).split("\n\nHuman:", 1)[1]

        synthesis_input = (
            "Summary of User Queries:\n"
            + human_query_summary.strip()
            + "\n\nCollected Information:\n"
            + collected_information.strip()
        )

        synthesis = synthesize_information(synthesis_input)
        response["synthesis"] = clean_output(synthesis)

    return response 


@app.get("/history/{session_id}")
def history(session_id: str):
    convo = get_conversation(session_id)
    return {
        "history": [{"role": msg.type, "content": msg.content} for msg in convo] if convo else[],
        "message_count": len(convo) if convo else 0
    }

def get_combined_conversation(session_id: str) -> str:
    convo = get_conversation(session_id)
    lines = []
    for msg in convo:
        if isinstance(msg, SystemMessage):
            role = "System"
        elif isinstance(msg, HumanMessage):
            role = "Human"
        elif isinstance(msg, AIMessage):
            role = "AI"
        elif isinstance(msg, ToolMessage):
            role = "Tool"
        else:
            role = "Unknown"
        lines.append(f"{role}: {msg.content}")
    return "\n".join(lines)

def get_human_conversation(session_id: str) -> str:
    convo = get_conversation(session_id)
    lines = []
    role = ""
    for msg in convo:
        if isinstance(msg, HumanMessage):
            role = "Human"
        lines.append(f"{role}: {msg.content}")
    return "\n".join(lines)
