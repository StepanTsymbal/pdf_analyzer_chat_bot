import os
from uuid import uuid4
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore


PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
MODEL = "text-embedding-ada-002"
# index_name = "python-index"

pc = Pinecone(api_key=PINECONE_API_KEY)
# index = pc.Index(name=index_name)

client = OpenAI()


def create_index(index_name, dimension=1536, metric="cosine", cloud='aws', region='us-east-1'):
    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
    if index_name not in existing_indexes:
    # if not pc.has_index(index_name):
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric=metric,
            spec=ServerlessSpec(
                cloud=cloud,
                region=region
            )
        )

    return pc.Index(name=index_name)


def create_pinecone_documents(texts):
    documents = []
    for text in texts:
        documents.append(Document(page_content=text))

    return documents


def upsert_documents(vector_store, documents):
    uuids = [str(uuid4()) for i in range(len(documents))]
    res = vector_store.add_documents(documents=documents, ids=uuids)
    # print('res:', res)


def vector_store_init(index, model=MODEL):
    embedding = OpenAIEmbeddings(model=model)
    vector_store = PineconeVectorStore(index=index, embedding=embedding)

    return vector_store


# def create_embeddings(texts, model=MODEL):
#     embeddings_list = []
#     for text in texts:
#         res = client.embeddings.create(input=[text], model=model)
#         embeddings_list.append(res.data[0].embedding)
#
#     return embeddings_list
#
#
# def upsert_embeddings(index, embeddings):
#     # metadata = {'text': 'text'}
#     vectors = [(str(uuid4()), embedding) for embedding in embeddings]
#     index.upsert(vectors)
#     # index.upsert(vectors=[(id, embedding) for id, embedding in zip(ids, embeddings)])


# def get_ids(file_path, embeddings):
#     ids = []
#     i = 0
#
#     for embedding in embeddings:
#         ids.append(file_path + '_' + str(i))
#         i += 1
#
#     return ids

