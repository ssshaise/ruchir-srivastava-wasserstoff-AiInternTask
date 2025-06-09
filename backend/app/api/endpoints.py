from fastapi import APIRouter, UploadFile, HTTPException
from typing import List
from ..core.services.documentprocessor import DocumentProcessor
from ..core.services.queryprocessor import QueryProcessor
from pydantic import BaseModel

from ..core.services.in_memory_store import db_store

router = APIRouter()
doc_processor = DocumentProcessor()
query_processor = QueryProcessor()

@router.post("/upload/")
async def upload_documents(files: List[UploadFile]):
    if not files:
        raise HTTPException(status_code=400, detail="No files were uploaded.")

    try:
        vector_store = doc_processor.process_and_store(files)

        if vector_store is None:
            raise HTTPException(status_code=400, detail="Could not extract any text from the uploaded documents.")

        db_store.vector_store = vector_store

        return {"message": f"Successfully uploaded and processed {len(files)} documents."}
    except Exception as e:
        print(f"Error during document processing: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

class QueryRequest(BaseModel):
    question: str

@router.post("/query/")
async def process_query(request: QueryRequest):
    try:
        result = query_processor.handle_query(request.question)
        return result
    except Exception as e:
        print(f"Error during query processing: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@router.get("/test-access/")
async def test_public_access():
    # Forcing a new deployment on Vercel
    return {"message": "Success! Public access is working."}