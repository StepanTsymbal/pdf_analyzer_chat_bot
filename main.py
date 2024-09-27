import utils.pdf_service as pdf_service
import database.pinecone_service as pinecone_service
import chats.chat_service as chat_service
import database.postgresql_service as postgresql_service

from uuid import uuid4
import time


file_path = "drylab.pdf"

# texts = pdf_service.process_pdf(file_path)
# documents = pinecone_service.create_pinecone_documents(texts)

# index_name = str(uuid4())
index_name = '632efe90-1f08-46ad-b4c7-efc5202210b3'

# postgresql_service.create_documents_table()
# document_id = postgresql_service.insert_documents_row(index_name, file_path)
document_id = 29

index = pinecone_service.create_index(index_name)

vector_store = pinecone_service.vector_store_init(index=index)
# pinecone_service.upsert_documents(vector_store, documents)

# time.sleep(5)

# query = "helped anonymize names in the process"
# response = vector_store.similarity_search(query)
# print(response)

# qa = chat_service.get_qa(vector_store)

# postgresql_service.create_chat_history_table()

# query = 'count these people'
# postgresql_service.insert_chat_history_row(query, True, document_id)
# response = qa.invoke(query)
# print(response)
# postgresql_service.insert_chat_history_row(response['result'], False, document_id)
# print(response)

# query = 'list new owners'
# postgresql_service.insert_chat_history_row(query, True, document_id)
# response = qa.invoke(query)
# postgresql_service.insert_chat_history_row(response['result'], False, document_id)
# print(response)

# query = 'count these people'
# postgresql_service.insert_chat_history_row(query, True, document_id)
# response = qa.invoke(query)
# postgresql_service.insert_chat_history_row(response['result'], False, document_id)
# print(response)


# qa_old = chat_service.get_qa_old(vector_store)
# response = qa_old.invoke({"question": "count these people"})
# print(f"{response['chat_history']}\n")
# response = qa_old.invoke({"question": "list new owners"})
# print(f"{response['chat_history']}\n")
# response = qa_old.invoke({"question": "count these people"})
# print(f"{response['chat_history']}\n")

store = {}
qa_2 = chat_service.get_qa_2(vector_store)
response = qa_2.invoke(
    {"input": "count these people"},
    config={
        "configurable": {"session_id": "abc123", "store": store}
    },  # constructs a key "abc123" in `store`.
)
print(response['answer'])
response = qa_2.invoke(
    {"input": "list new owners"},
    config={
        "configurable": {"session_id": "abc123", "store": store}
    },  # constructs a key "abc123" in `store`.
)
print(response['answer'])
response = qa_2.invoke(
    {"input": "count these people"},
    config={
        "configurable": {"session_id": "abc123", "store": store}
    },  # constructs a key "abc123" in `store`.
)
print(response['answer'])
response = qa_2.invoke(
    {"input": "show them as table"},
    config={
        "configurable": {"session_id": "abc123", "store": store}
    },  # constructs a key "abc123" in `store`.
)
print(response['answer'])
response = qa_2.invoke(
    {"input": "who is it?"},
    config={
        "configurable": {"session_id": "abc123", "store": store}
    },  # constructs a key "abc123" in `store`.
)
print(response['answer'])