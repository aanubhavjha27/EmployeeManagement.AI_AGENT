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

# ---------------- MEMORY ---------------- #

memory = MemorySaver()


# ---------------- INTENT CLASSIFIER ---------------- #

def classify_intent(state: AgentState) -> AgentState:

    # ✅ If waiting for confirmation, skip classification
    if state.get("awaiting_confirmation"):
        return state

    system = """You are an intent classifier for an Employee Management System.
Return ONLY a valid JSON object. No explanations. No markdown.

INTENTS: search, add, delete, update, filter_gender, showall, chitchat

FIELD NAME RULES - Always use these EXACT field names:
- Phone/mobile/contact number → "phoneNumber"  
- First name → "firstname"
- Last name → "lastname"
- Email → "email"
- Salary/pay/wage → "salary"
- Department/dept → "department"
- Gender/sex → "gender"
- Age → "age"

EXAMPLES:

Search:
{"intent":"search","params":{"name":"rahul"}}

Delete by name:
{"intent":"delete","params":{"name":"jessica"}}

Delete by id:
{"intent":"delete","params":{"id":12}}

Add:
{"intent":"add","params":{"firstname":"rahul","lastname":"vaidya","email":"rahul@gmail.com","phoneNumber":"9876543210"}}

Filter by gender:
{"intent":"filter_gender","params":{"gender":"Male"}}

Show all:
{"intent":"showall","params":{}}

Update phone number:
{"intent":"update","params":{"name":"jessica","updates":{"phoneNumber":"989898"}}}

Update salary:
{"intent":"update","params":{"name":"john","updates":{"salary":90000}}}

Update name:
{"intent":"update","params":{"name":"john","updates":{"firstname":"johnny"}}}

Update email:
{"intent":"update","params":{"email":"old@gmail.com","updates":{"email":"new@gmail.com"}}}

Chitchat:
{"intent":"chitchat","params":{}}

CRITICAL:
- "name" in params root = used to FIND the employee
- "firstname"/"lastname" inside "updates" = used to CHANGE the name
- Phone field is ALWAYS "phoneNumber" - never "phone" or "mobile"
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

    # ✅ Handle confirmation replies
    if state.get("awaiting_confirmation"):
        msg = state["message"].lower().strip()

        if msg in ["yes", "confirm", "ok", "do it", "y"]:
            return "execute"
        elif msg in ["no", "cancel", "stop", "n"]:
            return "cancel"
        else:
            # Unclear reply - ask again
            return "reconfirm"

    # ✅ Route to confirmation first for destructive actions
    if state["intent"] in ["delete", "update"]:
        return "confirm_direct"

    if state["intent"] in ["search", "filter_gender", "add", "showall"]:
        return state["intent"]

    return "chitchat"


# ---------------- CONFIRMATION NODES ---------------- #

def confirm_direct_node(state: AgentState) -> AgentState:
    """Ask user to confirm delete/update"""
    intent = state["intent"]
    params = state["params"]

    # Build a readable confirmation message
    if intent == "delete":
        target = (
            params.get("name") or
            params.get("email") or
            params.get("id") or
            "selected employee"
        )
        msg = f"⚠️ Are you sure you want to DELETE '{target}'? (yes/no)"
    elif intent == "update":
        target = (
            params.get("name") or
            params.get("email") or
            params.get("id") or
            "selected employee"
        )
        updates = params.get("updates", {})
        msg = f"⚠️ Are you sure you want to UPDATE '{target}' with {updates}? (yes/no)"
    else:
        msg = f"⚠️ Confirm {intent}? (yes/no)"

    return {
        **state,
        "botmessage": msg,
        "awaiting_confirmation": True,
        "confirmed": False,
        # ✅ Store the action in params so execute node knows what to do
        "params": {
            **state["params"],
            "_pending_action": intent  # track what action is pending
        }
    }


def reconfirm_node(state: AgentState) -> AgentState:
    """User gave unclear answer"""
    return {
        **state,
        "botmessage": "Please reply with 'yes' to confirm or 'no' to cancel.",
        "awaiting_confirmation": True
    }


def cancel_node(state: AgentState) -> AgentState:
    """User cancelled"""
    return {
        **state,
        "botmessage": "❌ Operation cancelled.",
        "awaiting_confirmation": False,
        "confirmed": False,
        "params": {},
        "apiresult": {}
    }


# ---------------- EXECUTE NODE ---------------- #

async def execute_node(state: AgentState) -> AgentState:
    """Execute confirmed delete/update"""

    params = state["params"]
    action = params.get("_pending_action")

    # Remove internal key before passing to API
    clean_params = {k: v for k, v in params.items() if k != "_pending_action"}

    if not action:
        return {
            **state,
            "botmessage": "❌ No pending action found.",
            "awaiting_confirmation": False,
            "confirmed": False,
            "params": {}
        }

    try:
        if action == "delete":
            res = await delete_employee(**clean_params)

        elif action == "update":
            res = await update_employee(**clean_params)

        else:
            res = {"success": False, "error": f"Unknown action: {action}"}

    except Exception as e:
        res = {"success": False, "error": str(e)}

    return {
        **state,
        "intent": action,        # ✅ restore intent for respond node
        "apiresult": res,
        "awaiting_confirmation": False,
        "confirmed": True,
        "params": {}
    }


# ---------------- BASIC ACTION NODES ---------------- #

async def search_node(state: AgentState) -> AgentState:
    result = await search_employee(state["params"].get("name", ""))
    return {**state, "apiresult": result}


async def filter_gender_node(state: AgentState) -> AgentState:
    result = await filter_gender(state["params"].get("gender", ""))
    return {**state, "apiresult": result}


async def add_node(state: AgentState) -> AgentState:
    # Remove any internal keys
    payload = {k: v for k, v in state["params"].items() if not k.startswith("_")}
    result = await add_employee(payload)
    return {**state, "apiresult": result}


async def showall_node(state: AgentState) -> AgentState:
    result = await showallemployee()
    return {**state, "apiresult": result}


def chitchat_node(state: AgentState) -> AgentState:
    response = llm.invoke([
        SystemMessage(content="You are a helpful HR assistant. Answer conversationally."),
        HumanMessage(content=state["message"])
    ])
    return {
        **state,
        "apiresult": {},
        "botmessage": response.content
    }


# ---------------- RESPONSE NODE ---------------- #

def respond_node(state: AgentState) -> AgentState:
    api = state.get("apiresult", {})
    intent = state.get("intent", "")

    # ✅ Don't overwrite botmessage if already set (cancel/reconfirm)
    if state.get("botmessage") and intent not in ["delete", "update", "search", "add", "filter_gender", "showall"]:
        return state

    if intent == "delete":
        if api.get("success"):
            name = api.get("name", "Employee")
            msg = f"✅ '{name}' has been deleted successfully."
        else:
            error = api.get("error", "Unknown error")
            msg = f"❌ Delete failed: {error}"

    elif intent == "update":
        if api.get("success"):
            name = api.get("name", "Employee")
            msg = f"✅ '{name}' has been updated successfully."
        else:
            error = api.get("error", "Unknown error")
            msg = f"❌ Update failed: {error}"

    elif intent == "add":
        if api.get("success"):
            name = api.get("name", "Employee")
            msg = f"✅ Employee '{name}' added successfully."
        else:
            error = api.get("error", "Unknown error")
            msg = f"❌ Add failed: {error}"

    elif intent == "search":
        count = api.get("count", 0)
        msg = f"🔍 Found {count} employee(s)." if count > 0 else "❌ No employees found."

    elif intent == "filter_gender":
        count = api.get("count", 0)
        msg = f"🔍 Found {count} employee(s)." if count > 0 else "❌ No employees found."

    elif intent == "showall":
        count = api.get("count", 0)
        msg = f"📋 Showing all {count} employees."

    elif intent == "chitchat":
        # Already set by chitchat_node
        return state

    else:
        msg = state.get("botmessage", "Done.")

    return {**state, "botmessage": msg}


# ---------------- BUILD GRAPH ---------------- #

def build_graph():
    graph = StateGraph(AgentState)

    # Add all nodes
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("confirm_direct", confirm_direct_node)
    graph.add_node("execute", execute_node)
    graph.add_node("cancel", cancel_node)
    graph.add_node("reconfirm", reconfirm_node)
    graph.add_node("search", search_node)
    graph.add_node("filter_gender", filter_gender_node)
    graph.add_node("add", add_node)
    graph.add_node("showall", showall_node)
    graph.add_node("chitchat", chitchat_node)
    graph.add_node("respond", respond_node)

    # Entry
    graph.add_edge(START, "classify_intent")

    # Route after classification
    graph.add_conditional_edges(
        "classify_intent",
        route_intent,
        {
            "confirm_direct": "confirm_direct",
            "execute": "execute",
            "cancel": "cancel",
            "reconfirm": "reconfirm",
            "search": "search",
            "filter_gender": "filter_gender",
            "add": "add",
            "showall": "showall",
            "chitchat": "chitchat",
        }
    )

    # Confirmation nodes end (waiting for user reply)
    graph.add_edge("confirm_direct", END)
    graph.add_edge("reconfirm", END)

    # After execute/cancel -> respond -> end
    graph.add_edge("execute", "respond")
    graph.add_edge("cancel", "respond")

    # Basic actions -> respond
    for node in ["search", "filter_gender", "add", "showall", "chitchat"]:
        graph.add_edge(node, "respond")

    graph.add_edge("respond", END)

    return graph.compile(checkpointer=memory)


agent = build_graph()


# ---------------- RUN AGENT ---------------- #

async def run_agent(thread_id: str, message: str):
    config = {"configurable": {"thread_id": thread_id}}

    # ✅ Get existing checkpoint state
    checkpoint = await agent.aget_state(config)

    if checkpoint and checkpoint.values:
        # ✅ RESUME: update only the message in existing state
        existing = checkpoint.values
        input_state = {
            **existing,
            "message": message,  # only update message
        }
    else:
        # ✅ FRESH: no previous state
        input_state = {
            "message": message,
            "intent": "",
            "params": {},
            "apiresult": {},
            "botmessage": "",
            "awaiting_confirmation": False,
            "confirmed": False
        }

    result = await agent.ainvoke(input_state, config=config)

    # ✅ Return employeeid for delete action in frontend
    api_result = result.get("apiresult", {})

    return {
        "action": result.get("intent", ""),
        "botmessage": result.get("botmessage", ""),
        "employees": api_result.get("employees", []),
        "success": api_result.get("success", False),
        "employeeid": api_result.get("employeeid"),    # ✅ for delete
        "awaiting_confirmation": result.get("awaiting_confirmation", False),
    }