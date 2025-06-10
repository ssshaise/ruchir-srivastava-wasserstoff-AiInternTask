import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide" , page_title="Document Reasearch and Theme Identification Chatbot")

def load_css(file_path):
    """A simple helper function to load and inject a custom CSS file."""
    try:
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"CSS file not found at {file_path}. Continuing with default styles.")

def display_results(results_data):
    """
    This function takes the JSON response from the backend and renders it in a
    user-friendly way, separating the synthesized themes from the individual answers.
    """
    st.subheader("Synthesized Theme Answer")
    # We're building up an HTML string here to get more control over the formatting.
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
        # Pandas DataFrames are great for displaying tabular data cleanly in Streamlit.
        df = pd.DataFrame(individual_answers)
        if "Source Text" in df.columns:
            df = df.drop(columns=["Source Text"])
        # We're reordering the columns here to ensure a consistent display format.    
        df = df[["Document ID", "Extracted Answer", "Citation"]]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No specific answers could be extracted from the documents for this query.")
        
# Main App Logic

load_css("style.css")

# This is the public URL of our deployed backend on Render.
API_URL = "https://ruchir-srivastava-wasserstoff.onrender.com" 

# Using session_state is crucial for keeping data persistent between user interactions.
# It acts like the app's short-term memory.
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_files_list" not in st.session_state:
    st.session_state.uploaded_files_list = []

# We'll split the main page into two columns for a better layout.
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
                # We need to format the files in the way the 'requests' library expects for multi-part form data.
                files_for_api = [("files", (file.name, file.getvalue(), file.type)) for file in uploaded_files]
                try:
                    # This is where we make the actual call to our backend's /upload/ endpoint.
                    response = requests.post(f"{API_URL}/upload/", files=files_for_api)
                    response.raise_for_status()
                    # To avoid duplicates, we'll keep a unique, sorted list of file names.
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
    st.subheader("‎ What can I help you with?") # The empty character here is a small trick to add vertical space.
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                # If the message is from the AI, we use our custom display function.
                display_results(message["content"])
            else:
                st.markdown(message["content"])
    
     # st.chat_input is a special Streamlit component that 'listens' for user input.
    if prompt := st.chat_input("Ask a question about your documents..."):
        # First, display the user's own message in the chat.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Now, display the assistant's response.
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Make the call to our backend's /query/ endpoint with the user's question.
                    response = requests.post(f"{API_URL}/query/", json={"question": prompt})
                    response.raise_for_status()
                    results = response.json()
                    
                    # Save the AI's full JSON response to the chat history and display it.
                    st.session_state.messages.append({"role": "assistant", "content": results})
                    display_results(results)
                except requests.exceptions.RequestException as e:
                    st.error(f"Error connecting to backend: {e}")
                except Exception as e:
                    st.error(f"An error occurred: {e}")