from qdrant_client import QdrantClient,models
import uuid

client = QdrantClient(url="http://qdrant:6333")

if client.collection_exists("test"):
    pass
else:
    client.create_collection(
        collection_name="test",
        vectors_config=models.VectorParams(size=3072, distance=models.Distance.COSINE),
    )

from google.genai import Client, types

google_client = Client(api_key="API_KEY")

texts = [
    "Qdrant is a vector database that is compatible with Gemini.",
    "Gemini is a family of natively multimodal, large language models (LLMs).",
]

def qdrant_upload(text):

    result = google_client.models.embed_content(
        model="gemini-embedding-2-preview",
        contents=text,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
    )
    
    client.upsert(
        collection_name="test",
         points=[
            models.PointStruct(
                id=str(uuid.uuid4()),
                payload={
                "text": text,
                },
                vector=result.embeddings[0].values
            )
        ]
    )

    return

# for text in texts:
#     qdrant_upload(text)

def qdrant_retrieve(query):
    result = google_client.models.embed_content(
        model="gemini-embedding-2-preview",
        contents=query,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
    )
     
    queried_points = client.query_points(
        collection_name="test",
        query=result.embeddings[0].values,
        search_params=models.SearchParams(hnsw_ef=128, exact=False),
        limit=3,
    )

    return queried_points
