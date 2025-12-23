from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition
from agents.booking import booking_node
from agents.cancellations import cancel_node
from agents.chatbot import chatbot_node
from utils.types import State
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

def greetings(state: State):
    # Add system message for context
    if not state["messages"]:
        state["messages"].append(
            SystemMessage(content="This is an Uber assistance chatbot that can help with bookings, cancellations, and general queries.")
        )
    
    user_input = input("Hey! What can I help you with?\n1. Booking\n2. Cancel\n3. Something Else\n4. Logout\n")
    state["messages"].append(HumanMessage(content=user_input))
    return state

def router_node(state: State):
    state = greetings(state)
    user_input = state["messages"][-1].content
    if "Booking" in user_input or "1" in user_input:
        state["intent"] = "Booking"
        state["messages"].append(
            SystemMessage(content="Switching to booking flow.")
        )
    elif "Cancel" in user_input or "2" in user_input:
        state["intent"] = "Cancel"
        state["messages"].append(
            SystemMessage(content="Switching to cancellation flow.")
        )
    elif "Something Else" in user_input or "3" in user_input:
        state["intent"] = "Direct to Chatbot"
        state["messages"].append(
            SystemMessage(content="Switching to general assistance. Feel free to ask any question.")
        )
    elif "Logout" in user_input or "4" in user_input:
        state["intent"] = "Logout"
        state["messages"].append(
            AIMessage(content="Logging out. Thank you for using Uber Chatbot!")
        )
    else:
        state["intent"] = "Invalid Response"
        state["messages"].append(
            AIMessage(content="Invalid option. Please select 1 for Booking, 2 for Cancel, 3 for Something Else, or 4 to Logout.")
        )
    return state

def router_conditions(state: State):
    intent = state["intent"]
    if intent == "Booking":
        return "booking_node"
    elif intent == "Cancel":
        return "cancel_node"
    elif intent == "Direct to Chatbot":
        return "chatbot_node"
    elif intent == "Logout":
        return END
    else:
        return "router_node"

def build_graph():
    graph = StateGraph(State)
    
    # Add nodes
    graph.add_node("router_node", router_node)
    graph.add_node("booking_node", booking_node)
    graph.add_node("cancel_node", cancel_node)
    graph.add_node("chatbot_node", chatbot_node)

    # Add edges
    graph.add_edge(START, "router_node")
    graph.add_conditional_edges("router_node", router_conditions)
    
    # Add edges back to router from each operation node
    graph.add_edge("booking_node", "router_node")
    graph.add_edge("cancel_node", "router_node")
    graph.add_edge("chatbot_node", "router_node")

    return graph.compile()

agent = build_graph()





