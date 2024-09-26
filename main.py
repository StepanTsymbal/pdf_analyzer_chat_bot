import utils.pdf_service as pdf_service
import pine_cone.pinecone_service as pinecone_service
import chats.chat_service as chat_service


index_name = "python-index--test-2"

file_path = "drylab.pdf"

texts = pdf_service.process_pdf(file_path)
# embeddings = pinecone_service.create_embeddings(texts)
documents = pinecone_service.create_pinecone_documents(texts)

index = pinecone_service.create_index(index_name)
# pinecone_service.upsert_embeddings(index, embeddings)

vector_store = pinecone_service.vector_store_init(index=index)
# pinecone_service.upsert_documents(vector_store, documents)

# query = "helped anonymize names in the process"
# response = vector_store.similarity_search(query)
# print(response)

qa = chat_service.get_qa(vector_store)

query = 'list New owners'
print(qa.invoke(query)['result'])
query = 'count them and show as table'
print(qa.invoke(query)['result'])
