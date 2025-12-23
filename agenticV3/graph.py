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
from utils.types import Rider, AgentState, BookingRecord, CancellationEvent, output
from utils.booking_manager import BookingManager
from utils.input_handlers import get_wait_time, get_cancellation_time
from langchain_core.output_parsers.pydantic import PydanticOutputParser
# from langgraph.checkpoint.filesystem import FileSystemSaver
import json

load_dotenv()

# Initialize tools and managers
booking_manager = BookingManager()

# Initialize the model with Groq
model = ChatGroq(
    model_name="gemma2-9b-it",
    temperature=0.7
)

parser = PydanticOutputParser(pydantic_object=output)

system_prompt = SystemMessage(content=f"""
You are a helpful Uber assistant. Respond with one of the following tools based on the user's intent:

1. 'book_ride': When the user wants to book a ride. Include both 'pickup' and 'drop'. Ask for any missing fields before responding.
2. 'cancel_ride': When the user wants to cancel a ride. Include 'booking_id'. Ask for it if missing.
3. 'list_bookings': When the user asks about current bookings.
4. 'answer_query': For general Uber-related questions.
5. 'logout': When the user wants to exit or logout or similar intent expressed

Respond ONLY with the correct JSON structure as follows:
{parser.get_format_instructions()}
""")

def chatbot(state: AgentState)->AgentState:
    response = model.invoke([system_prompt] + state["messages"])
    state["messages"].append(response)
    return state

def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("chatbot",chatbot)

    builder.add_edge(START, "chatbot")
    builder.add_edge("chatbot", END)

    # memory = FileSystemSaver("chatbot_memory_dir")  # Directory to store state files
    graph = builder.compile()
    return graph

agent = build_graph()


















