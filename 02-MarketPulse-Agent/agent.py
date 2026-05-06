import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults

from langchain_classic.agents import AgentExecutor, create_tool_calling_agent

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(page_title="MarketPulse Agent", page_icon="🕵️‍♂️")
st.title("🕵️‍♂️ MarketPulse: AI Researcher")

@st.cache_resource
def setup_agent():
    # 1. Asegúrate de que Tavily esté bien configurado
    # Importante: Si no pusiste la llave en el .env, cámbiala aquí directamente para probar
    api_key = os.getenv("TAVILY_API_KEY")
    search_tool = TavilySearchResults(k=5) # Pedimos 5 resultados para más detalle
    tools = [search_tool]
    
    # 2. Cerebro
    llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)

    # 3. Prompt de Sistema más "Agresivo"
    # Aquí le ordenamos que USE las herramientas obligatoriamente
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Eres un Investigador de Mercado de ÉLITE. 
        TU REGLA NÚMERO 1: Si te preguntan por datos actuales, precios o noticias, DEBES usar la herramienta de búsqueda.
        No des respuestas genéricas. Busca en internet, analiza los resultados y cita las fuentes con sus URLs."""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # 4. Construcción con 'classic'
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    # handle_parsing_errors=True es vital para que no se rinda si la respuesta es compleja
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# Inicializar
try:
    agent_executor = setup_agent()
except Exception as e:
    st.error(f"Error al inicializar el agente: {e}")
    st.stop()

# --- Interfaz de Chat Simple ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("¿Qué quieres investigar?")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        response = agent_executor.invoke({
            "input": user_input,
            "chat_history": st.session_state.messages[:-1]
        })
        st.markdown(response["output"])
        st.session_state.messages.append({"role": "assistant", "content": response["output"]})