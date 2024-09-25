
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


def process_pdf(file_path, chunk_size=1000, chunk_overlap=10):
    loader = PyPDFLoader(file_path)
    data = loader.load()

    return process_data(data, chunk_size=chunk_size, chunk_overlap=chunk_overlap)


def process_data(data, chunk_size=1000, chunk_overlap=10):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    documents = text_splitter.split_documents(data)
    texts = [str(doc) for doc in documents]

    return texts

