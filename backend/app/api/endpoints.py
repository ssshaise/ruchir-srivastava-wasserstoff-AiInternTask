from fastapi import APIRouter, UploadFile, HTTPException
from typing import List
from ..core.services.documentprocessor import DocumentProcessor
from ..core.services.queryprocessor import QueryProcessor
from pydantic import BaseModel

from ..core.services.in_memory_store import db_store

router = APIRouter()

# Let's create instances of our main services upfront so they're ready for any incoming request.
doc_processor = DocumentProcessor()
query_processor = QueryProcessor()

@router.post("/upload/")
async def upload_documents(files: List[UploadFile]):
    if not files:
        raise HTTPException(status_code=400, detail="No files were uploaded.")

    try:
        # We'll hand off the heavy lifting of parsing and vectorizing to our dedicated document processor.
        vector_store = doc_processor.process_and_store(files)
        # If the processor couldn't get any usable text, there's nothing to store.
        if vector_store is None:
            raise HTTPException(status_code=400, detail="Could not extract any text from the uploaded documents.")
        # Here's the key part: we're storing the processed knowledge base
        # in a shared, in-memory object. This allows the /query endpoint to use it instantly.
        # Note: This state will be lost if the server ever restarts.
        db_store.vector_store = vector_store

        return {"message": f"Successfully uploaded and processed {len(files)} documents."}
    except Exception as e:
        print(f"Error during document processing: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

class QueryRequest(BaseModel):
    # Using Pydantic gives us nice, automatic validation for our request body.
    question: str

@router.post("/query/")
async def process_query(request: QueryRequest):
    try:
        # Now, we pass the user's question to the query processor, which will use the
        # vector store we saved in memory from the /upload step.
        result = query_processor.handle_query(request.question)
        return result
    except Exception as e:
        print(f"Error during query processing: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
