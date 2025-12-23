from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnableLambda, RunnablePassthrough
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
load_dotenv()

# Load back
embeddings = HuggingFaceEmbeddings(model_name = "sentence-transformers/all-MiniLM-L6-v2")
faiss_index = FAISS.load_local("RAG/vector_store", embeddings, allow_dangerous_deserialization=True)

retriever = faiss_index.as_retriever(search_type = 'similarity', search_kwargs = {'k': 3})
retriever

def format_docs(retrieved_docs):
    context = "\n\n".join(doc.page_content for doc in retrieved_docs)
    return context

llm = ChatGroq(model='gemma2-9b-it')

prompt = PromptTemplate(
    template = """
    You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.

    Question: {question} 
    Context: {context} 

    Answer:
    """,
    input_variables = ['context', 'question']
)

parallel_chain = RunnableParallel({
    'context': retriever | RunnableLambda(format_docs),
    'question': RunnablePassthrough()
})

chain = parallel_chain | prompt | llm

# response = chain.invoke('I had an issue with a co-rider')
# response.pretty_print()