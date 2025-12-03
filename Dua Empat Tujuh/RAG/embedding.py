from sentence_transformers import SentenceTransformer
from fastembed import SparseTextEmbedding
from pypdf import PdfReader
import json
import os
import requests
from qdrant_client import QdrantClient
from qdrant_client.http import models
import uuid

from sentence_transformers import SentenceTransformer
from fastembed import SparseTextEmbedding
from pypdf import PdfReader
import json
import os
import requests
from qdrant_client import QdrantClient
from qdrant_client.http import models
import uuid
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Document

#Define sentence splitter and embedding models
hf_embedding = HuggingFaceEmbedding("lazarusnlp/all-indo-e5-small-v4")
semantic_splitter = semantic_splitter = SemanticSplitterNodeParser(buffer_size=1, breakpoint_percentile_threshold=95, embed_model=hf_embedding)
dense_embedding_model = SentenceTransformer("lazarusnlp/all-indo-e5-small-v4")
sparse_embedding_model = SparseTextEmbedding("Qdrant/bm25")

client_qdrant = QdrantClient(host='172.20.3.3', port=6333)

#Function to read PDF files
def extract_text(filepath):
    _, file_extension = os.path.splitext(filepath)
    file_extension = file_extension.lower()

    text = ""

    if file_extension == '.txt':
        with open(filepath, 'r') as file:
            text = file.read()
    elif file_extension == '.doc' or file_extension == '.docx':
        text = docx2txt.process(filepath)
    elif file_extension == '.ppt' or file_extension == '.pptx':
        text = ''
        prs = pptx.Presentation(filepath)
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text += shape.text + ' '
    elif file_extension == '.pdf':
        with open(filepath, 'rb') as file:
            reader = PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text() + ' '
    else:
        raise ValueError("Unsupported file type")

    return text

#Create collection if not exists 
def create_collection_if_not_exists(collection_name):
    try:
        client_qdrant.get_collection(collection_name=collection_name)
        print(f"Collection '{collection_name}' already exists.")
    except Exception as e:
        print(f"Collection '{collection_name}' not found. Creating a new collection.")
        #2 vectors for each chunk, 1 dense and 1 sparse
        client_qdrant.create_collection(
            collection_name=collection_name,
            vectors_config={
                "dense-lazarusnlp":models.VectorParams(
                    size=384,
                    distance=models.Distance.COSINE
                ),
            },
            sparse_vectors_config={
                "sparse-bm25":models.SparseVectorParams()
            }
        )
        print(f"Collection '{collection_name}' created successfully.")

#Embed file to qdrant
def add_to_qdrant(file_path, collection):
    full_text = extract_text(file_path)

    create_collection_if_not_exists(collection)
    collection_name=collection

    if full_text != "":     
        nodes = semantic_splitter.get_nodes_from_documents([Document(text=full_text)])

        for node in nodes:
            chunk_text=node.get_content()

            filename=os.path.basename(file_path)
            payload = {"chunk": chunk_text, "filename": filename}

            dense_vector = dense_embedding_model.encode(chunk_text)
            sparse_vector = next(sparse_embedding_model.query_embed(chunk_text))
            
            client_qdrant.upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=str(uuid.uuid4()),
                        payload=payload,
                        vector={
                            "dense-lazarusnlp":dense_vector,
                            "sparse-bm25": models.SparseVector(
                                indices=sparse_vector.indices,
                                values=sparse_vector.values
                            )
                        }
                    )
                ]
            )

    return

#Run with
# file_path="/path/to/file/file.pdf"
# add_to_qdrant(file_path, "collection_name")
