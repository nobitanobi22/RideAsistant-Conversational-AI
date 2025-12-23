from utils.types import State
from RAG.RAG import chain
from langchain_core.messages import AIMessage, HumanMessage

def chatbot_node(state: State) -> State:
    # Get the user's actual query
    user_query = input("Please ask your question: ")
    state["messages"].append(HumanMessage(content=user_query))
    
    # Process through RAG
    response = chain.invoke(user_query)
    state["messages"].append(AIMessage(content=response.content))
    return state