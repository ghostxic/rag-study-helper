from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
from LLM_prompt_test import prompt_test
import chromadb

load_dotenv()

def question_to_embedding(question: str) -> list[str]:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=question,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY", output_dimensionality=768)
    )
    return result.embeddings[0].values

def embedding_to_chunks(embedding: list[str]) -> dict:
    client = chromadb.CloudClient(
            api_key=os.getenv("CHROMA_API_KEY"),
            tenant=os.getenv("CHROMA_TENANT"),
            database=os.getenv("CHROMA_DATABASE")
        )
    collection = client.get_or_create_collection(name="my_collection")
    result = collection.query(
        query_embeddings=embedding,
        n_results=5
    )
    return result

## Debugging for these methods
# question = ""
# embedding = question_to_embedding(question)
# chunks = embedding_to_chunks(embedding)

# print("=== QUERY RESULTS ===")
# print(f"Number of results: {len(chunks['ids'][0])}")
# print(f"\nTop 3 retrieved chunks:")
# for i in range(min(3, len(chunks['documents'][0]))):
#     print(f"\n--- Chunk {i+1} ---")
#     print(f"ID: {chunks['ids'][0][i]}")
#     print(f"Distance: {chunks['distances'][0][i]}")  # Lower = more similar
#     print(f"Text: {chunks['documents'][0][i][:300]}...")

# # Now send to LLM
# print("\n=== LLM RESPONSE ===")
# print(prompt_test(question, chunks))

def question_to_answer(question: str) -> str:
    embedding = question_to_embedding(question)
    chunks = embedding_to_chunks(embedding)
    return prompt_test(question, chunks)
