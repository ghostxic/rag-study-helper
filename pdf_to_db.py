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

    # Process content in batches of 100 (API limit)
    batch_size = 100
    all_embeddings = []
    
    for i in range(0, len(content), batch_size):
        batch_content = content[i:i + batch_size]
        
        result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=batch_content,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT", output_dimensionality=768)
        )
        
        # Extract embeddings from this batch
        batch_embeddings = [embedding.values for embedding in result.embeddings]
        all_embeddings.extend(batch_embeddings)
    
    client = chromadb.CloudClient(
            api_key=os.getenv("CHROMA_API_KEY"),
            tenant=os.getenv("CHROMA_TENANT"),
            database=os.getenv("CHROMA_DATABASE")
        )
    collection = client.get_or_create_collection(name="my_collection")
    
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
        embeddings=all_embeddings,
        documents=content,
        metadatas=metadatas
    )

    d = All_Data(doc_id, filename, num_chunks)

    return d