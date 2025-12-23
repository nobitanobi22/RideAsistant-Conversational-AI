from langchain_community.tools import tool
from langchain_tavily import TavilySearch
from dotenv import load_dotenv
load_dotenv()
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from graph import State

# @tool
# def add(a:float, b:float)->float:
#     """This tool adds two numbers"""
#     return a+b

# tavily = TavilySearch(max_results = 2)



from langchain.tools import Tool
from typing import Optional

@tool
def mock_booking_api(inputs: dict) -> str:
    """
    Book a ride for the user.
    The tool requires a pickup location (pickup) and drop location (drop).
    An optional schedule time (schedule) can be provided for future rides. 
    Responds with confirmation, fare, and either ETA or scheduled time.
    """ 
    pickup = inputs.get("pickup")
    drop = inputs.get("drop")
    schedule = inputs.get("schedule")

    if not pickup or not drop:
        return "Booking failed: Please provide both pickup and drop locations."

    if schedule:
        return f"✅ Ride booked from {pickup} to {drop}. Fare: $20, Scheduled Time: {schedule}"
    else:
        return f"✅ Ride booked from {pickup} to {drop}. Fare: $20, ETA: 5 min."

# --- Tracking API Simulator ---
def mock_tracking_api(ride_id: str) -> str:
    if not ride_id:
        return "Tracking failed: Ride ID is missing."
    return f"🛺 Ride {ride_id} is currently 2 km away and approaching your location."

# --- Cancel API Simulator ---
def mock_cancel_api(ride_id: str) -> str:
    if not ride_id:
        return "Cancelation failed: Ride ID is missing."
    return f"🚫 Ride {ride_id} has been canceled. A penalty of $5 has been applied."

# --- Complaint API Simulator ---
def mock_complaint_api(issue: str) -> str:
    if not issue:
        return "Complaint failed: Please describe the issue."
    return f"⚠️ Complaint registered: {issue}. Your ticket number is #12345."

# --- Wrap these as LangChain Tools ---
# booking_tool = Tool.from_function(
#     name="book_ride",
#     func=mock_booking_api,
#     description=(
#         "Book a ride for the user. "
#         "The tool requires a pickup location (pickup) and drop location (drop). "
#         "An optional schedule time (schedule) can be provided for future rides. "
#         "Responds with confirmation, fare, and either ETA or scheduled time."
#     )
# )


# response = mock_booking_api.run({
#     "pickup": "Main Street",
#     "drop": "Airport",
#     "schedule": "6 PM today"
# })
# print(response)


# # # Or without schedule
# # response = booking_tool.run({
# #     "pickup": "Main Street",
# #     "drop": "Airport"
# # })
# # print(response)


# tracking_tool = Tool.from_function(
#     name="track_ride",
#     func=mock_tracking_api,
#     description="Tracks the ride given a ride ID."
# )

# cancel_tool = Tool.from_function(
#     name="cancel_ride",
#     func=mock_cancel_api,
#     description="Cancels the ride given a ride ID."
# )

# complaint_tool = Tool.from_function(
#     name="file_complaint",
#     func=mock_complaint_api,
#     description="Files a complaint given the issue description."
# )

# # --- Collect all tools ---
# TOOLS = [booking_tool, tracking_tool, cancel_tool, complaint_tool]


class BookingInfo(BaseModel):
    pickup: str
    drop: str
    schedule_time: str | None ######### improve by using datetime format later on

def booking_node(state: State): 
    parser = PydanticOutputParser(pydantic_object=BookingInfo)

    booking_prompt = PromptTemplate(
        template = 
    """
    You are a ride booking assistant. Extract the following from the user's message:
    - pickup location
    - drop location
    - schedule_time (if the user specifies a time; otherwise null)

    Respond with ONLY the following JSON — no other text, no code fences, no explanation. If no date is given :
    {format_instructions}

    User message: {input}
    """,
        
        input_variables=["input"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    llm = ChatGroq(model = 'gemma2-9b-it')
    booking_chain = booking_prompt | llm | parser
    booking_info = booking_chain.invoke(state["messages"][-1].content)

    state["booking_info"] = booking_info
    return state


