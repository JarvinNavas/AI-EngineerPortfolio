import os
import shutil
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

def procesar_pdf():
    """
    Pipeline de Ingesta (ETL):
    Carga de documentos, segmentación semántica y persistencia en base de datos vectorial.
    """
    
    # --- PASO 1: Gestión de Estado Inicial ---
    # Eliminamos versiones previas de la base de datos para asegurar la integridad 
    # de los metadatos y evitar colisiones de índices vectoriales.
    if os.path.exists("./mi_base_de_datos"):
        shutil.rmtree("./mi_base_de_datos")
        print("🗑️ Base de datos antigua eliminada para limpieza de índices.")

    # --- PASO 2: Extracción de Datos (Extract) ---
    # PyPDFLoader no solo extrae texto plano, sino que preserva metadatos 
    # esenciales como el número de página para la trazabilidad de fuentes.
    print("📂 Cargando PDF...")
    loader = PyPDFLoader("manual.pdf")
    paginas = loader.load()

    # --- PASO 3: Segmentación Semántica (Transform) ---
    # El 'Chunking' es vital para no exceder la ventana de contexto del LLM.
    # Usamos RecursiveCharacterTextSplitter porque intenta mantener párrafos 
    # y oraciones completas unidas, mejorando la coherencia semántica.
    # chunk_size=1000: Balance óptimo entre granularidad y contexto.
    # chunk_overlap=150: Evita la pérdida de significado en los cortes de fragmentos.
    print("✂️ Aplicando segmentación (Chunking)...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=150,
        length_function=len
    )
    trozos = text_splitter.split_documents(paginas)
    print(f"✅ Documento segmentado en {len(trozos)} fragmentos.")

    # --- PASO 4: Generación de Embeddings (Modelado) ---
    # Utilizamos 'all-MiniLM-L6-v2' de sentence-transformers.
    # Es un modelo bi-encoder que mapea oraciones a un espacio vectorial de 384 dimensiones.
    # Elegido por su baja latencia y alta eficiencia en ejecución sobre CPU (Local).
    print("🧠 Generando representaciones vectoriales (Embeddings)...")
    embeddings_locales = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # --- PASO 5: Persistencia Vectorial (Load) ---
    # ChromaDB almacena los vectores y permite búsquedas de similitud de coseno.
    # 'persist_directory' asegura que el conocimiento se guarde en disco duro,
    # permitiendo que 'app.py' lo consulte sin repetir este proceso.
    print("💾 Indexando en base de datos vectorial persistente...")
    Chroma.from_documents(
        documents=trozos,
        embedding=embeddings_locales,
        persist_directory="./mi_base_de_datos"
    )
    print("🚀 PROCESO DE INGESTA COMPLETADO. Datos listos para RAG.")

if __name__ == "__main__":
    procesar_pdf()