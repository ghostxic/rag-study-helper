from pypdf import PdfReader, PdfWriter
from langchain_text_splitters import RecursiveCharacterTextSplitter

folder = "test_files"
files = ["Dos.pdf", "Tres.pdf", "White.pdf"]

def pdf_folder_files_text(folder: str, files: str) -> list[str]:
    text = ""
    for file in files:
        path = f"{folder}/{file}"
        writer = PdfWriter(clone_from=path, strict=True)
        writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)
        writer.remove_images()
        writer.write(path)

        reader = PdfReader(path, strict=True)
        for page in reader.pages:
            text += page.extract_text()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,      # The maximum size of each chunk (in characters/tokens, depending on your length function)
            chunk_overlap=100,   # The amount of overlap between chunks to maintain context across boundaries
            length_function=len, # Use the built-in len() function to measure chunk length (for character count)
        )
            # Split the text
        chunks = text_splitter.split_text(text)
        return chunks
        # for i, chunk in enumerate(chunks):
        #     print(f"Chunk {i+1} (Length: {len(chunk)}):\n{chunk}\n{'-'*20}")