import os
from uuid import uuid4
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore


PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
MODEL = "text-embedding-ada-002"

pc = Pinecone(api_key=PINECONE_API_KEY)
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


def vector_store_init(index, model=MODEL):
    embedding = OpenAIEmbeddings(model=model)
    vector_store = PineconeVectorStore(index=index, embedding=embedding)

    return vector_store


