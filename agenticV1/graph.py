from typing import Annotated, Sequence, TypedDict, Optional, Dict, Any, Literal
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from tools.booking_tool import book_ride
from tools.cancellation_tool import cancel_ride
from tools.chatbot_tool import answer_query
from tools.list_booking_tool import list_bookings
from utils.types import Rider, AgentState, BookingRecord, CancellationEvent
from utils.booking_manager import BookingManager
from utils.input_handlers import get_wait_time, get_cancellation_time
# from langgraph.checkpoint.filesystem import FileSystemSaver

import json

load_dotenv()

# Initialize tools and managers
tools = [book_ride, cancel_ride, list_bookings, answer_query]
booking_manager = BookingManager()

# Initialize the model with Groq
model = ChatGroq(
    model_name="gemma2-9b-it",
    temperature=0.7
).bind_tools(tools)


system_prompt = SystemMessage(content="""
You are a helpful Uber assistant. You have the following tools:

1. book_ride: Call this tool when the user wants to book a ride. 
   You must provide both 'pickup' and 'drop' locations. 
   If either is missing, ask the user for the missing information before calling the tool.

2. cancel_ride: Call this tool when the user wants to cancel a ride. 
   You must provide the 'booking_id'. 
   If it is missing, ask the user for it before calling the tool.

3. list_bookings: Call this tool when the user wants to know about their active bookings.

4. answer_query: Call this tool for general Uber-related questions.

If the user wants to logout, do not call any tools. Just end the session.
""")

def chatbot_with_tools(state: AgentState)->AgentState:
    response = model.invoke([system_prompt] + state["messages"])
    state["messages"].append(response)
    return state

def router(state: AgentState) -> Literal["tools", "__end__"]:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    return "__end__"

def build_graph():
    builder = StateGraph(AgentState)
    
    tool_node = ToolNode(tools)
    builder.add_node("chatbot_with_tools",chatbot_with_tools)
    builder.add_node("tools", tool_node)

    builder.add_edge(START, "chatbot_with_tools")
    builder.add_conditional_edges("chatbot_with_tools", router)
    builder.add_edge("tools", "chatbot_with_tools")

    # memory = FileSystemSaver("chatbot_memory_dir")  # Directory to store state files
    graph = builder.compile()
    return graph





























# def model_call(state: AgentState) -> AgentState:
#     rider = state.get("rider")
#     last_message = state["messages"][-1]

#     # Updated system prompt with list_bookings tool
#     system_prompt = SystemMessage(content=f"""
# You are an Uber assistant. Use these tools:
# - book_ride: Needs pickup, drop.
# - cancel_ride: Needs booking_id only; the system will prompt for other details.
# - list_bookings: Shows your current active bookings.
# - answer_query: For questions about Uber services or policies.

# End the session if the user says exit, logout, or bye. Respond with "logout"
# """ + (f"\nActive bookings: {[f'ID: {b.booking_id}' for b in booking_manager.get_rider_bookings(rider.rider_id)]}" if rider else ""))

#     response = model.invoke([system_prompt] + state["messages"])

#     # Example: Look for an intent marker in the LLM's response
#     if hasattr(response, "content") and "logout" in response.content.lower():
#         state["intent"] = "Logout"

#     state["messages"] = state["messages"] + [response]
#     return state

# def should_continue(state: AgentState) -> str:
#     """Determine if we should continue processing or end the conversation."""
#     if state.get("intent") == "Logout":
#         return "end"
        
#     messages = state["messages"]
#     last_message = messages[-1]
    
#     # Check if the last message has tool calls
#     if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
#         return "end"
    
#     return "continue"

# def build_graph():
#     """Build the conversation graph."""
#     # Initialize the graph
#     graph = StateGraph(AgentState)
    
#     # Add nodes
#     graph.add_node("agent", model_call)
#     tool_node = ToolNode(tools=tools)
#     graph.add_node("tools", tool_node)
    
#     # Set entry point
#     graph.set_entry_point("agent")
    
#     # Add conditional edges
#     graph.add_conditional_edges(
#         "agent",
#         should_continue,
#         {
#             "continue": "tools",
#             "end": END,
#         },
#     )
    
#     # Add edge from tools back to agent
#     graph.add_edge("tools", "agent")
    
#     # Compile the graph with MemorySaver
#     memory = FileSystemSaver("chatbot_memory_dir")  # Directory to store state files
#     return graph.compile(checkpointer=memory)

# # Create the application
# app = build_graph()





