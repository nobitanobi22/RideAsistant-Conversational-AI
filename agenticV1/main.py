from utils.langsmith_env import setup_env
from utils.user_manager import UserManager
from graph import build_graph
from langchain_core.messages import SystemMessage, HumanMessage
from utils.handleRegistrations import handle_user_registration

setup_env() ##Set langsmith environment if api key available

# Initialize user manager
user_manager = UserManager()

def main():
    while True:
        print("\n=== Welcome to Uber Chatbot ===")
        print("1. Login")
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
                    "intent": None,
                    "booking_info": None,
                    "cancellation_event": None,
                    "messages": [
                        SystemMessage(content="Welcome to Uber Chatbot! How can I assist you today?")
                    ]
                }

                print("\nAssistant: Welcome to Uber Chatbot! How can I assist you today?")

                while True:
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
                    response = graph.invoke(state)
                    
                    # Print all new messages from the response
                    if response["messages"]:
                        new_messages = response["messages"][len(state["messages"]):]
                        for msg in new_messages:
                            if isinstance(msg, (HumanMessage, SystemMessage)):
                                print(f"\nAssistant: {msg.content}")
                            elif hasattr(msg, 'content'):
                                print(f"\nAssistant: {msg.content}")
                    
                    # Check if user logged out
                    if response.get("intent") == "Logout":
                        print("\nLogged out successfully. Returning to main menu.")
                        break
                    
                    # Update state for next iteration
                    state = response
                
                # Break out of the outer loop if we're logging out
                break
            
        elif choice == "2":
            handle_user_registration()
            
        elif choice == "3":
            print("Thank you for using Uber Chatbot. Goodbye!")
            return
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
