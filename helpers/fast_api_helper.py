import os
# import tempfile
from uuid import uuid4

from PyPDF2 import PdfReader
# from langchain_community.document_loaders import PyPDFLoader

from database import pinecone_service, postgresql_service
# from utils import pdf_service
from chats import chat_service_with_chat_history


def init():
    postgresql_service.create_documents_table()
    postgresql_service.create_chat_history_table()


def get_all_documents():
    documents = postgresql_service.get_all_documents()

    return [{"id": document[0], "uuid": document[1], "name": document[2]} for document in documents]


# async def index_doc(file):
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
#         content = await file.read()
#         temp_file.write(content)
#         temp_file_path = temp_file.name
#
#     loader = PyPDFLoader(temp_file_path)
#     data = loader.load()
#     pdf_text = pdf_service.process_data(data)
#
#     index_name = str(uuid4())
#
#     postgresql_service.insert_documents_row(index_name, file.filename)
#     documents = pinecone_service.create_pinecone_documents(pdf_text)
#     index = pinecone_service.create_index(index_name)
#     vector_store = pinecone_service.vector_store_init(index=index)
#     pinecone_service.upsert_documents(vector_store, documents)


async def process_and_upload_to_pinecone(file_path: str, file_name: str, index_name: str = None):
    CHUNK_SIZE = 1024 * 1024
    if not index_name: index_name = str(uuid4())
    # postgresql_service.insert_documents_row(index_name, file_name)
    index = pinecone_service.create_index(index_name)
    vector_store = pinecone_service.vector_store_init(index=index)

    # try:
    with open(file_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        chunks = []

        for page in pdf_reader.pages:
            text = page.extract_text()
            chunks.extend([text[i:i+CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)])

        documents = pinecone_service.create_pinecone_documents(chunks)
        pinecone_service.upsert_documents(vector_store, documents)

    postgresql_service.insert_documents_row(index_name, file_name)

    os.remove(file_path)


def process_question(chat):
    index_name = postgresql_service.get_document_by_id(chat.DocId)[1]
    index = pinecone_service.create_index(index_name)
    vector_store = pinecone_service.vector_store_init(index=index)
    chat_history = chat_service_with_chat_history.get_ai_history(chat.History)
    question = chat.Question

    postgresql_service.insert_chat_history_row(question, True, chat.DocId, '-')

    qa = chat_service_with_chat_history.get_qa_with_chat_history(vector_store)

    response = qa.invoke({"input": question, "chat_history": chat_history})

    postgresql_service.insert_chat_history_row(response['answer'], False, chat.DocId, '-')

    return response
