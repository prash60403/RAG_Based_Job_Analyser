import os
import streamlit as st

from rag_utility import process_document_to_chroma_db, answer_question

# Working directory
working_dir = os.path.dirname(os.path.abspath(__file__))

st.title("📄 Llama RAG Chatbot")

# Upload PDF
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

# Process document only once
if uploaded_file is not None:
    save_path = os.path.join(working_dir, uploaded_file.name)

    # Save file
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Avoid reprocessing
    if "processed" not in st.session_state:
        process_document_to_chroma_db(uploaded_file.name)
        st.session_state.processed = True
        st.success(" Document processed successfully!")

# Ask question
user_question = st.text_input("Ask a question about the document:")

if st.button("Get Answer"):
    if uploaded_file is None:
        st.warning("⚠️ Please upload a PDF first.")
    elif user_question.strip() == "":
        st.warning("⚠️ Please enter a question.")
    else:
        answer = answer_question(user_question)

        st.markdown("### 🤖 Llama Answer:")
        st.write(answer)