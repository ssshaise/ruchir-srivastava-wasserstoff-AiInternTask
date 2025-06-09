# Advanced Document Analysis & Theme Synthesis Chatbot

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Framework](https://img.shields.io/badge/LangChain-b047f5?style=for-the-badge)
![LLM](https://img.shields.io/badge/Google-Gemini_Pro-4285F4?style=for-the-badge)
![Frontend](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)
![Backend](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi)

An intelligent application that goes beyond simple Q&A to act as a powerful research assistant. It ingests multiple documents and synthesizes overarching themes, providing users with deep, contextual insights from their knowledge base.

---

## Live URL

You can visit the live demo at : https://reasearchgpttask.streamlit.app/

## The Problem

Researchers, students, and professionals often work with large volumes of documents (reports, academic papers, legal texts). While finding specific facts can be tedious, the real challenge lies in identifying the **connections, patterns, and recurring themes** that exist across the entire document set. Standard search tools and basic Q&A bots fail to provide this high-level synthesis.

## The Solution

This Chatbot is designed to bridge this gap. It's an advanced AI tool that doesn't just fetch answers—it **synthesizes knowledge**. By leveraging Large Language Models, this application provides users with two levels of insight:

1.  **Granular Answers:** Direct, specific answers extracted from individual documents, complete with precise citations.
2.  **Synthesized Themes:** The core feature. The AI analyzes all retrieved information to identify and explain the main themes, presenting a bird's-eye view of the most important concepts related to the user's query.

## Key Features

-   **📚 Multi-Document Ingestion:** Upload multiple documents (`.pdf`, `.txt`, etc.) to create a custom, ad-hoc knowledge base.
-   **💬 Context-Aware Q&A:** Get detailed, comprehensive answers based on the content of your documents. Prompt engineering was utilized to ensure responses are explanatory, not just concise.
-   **✨ Advanced Theme Synthesis:** The AI automatically detects recurring topics and synthesizes them into clear, easy-to-understand themes, complete with summaries and a list of supporting documents.
-   **📋 Dual-Response UI:** Presents information in a highly effective format: a high-level thematic summary followed by a detailed table of individual answers and their sources.
-   **🎨 Modern Tech Stack:** Built with a powerful and scalable combination of Python, Streamlit, FastAPI, LangChain, and Google's Gemini Pro.

## How It Works: Architecture Overview

This project implements an advanced Retrieval-Augmented Generation (RAG) pipeline.

1.  **Ingestion & Embedding:** When documents are uploaded, the text is extracted, split into manageable chunks, and converted into numerical representations (embeddings) using Google's text embedding model.
2.  **Vector Storage:** These embeddings and their associated metadata (source document, page number) are stored in a **FAISS** vector store, which allows for efficient similarity searches.
3.  **Retrieval:** When a user asks a question, the query is also embedded, and the vector store is searched to find the most semantically relevant document chunks.
4.  **Generation (Individual Answers):** Each relevant chunk is passed to the Gemini Pro LLM with a carefully engineered prompt, asking it to provide a detailed answer based *only* on that context.
5.  **Synthesis (Theme Generation):** All the individual answers are collected and fed into the Gemini Pro LLM a second time with a more complex prompt. This prompt instructs the AI to act as an analyst, find the common threads, and structure the output into the final themes, highlights, and supporting document lists.

## Tech Stack

| Category      | Technology                                    |
| :------------ | :-------------------------------------------- |
| **Frontend** | Streamlit                                     |
| **Backend** | Python, FastAPI (for API structure)           |
| **AI/ML** | Google Gemini Pro, LangChain                  |
| **Database** | FAISS (Vector Store)                          |
| **Styling** | Custom CSS                                    |

## Setup & Running the Application

Follow these steps to run the project locally. This project uses `conda` for environment management.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ssshaise/ruchir-srivastava-wasserstoff-AiInternTask.git
    cd ruchir-srivastava-wasserstoff-AiInternTask
    ```

2.  **Create and activate the Conda environment:**
    ```bash
    # Create a new conda environment with Python 3.9
    conda create --name researchgpt-env python=3.9 -y

    # Activate the new environment
    conda activate researchgpt-env
    ```

3.  **Install dependencies:**
    *The `requirements.txt` file works perfectly with `pip` inside a conda environment.*
    ```bash
    pip install -r backend/requirements.txt
    ```

4.  **Set up your API Key:**
    * Create a file named `.env` inside the `backend` folder.
    * Add your Google API key to it: `GOOGLE_API_KEY="your_actual_api_key_here"`

5.  **Run the application:**
    * Open two terminals (and ensure the `researchgpt-env` conda environment is activated in both).
    * In the **first terminal**, run the backend server:
        ```bash
        uvicorn backend.app.main:app --reload
        ```
    * In the **second terminal**, run the frontend:
        ```bash
        streamlit run frontend.py
        ```
    * Open your web browser to the local URL provided by Streamlit (usually `http://localhost:8501`).

