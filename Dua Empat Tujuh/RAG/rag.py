from sentence_transformers import SentenceTransformer
from fastembed import SparseTextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain.chat_models import init_chat_model

client_qdrant = QdrantClient(host='localhost', port=6333)

dense_embedding_model = SentenceTransformer("lazarusnlp/all-indo-e5-small-v4")
sparse_embedding_model = SparseTextEmbedding("Qdrant/bm25")
    

#Retrieval using hybrid vectors and RRF reranking
def search_in_qdrants_rrf(query_text, collection_name):
    dense_query = dense_embedding_model.encode(query_text)
    sparse_query = next(sparse_embedding_model.query_embed(query_text))

    search_results=client_qdrant.query_points(
        collection_name=collection_name,
        prefetch=[
            models.Prefetch(
                query=dense_query,
                using="dense-lazarusnlp",
                limit=25
            ),
            models.Prefetch(
                query=models.SparseVector(indices=sparse_query.indices, values=sparse_query.values),
                using="sparse-bm25",
                limit=25
            )
        ],
        query=models.FusionQuery(fusion=models.Fusion.RRF),
        limit=5,
        timeout=10000
    )

    return search_results

system_message_advanced = (
    "Kamu adalah chatbot bernama yang sudah dikembangkan selama 5 tahun terakhir,"
    "Kamu akan menerima beberapa pasangan nama_document dan text."
    "Jawablah pertanyaan user dengan metode Retrieval Augmented Generation, di mana kamu mengambil dokumen dari database, dan mendasarkan jawaban dengan isi dokumen tersebut."
    "Boleh jawab dengan bulletpoint atau paragraf biasa, tergantung format yang mana yang lebih sesuai."
)

llm = init_chat_model(
    model="gpt-4o-mini",
    api_key="OPEN_AI_API_KEY"
)

def rag_response(user_input, collection_name):
    response_qdrant=search_in_qdrants_rrf(user_input,collection_name)

    if response_qdrant:
        document_list = []

        valid_qdrant_response = []

        for result in response_qdrant.points :
            doc_name = result.payload['filename']

            if doc_name not in document_list :
                document_list.append(doc_name)

            if result.score > 0.2 :
                text = result.payload['chunk'].replace("\n","")[:2000]
                doc_name = result.payload['filename']

                collected_valid_response = f"\n\nDocument Name: {doc_name} ; text : {text}"
                valid_qdrant_response.append(collected_valid_response)

        if len(valid_qdrant_response) > 0:
            valid_qdrant_response_str = " =====\n\n ".join(valid_qdrant_response)
            document_list_str = "<br>".join(document_list)                  

            prompt_advanced = []
            prompt_advanced.append({"role": "system", "content": system_message_advanced })
            prompt_advanced.append({"role": "user", "content": f"Jawablah query dari user: {user_input}. Hanya kalau relevan, boleh menggunakan konteks dari hasil retrieve augmented generation document_name - text sebagai berikut: {valid_qdrant_response_str}. Jangan memberikan penjelasan berulang-ulang hal yang sama"})

    resp = llm.invoke(input=prompt_advanced).content

    return resp

#Run RAG chatbot
# rag_response("Query?", "collection_name")
