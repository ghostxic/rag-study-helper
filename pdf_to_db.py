from print_function import pdf_path_text
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import chromadb

load_dotenv()

def pdf_path_to_chromadb(path: str) -> None:

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
    collection.add(
        ids=[f"{path}_{i}" for i in range(len(content))],
        embeddings=embedding_arrays,
        documents=content
        
    )
    print("Success! Chunks stored: " + str(len(content)))

pdf_path_to_chromadb("test_files/induction_answers.pdf")
pdf_path_to_chromadb("test_files/induction_problems.pdf")