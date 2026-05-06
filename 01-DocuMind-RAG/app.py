import streamlit as st
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# --- CONFIGURACIÓN INICIAL ---
load_dotenv() 

st.set_page_config(page_title="DocuMind RAG Pro", page_icon="🕵️‍♂️")
st.title("🕵️‍♂️ DocuMind: Inteligencia con Fuentes")
st.markdown("---")

# st.cache_resource es CRÍTICO: Evita que el modelo de 400MB y la base de datos
# se recarguen cada vez que el usuario hace clic en un botón, ahorrando RAM y tiempo.
@st.cache_resource
def inicializar_sistema():
    """
    Orquestación de los componentes de Inteligencia Artificial.
    """
    # 1. Cargamos el modelo de embeddings (Debe ser el mismo usado en ingest.py)
    # Convierte la pregunta del usuario en un vector numérico para poder compararla.
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # 2. Conexión con ChromaDB: Accedemos a la carpeta donde guardamos los vectores.
    vector_db = Chroma(persist_directory="./mi_base_de_datos", embedding_function=embeddings)
    
    # 3. El Retriever (Recuperador): Es el 'librero'. 
    # search_kwargs={"k": 3} significa que solo extraerá los 3 párrafos más relevantes.
    retriever = vector_db.as_retriever(search_kwargs={"k": 3}) 

    # 4. LLM: Usamos Groq con Llama 3.3. 
    # temperature=0 es fundamental para respuestas técnicas para evitar que la IA 'alucine'.
    llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)

    # 5. Prompt Engineering: Aquí definimos la 'personalidad' y límites de la IA.
    # El placeholder {context} será llenado con los fragmentos que encuentre el retriever.
    system_prompt = (
        "Eres un asistente técnico riguroso. Usa los fragmentos de contexto para responder. "
        "Si no encuentras la respuesta, admítelo. Al final de tu respuesta, "
        "indica siempre en qué página(s) encontraste la información.\n\n"
        "Contexto: {context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    # 6. Creación de la Cadena (Chain): 
    # combine_docs_chain: Define cómo se mezclan los fragmentos de texto con el prompt.
    # rag_chain: Es el proceso completo (Pregunta -> Recuperar -> Generar).
    combine_docs_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, combine_docs_chain)
    
    return rag_chain

# Ejecutamos la inicialización una sola vez
chain = inicializar_sistema()

# --- GESTIÓN DE MEMORIA DE CHAT ---
# session_state permite que el chat no se borre al refrescar la página.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Muestra el historial guardado en la pantalla
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- LÓGICA DE PREGUNTA Y RESPUESTA ---
if prompt_user := st.chat_input("¿Qué dice el manual sobre...?"):
    # Guardamos la pregunta del usuario en el historial
    st.session_state.messages.append({"role": "user", "content": prompt_user})
    with st.chat_message("user"):
        st.markdown(prompt_user)

    with st.chat_message("assistant"):
        with st.spinner("Buscando en el documento..."):
            # chain.invoke: Dispara todo el proceso RAG.
            # Retorna un diccionario con 'answer' (texto) y 'context' (los trozos del PDF usados).
            response = chain.invoke({"input": prompt_user})
            full_response = response["answer"]
            
            # EXTRACCIÓN DE METADATOS: 
            # Recorremos los documentos recuperados para extraer el número de página original.
            # set() evita que se repita el número de página si usó dos párrafos de la misma hoja.
            sources = set([doc.metadata.get("page", "N/A") for doc in response["context"]])
            source_text = f"\n\n**Fuentes consultadas (Páginas):** {', '.join(map(str, sources))}"
            
            final_text = full_response + source_text
            st.markdown(final_text)
            
            # Guardamos la respuesta final en el historial
            st.session_state.messages.append({"role": "assistant", "content": final_text})