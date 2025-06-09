import streamlit as st
import requests
import pandas as pd

st.subheader("Backend Connection Test")

VERCEL_BASE_URL = "https://ruchir-srivastava-wasserstoff-ai-intern-task-3yv9jdiqr.vercel.app" 

if st.button("Run Backend Connection Test"):
    try:
        test_url = f"{VERCEL_BASE_URL}/test-public-access/"
        st.write(f"Calling: {test_url}")
        response = requests.get(test_url)
        st.write("Backend Response:")
        st.write(f"Status Code: {response.status_code}")
        st.json(response.json())
    except Exception as e:
        st.error(f"An error occurred during the test: {e}")


st.set_page_config(layout="wide" , page_title="Document Reasearch and Theme Identification Chatbot")

def load_css(file_path):
    try:
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"CSS file not found at {file_path}. Continuing with default styles.")

def display_results(results_data):
    """Renders the results in the specified format."""
    
    st.subheader("Synthesized Theme Answer")
    themes = results_data.get("synthesized_themes", [])
    
    if themes:
        theme_html = ""
        for i, theme in enumerate(themes):
            theme_title = theme.get("Theme", "Unnamed Theme")
            doc_ids = theme.get("Supporting Documents", "N/A")
            highlight = theme.get("Highlight", "No summary available.")
            
            # This line creates the "Theme 1 - Title: Docs: Highlight" format.
            theme_html += f"<p><b>Theme {i+1} – {theme_title}:</b><br>{doc_ids}: {highlight}</p>"
            
        st.markdown(theme_html, unsafe_allow_html=True)
    else:
        st.info("No distinct themes were identified for this query.")
    
    st.markdown("---")
    
    st.subheader("Individual Document Answers")
    individual_answers = results_data.get("individual_answers", [])
    
    if individual_answers:
        df = pd.DataFrame(individual_answers)
        if "Source Text" in df.columns:
            df = df.drop(columns=["Source Text"])
        df = df[["Document ID", "Extracted Answer", "Citation"]]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No specific answers could be extracted from the documents for this query.")

load_css("style.css")

API_URL = "https://ruchir-srivastava-wasserstoff-ai-intern-task-3yv9jdiqr.vercel.app" 

if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_files_list" not in st.session_state:
    st.session_state.uploaded_files_list = []

chat_col, knowledge_col = st.columns([2, 1])

with knowledge_col:
    st.subheader("Knowledge Base")
    uploaded_files = st.file_uploader(
        "Upload documents", 
        accept_multiple_files=True,
        type=['pdf', 'txt', 'png', 'jpg'],
        label_visibility="collapsed"
    )

    if st.button("Process Documents", use_container_width=True):
        if uploaded_files:
            with st.spinner("Processing documents..."):
                files_for_api = [("files", (file.name, file.getvalue(), file.type)) for file in uploaded_files]
                try:
                    response = requests.post(f"{API_URL}/upload/", files=files_for_api)
                    response.raise_for_status()
                    current_files = [file.name for file in uploaded_files]
                    st.session_state.uploaded_files_list.extend(current_files)
                    st.session_state.uploaded_files_list = sorted(list(set(st.session_state.uploaded_files_list)))
                    st.success(response.json().get("message", "Success!"))
                except requests.exceptions.RequestException as e:
                    st.error(f"Error connecting to backend: {e}")
        else:
            st.warning("Please upload documents first.")

    st.markdown("---")
    st.write("Processed Documents:")
    if st.session_state.uploaded_files_list:
        for file_name in st.session_state.uploaded_files_list:
            st.info(f"📄 {file_name}")
    else:
        st.info("No documents processed yet.")

with chat_col:
    st.subheader("‎ What can I help you with?")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                display_results(message["content"])
            else:
                st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question about your documents..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = requests.post(f"{API_URL}/query/", json={"question": prompt})
                    response.raise_for_status()
                    results = response.json()
                    st.session_state.messages.append({"role": "assistant", "content": results})
                    display_results(results)
                except requests.exceptions.RequestException as e:
                    st.error(f"Error connecting to backend: {e}")
                except Exception as e:
                    st.error(f"An error occurred: {e}")