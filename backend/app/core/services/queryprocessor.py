import re
import time
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from ...core.services.in_memory_store import db_store

class QueryProcessor:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.2, 
            
        )
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001", 
            
        )

    def handle_query(self, question: str):
        vector_store = db_store.vector_store
        if not vector_store:
            return {"individual_answers": [], "synthesized_themes": []}

        relevant_docs = vector_store.similarity_search(question, k=5)
        if not relevant_docs:
            return {"individual_answers": [], "synthesized_themes": []}

        individual_answers = []
        for doc in relevant_docs:
            time.sleep(1)
            
            prompt = PromptTemplate(
                template="You are a helpful research assistant. Based *only* on the context provided below, give a detailed and comprehensive answer to the user's question. Explain the answer fully in 2-3 sentences. If the context contains direct quotes or key phrases that are highly relevant, you can include them. Do not give a short or overly summarized answer.\n\nContext:\n```\n{context}\n```\n\nQuestion: {question}",
                input_variables=["context", "question"]
            )
            chain = LLMChain(llm=self.llm, prompt=prompt)
            try:
                response = chain.invoke({"context": doc.page_content, "question": question})
                answer_text = response['text'].strip()
            except Exception as e:
                print(f"Error invoking LLM chain for a document: {e}")
                answer_text = "Error processing this document."

            individual_answers.append({
                "Document ID": doc.metadata.get("source", "N/A"),
                "Extracted Answer": answer_text,
                "Citation": f"Page {doc.metadata.get('page', 'N/A')}, Para {doc.metadata.get('paragraph', 'N/A')}"
            })

        answers_context = "\n\n".join([f"From {ans['Document ID']} ({ans['Citation']}): {ans['Extracted Answer']}" for ans in individual_answers])

        theme_prompt_template = """
        Analyze the following extracted answers. Identify key themes.
        For each theme, you MUST format your output EXACTLY as follows:

        Theme Name: [A concise name for the theme]
        Supporting Documents: [A comma-separated list of unique Document IDs]
        Highlight: [A detailed paragraph of 2-4 sentences that synthesizes the insights for this theme. Explain what the theme means and why it's important based on the provided answers.]

        Here are the answers to analyze:
        {answers_context}
        """
        
        theme_prompt = PromptTemplate(template=theme_prompt_template, input_variables=["answers_context"])
        theme_chain = LLMChain(llm=self.llm, prompt=theme_prompt)
        
        try:
            theme_response_text = theme_chain.invoke({"answers_context": answers_context})['text']
        except Exception as e:
            print(f"Error during theme generation: {e}")
            theme_response_text = ""

        synthesized_themes = []
        theme_chunks = theme_response_text.strip().split("Theme Name:")
        pattern = re.compile(r"(.*?)\nSupporting Documents: (.*?)\nHighlight: (.*)", re.DOTALL)

        for chunk in theme_chunks:
            if not chunk.strip():
                continue
            
            match = pattern.search(chunk)
            if match:
                theme_name, supporting_docs, highlight = match.groups()
                doc_list = [doc.strip() for doc in supporting_docs.split(',')]
                unique_docs = list(dict.fromkeys(doc_list))
                cleaned_docs_str = ", ".join(unique_docs)

                synthesized_themes.append({
                    "Theme": theme_name.strip(),
                    "Supporting Documents": cleaned_docs_str,
                    "Highlight": highlight.strip()
                })

        return {
            "individual_answers": individual_answers,
            "synthesized_themes": synthesized_themes
        }