from print_function import pdf_folder_files_text
from google import genai
from google.genai import types
from dotenv import load_dotenv
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


import os

load_dotenv()

folder = "test_files"
files = ["Dos.pdf", "Tres.pdf", "White.pdf"]

content = pdf_folder_files_text(folder, files)

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

result = client.models.embed_content(
    model="gemini-embedding-001",
    contents=content,
    config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT", output_dimensionality=768)
)

# Extract the actual embedding vectors from ContentEmbedding objects
embeddings_matrix = np.array([embedding.values for embedding in result.embeddings])
similarity_matrix = cosine_similarity(embeddings_matrix)

for i, text1 in enumerate(content):
    for j in range(i + 1, len(content)):
        text2 = content[j]
        similarity = similarity_matrix[i, j]
        print(f"Similarity between '{text1}' and '{text2}': {similarity:.4f}")