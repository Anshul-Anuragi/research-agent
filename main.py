import os
import sys
import uuid
from datetime import datetime
from typing import Annotated, TypedDict
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

# Load API keys from .env
load_dotenv()

# ====================== TOOLS (Online APIs) ======================
# 1. Tavily - Online web search (best for agents)
search_tool = TavilySearch(max_results=5)

# 2. Wikipedia - Online knowledge base
wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(top_k_results=2))

# 3. Current date
@tool
def get_current_date() -> str:
    """Returns today's date so the agent knows what is recent."""
    return datetime.now().strftime("%Y-%m-%d")

# 4. Save report locally
@tool
def save_report(filename: str, content: str) -> str:
    """Save the final research report as a Markdown file."""
    os.makedirs("reports", exist_ok=True)
    # Clean filename
    if not filename.endswith(".md"):
        filename += ".md"
    path = os.path.join("reports", filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"✅ Report saved successfully at: {path}"

tools = [search_tool, wikipedia, get_current_date, save_report]
tool_node = ToolNode(tools)

# ====================== STATE ======================
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    topic: str

# ====================== LLM with Resilient Fallbacks ======================
# Gemini Free Tier models have low daily rate limits (e.g. 20 requests/day).
# Using with_fallbacks ensures automatic failover if a model hits 429 (quota) or 503 (high demand).
candidate_models = [
    "gemini-3.5-flash-lite",
    "gemini-3-flash-preview",
    "gemini-3.8-flash",
    "gemini-3.5-flash",
]
preferred_model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
if preferred_model in candidate_models:
    candidate_models.remove(preferred_model)
model_order = [preferred_model] + candidate_models

llm_instances = [
    ChatGoogleGenerativeAI(
        model=m,
        max_retries=1,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    ).bind_tools(tools)
    for m in model_order
]
# Bind tools and attach fallback models
llm = llm_instances[0].with_fallbacks(llm_instances[1:])

# ====================== AGENT NODE ======================
def agent_node(state: AgentState):
    system_prompt = f"""You are an expert research agent.

Topic to research: {state['topic']}

Steps you must follow:
1. Call get_current_date first.
2. Use tavily_search and wikipedia to gather up-to-date and reliable information.
3. Collect information from multiple sources.
4. When you have enough good information, write a clear Markdown report.
5. Finally call save_report with a good filename and the full report content.

Report structure:
# Title
## Executive Summary
## Key Findings
## Detailed Analysis
## Trends & Outlook
## Sources
"""
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END

# ====================== BUILD THE GRAPH ======================
workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
workflow.add_edge("tools", "agent")

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# ====================== RUN FUNCTION ======================
def format_message_content(content) -> str:
    """Helper to convert string or list-of-parts content into readable text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = []
        for part in content:
            if isinstance(part, dict) and "text" in part:
                texts.append(part["text"])
            elif isinstance(part, str):
                texts.append(part)
        return "\n".join(texts)
    return str(content)

def run_agent(topic: str, thread_id: str | None = None):
    print(f"\n🚀 Starting research on: {topic}")
    print("=" * 60)
    
    # Use a unique thread ID per session so previous conversations don't bleed into new topics
    if not thread_id:
        thread_id = f"research-{uuid.uuid4().hex[:8]}"
        
    config = {"configurable": {"thread_id": thread_id}}
    
    result = app.invoke(
        {
            "messages": [HumanMessage(content=f"Please research this topic thoroughly: {topic}")],
            "topic": topic
        },
        config=config
    )
    
    print("\n✅ Agent finished!")
    print("=" * 60)
    
    for msg in result["messages"][-5:]:
        content = getattr(msg, "content", None)
        if content:
            role = getattr(msg, "type", "message")
            print(f"[{role.upper()}]:")
            print(format_message_content(content))
            print("-" * 40)

# ====================== START ======================
if __name__ == "__main__":
    # Allows passing topic as command line argument or defaults to sample topic
    target_topic = sys.argv[1] if len(sys.argv) > 1 else "Current state of AI Agents in 2026"
    run_agent(target_topic)
