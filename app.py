import streamlit as st
from src.DocumentChatbot import DocumentChatbot
import os
import tempfile

# Initialize session state for chatbot and document status
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = DocumentChatbot()

if 'document_loaded' not in st.session_state:
    st.session_state.document_loaded = False

if 'messages' not in st.session_state:
    st.session_state.messages = []

st.title("Document Chatbot")

# File upload section
uploaded_file = st.file_uploader("Upload a document", type=['pdf'])
if uploaded_file and not st.session_state.document_loaded:

    # Create a temporary file to save the uploaded content
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name
    
    try:
        # Load the document using the temporary file path
        st.session_state.chatbot.load_document(tmp_file_path)
        st.session_state.document_loaded = True
        st.success("Document loaded successfully! You can now ask questions.")
    except Exception as e:
        st.error(f"Error loading document: {str(e)}")
    finally:
        # Clean up the temporary file
        os.unlink(tmp_file_path)

# Display chat interface and conversation history
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input area for users to ask questions about the document
if st.session_state.document_loaded:
    if prompt := st.chat_input("Ask a question about the document"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get bot response to the user's query
        response = st.session_state.chatbot.process_query(prompt)

        # Add assistant's response to chat history and display it
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
else:
    st.info("Please upload a PDF document to get started.")
