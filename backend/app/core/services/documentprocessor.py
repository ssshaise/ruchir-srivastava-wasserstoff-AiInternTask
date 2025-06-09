# In backend/app/core/services/document_processor.py

import os
import pytesseract
from PIL import Image
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from fastapi import UploadFile
from typing import List
from ...config import settings

try:
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
except Exception as e:
    print(f"Tesseract configuration skipped, assuming it's in PATH. Error: {e}")

DATA_DIR = "backend/data"
VECTOR_STORE_PATH = os.path.join(DATA_DIR, "faiss_index")

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=settings.GOOGLE_API_KEY
        )
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

    def _create_documents_with_paragraph_metadata(self, text_chunks, source, page_number):
        """Helper function to create Document objects with paragraph metadata."""
        documents = []
        for i, chunk in enumerate(text_chunks):
            documents.append(Document(
                page_content=chunk,
                metadata={
                    'source': source, 
                    'page': page_number,
                    'paragraph': i + 1 
                }
            ))
        return documents

    def _extract_text_from_pdf(self, file_path: str, filename: str):
        """Extracts text from a PDF, splits by paragraph, and adds metadata."""
        print(f"Processing PDF: {filename}")
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        
        all_page_chunks = []
        for page in pages:
            text_chunks = self.text_splitter.split_text(page.page_content)
            docs = self._create_documents_with_paragraph_metadata(
                text_chunks, 
                filename, 
                page.metadata.get('page', 0) + 1
            )
            all_page_chunks.extend(docs)
        return all_page_chunks

    def _extract_text_from_image(self, file_path: str, filename: str):
        """Extracts text from an image, splits by paragraph, and adds metadata."""
        print(f"Processing Image: {filename}")
        try:
            text = pytesseract.image_to_string(Image.open(file_path))
            if not text:
                return []
            
            text_chunks = self.text_splitter.split_text(text)
            return self._create_documents_with_paragraph_metadata(
                text_chunks, 
                filename, 
                1
            )
        except Exception as e:
            print(f"Error processing image {filename}: {e}")
            return []

    def process_and_store(self, files: List[UploadFile]):
        """Processes uploaded files and returns an in-memory FAISS vector store."""
        all_chunks = []
        temp_dir = os.path.join(DATA_DIR, "temp_files")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        try:
            for file in files:
                file_path = os.path.join(temp_dir, file.filename)
                with open(file_path, "wb") as f:
                    f.write(file.file.read())

                chunks = []
                file_ext = os.path.splitext(file.filename)[1].lower()

                if file_ext == '.pdf':
                    chunks = self._extract_text_from_pdf(file_path, file.filename)
                elif file_ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
                    chunks = self._extract_text_from_image(file_path, file.filename)
                else:
                    print(f"Unsupported file type: {file.filename}, skipping.")

                if chunks:
                    all_chunks.extend(chunks)
        finally:
            for file in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, file))
            os.rmdir(temp_dir)

        if not all_chunks:
            print("No text could be extracted from the documents.")
            return None

        print("Creating in-memory vector store...")
        vector_store = FAISS.from_documents(all_chunks, self.embeddings)
        print("In-memory vector store created.")
        return vector_store