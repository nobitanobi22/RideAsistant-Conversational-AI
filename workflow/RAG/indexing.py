from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import faiss
import os

class Indexing:
    def __init__(self, embedding_model_name="sentence-transformers/all-MiniLM-L6-v2", chunk_size=1000, chunk_overlap=200):
        self.embedding_function = HuggingFaceEmbeddings(model_name=embedding_model_name)
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    def load_pdfs_as_single_document(self, directory_path):
        pdf_docs = {}
        
        for filename in os.listdir(directory_path):
            if filename.lower().endswith(".pdf"):
                file_path = os.path.join(directory_path, filename)
                loader = PyPDFLoader(file_path)
                pages = loader.load()
                
                # Combine all page contents
                full_text = "\n".join([page.page_content for page in pages])
                
                # Create a single Document
                merged_doc = Document(
                    page_content=full_text,
                    metadata={"source": filename}
                )
                
                pdf_docs[filename] = merged_doc
        
        return pdf_docs

    def split_pdf_documents(self, pdf_documents):
        all_chunks = []
        
        for filename, document in pdf_documents.items():
            chunks = self.splitter.split_documents([document])
            
            for chunk in chunks:
                chunk.metadata["source"] = filename
                chunk.page_content = f"Source: {filename}\n" + chunk.page_content
            
            all_chunks.extend(chunks)
        
        return all_chunks

    def create_vector_store(self, chunks):
        return FAISS.from_documents(chunks, self.embedding_function)
    

indexer = Indexing()

# Step 1: Load PDFs
pdf_documents = indexer.load_pdfs_as_single_document("Resources for Uber Rider Help Chatbot/Pdf's")

# Step 2: Split into chunks
chunks = indexer.split_pdf_documents(pdf_documents)

# Step 3: Create FAISS vector store
vector_store = indexer.create_vector_store(chunks)
vector_store.save_local(folder_path = 'RAG/vector_store')
