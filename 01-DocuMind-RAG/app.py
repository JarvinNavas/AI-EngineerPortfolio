import streamlit as st
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
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
    # El retriever buscará los 3 fragmentos más parecidos
    retriever = vector_db.as_retriever(search_kwargs={"k": 3})
    llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)

    template = """Eres un asistente técnico. Responde basado solo en el contexto:
    {context}
    
    Pregunta: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    # Cadena para generar la respuesta
    chain = (
        {"context": lambda x: x["context"], "question": lambda x: x["question"]}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return retriever, chain

retriever, chain = inicializar_sistema()

if "historial" not in st.session_state:
    st.session_state.historial = []

for msj in st.session_state.historial:
    with st.chat_message(msj["role"]):
        st.write(msj["texto"])

pregunta = st.chat_input("Consulta tu manual...")

if pregunta:
    st.session_state.historial.append({"role": "user", "texto": pregunta})
    with st.chat_message("user"):
        st.write(pregunta)

    with st.chat_message("assistant"):
        # PASO CLAVE: Primero recuperamos los documentos manualmente
        docs_relevantes = retriever.invoke(pregunta)
        
        # Extraemos el contenido para el LLM
        contexto_combinado = "\n\n".join([doc.page_content for doc in docs_relevantes])
        
        # Generamos la respuesta pasando el contexto
        respuesta = chain.invoke({"context": contexto_combinado, "question": pregunta})
        st.write(respuesta)
        
        # MOSTRAR FUENTES: Extraemos los números de página de los metadatos
        paginas = sorted(list(set([str(doc.metadata.get('page', 0) + 1) for doc in docs_relevantes])))
        fuentes_texto = f"📌 **Fuentes:** Páginas {', '.join(paginas)}"
        st.caption(fuentes_texto)
        
        st.session_state.historial.append({"role": "assistant", "texto": respuesta + "\n\n" + fuentes_texto})