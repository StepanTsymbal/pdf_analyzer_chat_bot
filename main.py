import utils.pdf_service as pdf_service
import database.pinecone_service as pinecone_service
import chats.chat_service_with_session_id as chat_service
import database.postgresql_service as postgresql_service

from uuid import uuid4
import time


# file_path = "drylab.pdf"

# texts = pdf_service.process_pdf(file_path)
# documents = pinecone_service.create_pinecone_documents(texts)

# index_name = str(uuid4())
index_name = '8c0ef590-df3f-4929-b08f-d8f619f09dc5'

# postgresql_service.create_documents_table()
# document_id = postgresql_service.insert_documents_row(index_name, file_path)
document_id = 29

index = pinecone_service.create_index(index_name)

vector_store = pinecone_service.vector_store_init(index=index)

# time.sleep(5)

store = {}
qa_2 = chat_service.get_qa_with_session_id(vector_store)
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
# response = qa_2.invoke(
#     {"input": "show them as table"},
#     config={
#         "configurable": {"session_id": "abc123", "store": store}
#     },  # constructs a key "abc123" in `store`.
# )
# print(response['answer'])
# response = qa_2.invoke(
#     {"input": "who is it?"},
#     config={
#         "configurable": {"session_id": "abc123", "store": store}
#     },  # constructs a key "abc123" in `store`.
# )
# print(response['answer'])