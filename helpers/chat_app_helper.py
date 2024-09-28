from uuid import uuid4

from chats import chat_service
from database import postgresql_service, pinecone_service


def init_postgresql_db():
    postgresql_service.create_documents_table()
    postgresql_service.create_chat_history_table()


def save_documents_to_dbs(pdf_text, file_name):
    index_name = str(uuid4())

    postgresql_service.insert_documents_row(index_name, file_name)

    documents = pinecone_service.create_pinecone_documents(pdf_text)
    index = pinecone_service.create_index(index_name)
    vector_store = pinecone_service.vector_store_init(index=index)
    pinecone_service.upsert_documents(vector_store, documents)


def init_qa(id):
    index_name = postgresql_service.get_document_by_id(id)[1]
    index = pinecone_service.create_index(index_name)
    vector_store = pinecone_service.vector_store_init(index=index)

    qa = chat_service.get_qa(vector_store)

    return qa


def save_chat_message_to_db(text, is_question, document_id, session_id):
    postgresql_service.insert_chat_history_row(text, is_question, document_id, session_id)
