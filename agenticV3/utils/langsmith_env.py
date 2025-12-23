import os

def setup_env():
    if not os.getenv("LANGSMITH_API_KEY"):
        print("⚠️ Warning: LANGSMITH_API_KEY not set. LangChain tracing may not work.")
    else:
        os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGSMITH_API_KEY")

    os.environ["LANGCHAIN_PROJECT"] = "UberChatbot"
    os.environ["LANGCHAIN_TRACING_V2"] = "true"