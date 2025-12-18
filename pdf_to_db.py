from print_function import pdf_path_text
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import chromadb
from datetime import datetime
import uuid
from dataclasses import dataclass

load_dotenv()
@dataclass
class All_Data:
    doc_id: str
    filename: str
    num_chunks: int

def pdf_path_to_chromadb(path: str) -> list[dict]:

    content = pdf_path_text(path)
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=content,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT", output_dimensionality=768)
    )
    client = chromadb.CloudClient(
            api_key=os.getenv("CHROMA_API_KEY"),
            tenant=os.getenv("CHROMA_TENANT"),
            database=os.getenv("CHROMA_DATABASE")
        )
    collection = client.get_or_create_collection(name="my_collection")
    # Extract the actual embedding vectors from ContentEmbedding objects
    embedding_arrays = [embedding.values for embedding in result.embeddings]
    
    # Get filename from path
    filename = os.path.basename(path)
    upload_date = datetime.now().isoformat()
    num_chunks = len(content)
    
    # Create metadatas for each chunk
    doc_id = str(uuid.uuid4())
    metadatas = [
        {
            "document_id": doc_id,
            "filename": filename,
            "upload_date": upload_date,
            "total_chunks": num_chunks,
            "chunk_index": i
        }
        for i in range(len(content))
    ]
    
    collection.add(
        ids=[f"{doc_id}_{i}" for i in range(len(content))],
        embeddings=embedding_arrays,
        documents=content,
        metadatas=metadatas
    )

    d = All_Data(doc_id, filename, num_chunks)


    return d