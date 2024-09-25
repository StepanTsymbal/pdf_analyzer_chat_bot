import os
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI


PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
MODEL = "text-embedding-ada-002"
# index_name = "python-index"

pc = Pinecone(api_key=PINECONE_API_KEY)
# index = pc.Index(name=index_name)

client = OpenAI()


def create_index(index_name, dimension=1536, metric="cosine", cloud='aws', region='us-east-1'):
    if not pc.has_index(index_name):
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


def create_embeddings(texts, model=MODEL):
    embeddings_list = []
    for text in texts:
        res = client.embeddings.create(input=[text], model=model)
        embeddings_list.append(res.data[0].embedding)

    return embeddings_list


def upsert_embeddings(index, embeddings, ids):
    index.upsert(vectors=[(id, embedding) for id, embedding in zip(ids, embeddings)])


def get_ids(file_path, embeddings):
    ids = []
    i = 0

    for embedding in embeddings:
        ids.append(file_path + '_' + str(i))
        i += 1

    return ids

