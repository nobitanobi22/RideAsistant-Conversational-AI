from langchain.tools import tool
from RAG.RAG import chain

@tool
def answer_query(query: str) -> str:
    """Answer questions about Uber services and policies.

    Args:
        query: Question about Uber (e.g. "How do refunds work?")

    Returns:
        Brief answer to the question (max 3 sentences)
    """
    try:
        result = chain.invoke(query)
        return result.content
    except:
        return "I don't know the answer to that question." 

 