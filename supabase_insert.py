from supabase import create_client
import os

def insert_metadata(all_data):
    try:
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_API_KEY")
        )
        
        # Create a single document entry
        document_entry = {
            "document_id": all_data.doc_id,
            "filename": all_data.filename,
            "num_chunks": all_data.num_chunks
        }
        
        # Insert document metadata (one record per document)
        result = supabase.table("documents").insert(document_entry).execute()
        print(f"Successfully stored document in Supabase: {all_data.filename}")
        return result
        
    except Exception as e:
        print(f"Failed to store in Supabase: {str(e)}")
        return None


