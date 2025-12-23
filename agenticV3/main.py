from utils.langsmith_env import setup_env
from utils.user_manager import UserManager
from graph import build_graph
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from utils.handleRegistrations import handle_user_registration
from tools.booking_tool import book_ride
from tools.cancellation_tool import cancel_ride
from tools.chatbot_tool import answer_query
from tools.list_booking_tool import list_bookings
import json
import re


setup_env() ##Set langsmith environment if api key available

# Initialize user manager as a global instance
user_manager = UserManager()

def main():
    while True:
        print("\n=== Welcome to Uber Chatbot ===")
        print("1. User login")
        print("2. Register")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == "1":
            rider_id = input("Enter User ID: ").strip()
            rider_password = input("Enter password: ").strip()

            rider = user_manager.authenticate_rider(rider_id, rider_password)
            
            if not rider:
                print("Invalid credentials. Please try again or register.")
                continue

            # Start a new session
            while True:
                state = {
                    "rider": rider,
                    "booking_info": None,
                    "cancellation_event": None,
                    "messages": [
                        SystemMessage(content="Welcome to Uber Chatbot! How can I assist you today?")
                    ],
                    "memory": {}
                }

                print("\nAssistant: Welcome to Uber Chatbot! I am equiped with utilities to book or cancel a ride, list your active bookings, and general questions related to Uber. How can I assist you today? ")

                while True:
                    # State will be expected to have cancellation_event of CancellationEvent class but if a cancellation was made previously then it will be of CancellationRecord type
                    state['cancellation_event'] = None

                    # Get user input
                    try:
                        user_input = input("\nYou: ").strip()
                    except KeyboardInterrupt:
                        print("\nLogged out successfully. Returning to main menu.")
                        break
                        
                    if not user_input:
                        continue
                    
                    # Add user message to state
                    state["messages"].append(HumanMessage(content=user_input))

                    # Process through graph
                    graph = build_graph()
                    # config = {"configurable": {"thread_id": rider.rider_id}}
                    response = graph.invoke(state)
                    content = response['messages'][-1].content

                    # Remove Markdown code block if present
                    if content.strip().startswith("```"):
                        # This regex extracts the content between ```json and ```
                        match = re.search(r"```(?:json)?\\n?(.*)```", content, re.DOTALL)
                        if match:
                            json_str = match.group(1).strip()
                        else:
                            # fallback: remove all backticks and 'json'
                            json_str = content.replace("```json", "").replace("```", "").strip()
                    else:
                        json_str = content.strip()

                    response_dict = json.loads(json_str)
                    # print(response_dict)
                    tool_call = response_dict.get("tool_call")

                    if tool_call == "book_ride":
                        pickup = response_dict.get("pickup")
                        drop = response_dict.get("drop")
                        if pickup and drop:
                            bookingRecord = book_ride.invoke({"pickup": pickup, "drop": drop, "state": response})
                            response['booking_info'] = bookingRecord
                            if bookingRecord:
                                ai_message = AIMessage(content=f"Ride booked from {pickup} to {drop}. Booking ID: {bookingRecord.booking_id}")
                                response["messages"].append(ai_message)
                            else: 
                                ai_message = AIMessage(content="Booking failed")
                                response["messages"].append(ai_message)
                        else:
                            ai_message = AIMessage(content="Please provide both pickup and drop locations to book a ride")
                            response["messages"].append(ai_message)

                    elif tool_call == "cancel_ride":
                        booking_id = response_dict.get("booking_id")
                        if booking_id:
                            cancelRecord = cancel_ride.invoke({"booking_id": booking_id, "state": response})
                            response['cancellation_event'] = cancelRecord

                            if cancelRecord:
                                # Convert all fields to a readable format
                                details_lines = [f"{key.replace('_', ' ').capitalize()}: {value}" for key, value in cancelRecord.model_dump().items()]
                                details_text = "\n".join(details_lines)

                                # Create and append the AI message
                                ai_message = AIMessage(
                                    content=(
                                        f"Ride with Booking ID {booking_id} has been cancelled.\n"
                                        f"Cancellation fee decision: {cancelRecord.decision}.\n\n"
                                        f"Details of Cancellation:\n{details_text}"
                                    )
                                )
                                response["messages"].append(ai_message)
                            else: 
                                ai_message = AIMessage(content="Cancellation failed")
                                response["messages"].append(ai_message)
                        else:
                            ai_message = AIMessage(content="Please provide booking id of the ride you want to cancel")
                            response["messages"].append(ai_message)

                    elif tool_call == "list_bookings":
                        activeBookings = list_bookings.invoke({"state": response})

                        if activeBookings:
                            ai_message = AIMessage(content=f"Here are your active bookings:\n{activeBookings}")
                            response["messages"].append(ai_message)
                        else:
                            ai_message = AIMessage(content="No active bookings")
                            response["messages"].append(ai_message)

                    elif tool_call == "answer_query":
                        queryResponse = answer_query.invoke({"query": user_input})

                        ai_message = AIMessage(content=queryResponse)
                        response["messages"].append(ai_message)

                    elif tool_call == "logout":
                        ai_message = AIMessage(content="Logged out successfully. Returning to main menu.")
                        response["messages"].append(ai_message)
                        print("\nLogged out successfully. Returning to main menu.")
                        break

                    # Print only the latest AI response from the updated state
                    latest_msg = response["messages"][-1]
                    content = getattr(latest_msg, 'content', None)
                    if content:
                        print(f"\nAssistant: {content}")

                    # Update state for next iteration
                    state = response
                
                # Break out of the outer loop if we're logging out
                break
            
        elif choice == "2":
            # Pass the global user_manager instance to the registration function
            handle_user_registration(user_manager)
            
        elif choice == "3":
            print("Thank you for using Uber Chatbot. Goodbye!")
            return
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()