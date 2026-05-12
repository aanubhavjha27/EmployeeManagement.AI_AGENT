from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, SystemMessage
import json
from dotenv import load_dotenv
load_dotenv()

from tools import (
    search_employee,
    filter_gender,
    delete_employee,
    add_employee,
    showallemployee,
    update_employee
)

# ---------------- STATE ---------------- #

class AgentState(TypedDict):
    message: str
    intent: str
    params: dict
    apiresult: dict
    botmessage: str
    awaiting_confirmation: bool
    confirmed: bool


# ---------------- LLM ---------------- #

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
)

#---memory---#
memory=MemorySaver()

# ---------------- INTENT CLASSIFIER ---------------- #

def classify_intent(state: AgentState) -> AgentState:

    if state.get("awaiting_confirmation"):
        return state

    system = """You are an intent classifier for an Employee Management System. Return ONLY a JSON object with: - "intent": one of "search", "add", "delete", "update", "chitchat","filter_gender","showall" - "params": extracted fields IMPORTANT RULES: - Always return valid JSON - Never include explanations - Normalize field names Search: { "intent": "search", "params": { "name": "rahul" } } Delete: {"intent":"delete","params":{"id":12}} {"intent":"delete","params":{"email":"rahul@gmail.com"}} {"intent":"delete","params":{"phoneNumber":"9876543210"}} {"intent":"delete","params":{"name":"rahul"}} Add: {"intent":"add","params":{"firstname":"rahul","lastname":"vaidya","email":"rahul@gmail.com"}} If missing required: {"intent":"add","params":{"missing_fields":true}} Filter_gender: { "intent": "filter_gender", "params": { "gender": "Male" } } Showall: {"intent":"showall","params":{}} UPDATE: {"intent":"update","params":{"name":"rahul","updates":{"salary":90000}}} If missing update fields: {"intent":"update","params":{"missing_fields":true}} IMPORTANT: - "name" is ONLY for searching - For updating name: use "firstname" and/or "lastname" Chitchat: { "intent": "chitchat", "params": {} } 
Complex tasks → plan

Example:
"delete employees above 60"
→ {"intent":"plan","params":{"task":"delete employees above 60"}}
"""
    response = llm.invoke([
        SystemMessage(content=system),
        HumanMessage(content=state["message"])
    ])

    raw = response.content.strip()

    if raw.startswith("```"):
        raw = raw.strip("```").replace("json", "").strip()

    try:
        parsed = json.loads(raw)
    except:
        parsed = {"intent": "chitchat", "params": {}}

    return {
        **state,
        "intent": parsed.get("intent", "chitchat"),
        "params": parsed.get("params", {})
    }


# ---------------- ROUTER ---------------- #

def route_intent(state: AgentState) -> str:

    if state.get("awaiting_confirmation"):
        msg = state["message"].lower().strip()

        if msg in ["yes", "confirm", "ok", "do it"]:
            return "execute"
        elif msg in ["no", "cancel", "stop"]:
            return "cancel"
        else:
            return "confirm"

    if state["intent"] in ["delete", "update"]:
        return "confirm_direct"

    if state["intent"] == "plan":
        return "plan"

    if state["intent"] in ["search", "filter_gender", "add", "showall"]:
        return state["intent"]

    return "chitchat"


# ---------------- CONFIRMATION ---------------- #

def confirm_direct_node(state: AgentState) -> AgentState:
    return {
        **state,
        "botmessage": f"⚠️ Confirm {state['intent']} with {state['params']}? (yes/no)",
        "awaiting_confirmation": True,
        "confirmed": False,
        "params": {
            **state["params"],
            "direct_action": state["intent"]
        }
    }


def confirmnode(state: AgentState) -> AgentState:
    return {
        **state,
        "botmessage": "⚠️ Confirm planned operation? (yes/no)",
        "awaiting_confirmation": True,
        "confirmed": False
    }


def cancelnode(state: AgentState) -> AgentState:
    return {
        **state,
        "botmessage": "Operation cancelled.",
        "awaiting_confirmation": False,
        "confirmed": False,
        "params": {}
    }


# ---------------- FILTER ---------------- #

def apply_filters(data, filters):
    result = []
    for emp in data:
        ok = True
        for field, condition in filters.items():
            value = emp.get(field)

            if isinstance(condition, str):
                if condition.startswith(">"):
                    if not (value and value > int(condition[1:])):
                        ok = False
                elif condition.startswith("<"):
                    if not (value and value < int(condition[1:])):
                        ok = False
            else:
                if value != condition:
                    ok = False

        if ok:
            result.append(emp)

    return result


# ---------------- PLANNER ---------------- #

def plannode(state: AgentState) -> AgentState:
    return state


# ---------------- EXECUTION ---------------- #

async def executenode(state: AgentState) -> AgentState:

    # ✅ CONFIRMATION HANDLING FIX
    if state.get("awaiting_confirmation"):
        msg = state["message"].lower().strip()

        if msg in ["yes", "confirm", "ok", "do it"]:
            state["confirmed"] = True
            state["awaiting_confirmation"] = False

        elif msg in ["no", "cancel", "stop"]:
            return {
                **state,
                "botmessage": "Operation cancelled.",
                "awaiting_confirmation": False,
                "confirmed": False,
                "params": {}
            }

        else:
            return {
                **state,
                "botmessage": "Please reply with yes or no.",
                "awaiting_confirmation": True
            }

    if not state.get("confirmed"):
        return {
            **state,
            "botmessage": "Action requires confirmation.",
            "awaiting_confirmation": True
        }

    # -------- DIRECT -------- #
    if "direct_action" in state["params"]:
        action = state["params"]["direct_action"]
        params = {k: v for k, v in state["params"].items() if k != "direct_action"}

        if action == "delete":
            res = await delete_employee(**params)
        elif action == "update":
            res = await update_employee(**params)
        else:
            res = {}

        return {
            **state,
            "apiresult": res,
            "awaiting_confirmation": False,
            "confirmed": False,
            "params": {}
        }

    return {
        **state,
        "apiresult": {},
        "awaiting_confirmation": False,
        "confirmed": False,
        "params": {}
    }


# ---------------- BASIC NODES ---------------- #

async def searchnode(state):
    return {**state, "apiresult": await search_employee(state["params"].get("name", ""))}

async def filter_gender_node(state):
    return {**state, "apiresult": await filter_gender(state["params"].get("gender", ""))}

async def add_node(state):
    return {**state, "apiresult": await add_employee(state["params"])}

async def showallnode(state):
    return {**state, "apiresult": await showallemployee()}

def chitchatnode(state):
    return {**state, "apiresult": {}}


# ---------------- RESPONSE ---------------- #

def respondnode(state):
    api = state.get("apiresult", {})
    intent = state["intent"]

    if intent == "delete":
        msg = "Deleted" if api.get("success") else "Delete failed"
    elif intent == "add":
        msg = "Added" if api.get("success") else "Add failed"
    elif intent == "search":
        msg = f"Found {api.get('count', 0)} employees"
    else:
        msg = "Done"

    return {**state, "botmessage": msg}


# ---------------- GRAPH ---------------- #

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("classify_intent", classify_intent)
    graph.add_node("execute", executenode)

    graph.add_node("search", searchnode)
    graph.add_node("filter_gender", filter_gender_node)
    graph.add_node("add", add_node)
    graph.add_node("showall", showallnode)
    graph.add_node("chitchat", chitchatnode)

    graph.add_node("confirm", confirmnode)
    graph.add_node("confirm_direct", confirm_direct_node)
    graph.add_node("cancel", cancelnode)
    graph.add_node("respond", respondnode)

    graph.add_edge(START, "classify_intent")
    graph.add_conditional_edges("classify_intent", route_intent)

    graph.add_edge("execute", "respond")

    graph.add_edge("confirm", END)
    graph.add_edge("confirm_direct", END)
    graph.add_edge("cancel", "respond")

    for node in ["search","filter_gender","add","showall","chitchat"]:
        graph.add_edge(node, "respond")

    graph.add_edge("respond", END)

    return graph.compile(checkpointer=memory)


agent = build_graph()


# ---------------- MEMORY ---------------- #

SESSION = {}

def get_default_state():
    return {
        "message": "",
        "intent": "",
        "params": {},
        "apiresult": {},
        "botmessage": "",
        "awaiting_confirmation": False,
        "confirmed": False
    }


# ---------------- RUN ---------------- #

async def run_agent(thread_id: str, message: str):

    initial_state={
        "message": message,
        "intent": "",
        "params": {},
        "apiresult": {},
        "botmessage": "",
        "awaiting_confirmation": False,
        "confirmed": False
    }

    config={"configurable":{"thread_id":thread_id}}
    result=await agent.ainvoke(initial_state,config=config)

    return {
        "action": result.get("intent", ""),
        "botmessage": result.get("botmessage", ""),
        "employees": result.get("apiresult", {}).get("employees", []),
        "success": result.get("apiresult", {}).get("success", False),
    }