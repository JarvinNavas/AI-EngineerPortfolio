import streamlit as st
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
# Usamos CORE en lugar de CHAINS (Más estable)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# 1. Cargar llaves
load_dotenv()

st.set_page_config(page_title="DocuMind AI", page_icon="🚀")
st.title("🚀 DocuMind: RAG Engine")

@st.cache_resource
def inicializar_sistema():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_db = Chroma(persist_directory="./mi_base_de_datos", embedding_function=embeddings)
    retriever = vector_db.as_retriever()
    llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)

    # Definimos el Prompt
    template = """Eres un asistente técnico. Responde basado solo en el contexto:
    {context}
    
    Pregunta: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    # LA MAGIA: Construimos la cadena con el operador "|" (Pipe)
    # Esto no usa el módulo "chains", así que no dará error.
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain

chain = inicializar_sistema()

if "historial" not in st.session_state:
    st.session_state.historial = []

for msj in st.session_state.historial:
    with st.chat_message(msj["rol"]):
        st.write(msj["texto"])

pregunta = st.chat_input("Consulta tu manual...")

if pregunta:
    st.session_state.historial.append({"role": "user", "texto": pregunta})
    with st.chat_message("user"):
        st.write(pregunta)

    with st.chat_message("assistant"):
        # En LCEL se usa .invoke directamente
        respuesta = chain.invoke(pregunta)
        st.write(respuesta)
        st.session_state.historial.append({"role": "assistant", "texto": respuesta})