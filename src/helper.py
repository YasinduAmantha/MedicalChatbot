from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List
from langchain.schema import Document
from langchain.embeddings import HuggingFaceEmbeddings

# Extract text from PDF files
def load_pdf_files(data):
    loader = DirectoryLoader(
        data,
        glob = "*.pdf",
        loader_cls=PyPDFLoader
    )

    documents = loader.load()
    return documents

# filetr souce and the page content
def filter_to_minimal_docs(docs: List[Document]) -> List[Document]:
    """
    Given a list of document objects, return a new list of document objects 
    containing only 'source' in metadata and the original page content.
    """
    minimal_docs: List[Document] = []
    for doc in docs:
        src = doc.metadata.get("source")
        minimal_docs.append(
            Document(
                page_content=doc.page_content,
                metadata={"source": src}
            )
        )
    return minimal_docs

# Split the document into smaller chunks
def text_split(minimal_docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=50
    )
    texts_chunk = text_splitter.split_documents(minimal_docs)
    return texts_chunk

# download the embedding model
def download_embeddings():
    """
    Download and return the hugging face embedding model
    """
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    embeddings = HuggingFaceEmbeddings(
        model_name = model_name
    )
    return embeddings
