import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

working_dir = os.path.dirname(os.path.abspath(__file__))

embedding = HuggingFaceEmbeddings()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.1,
)

# ✅ FIXED NAME
def process_document_to_chroma_db(file_name):
    loader = PyPDFLoader(f"{working_dir}/{file_name}")
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    texts = text_splitter.split_documents(documents)

    vectordb = Chroma.from_documents(
        documents=texts,
        embedding=embedding,
        persist_directory=f"{working_dir}/doc_vectorstore"
    )

    return vectordb


def answer_question(user_question):
    vectordb = Chroma(
        persist_directory=f"{working_dir}/doc_vectorstore",
        embedding_function=embedding
    )

    retriever = vectordb.as_retriever(search_kwargs={"k": 3})

    prompt = ChatPromptTemplate.from_template(
        """
        Answer the question based only on the context below.

        Context:
        {context}

        Question:
        {question}
        """
    )

    qa_chain = (
        {
            "context": retriever,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    answer = qa_chain.invoke(user_question)

    return answer