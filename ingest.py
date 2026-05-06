import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

def procesar_pdf():
    """
    Pipeline de Ingesta: Carga, Segmenta y Vectoriza un PDF.
    """
    # Paso 1: Limpieza de seguridad para evitar colisión de bases de datos
    if os.path.exists("./mi_base_de_datos"):
        import shutil
        shutil.rmtree("./mi_base_de_datos")
        print("🗑️ Base de datos antigua eliminada.")

    # Paso 2: Carga de Documento
    print("📂 Cargando PDF...")
    loader = PyPDFLoader("manual.pdf")
    paginas = loader.load()

    # Paso 3: Chunking (Segmentación Semántica)
    # Dividimos en trozos de 1000 caracteres con solapamiento para no perder contexto entre partes.
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    trozos = text_splitter.split_documents(paginas)
    print(f"✂️ Documento dividido en {len(trozos)} fragmentos.")

    # Paso 4: Embedding y Almacenamiento Vectorial
    # Usamos un modelo local de HuggingFace para transformar texto en coordenadas matemáticas.
    print("🧠 Generando Embeddings locales...")
    embeddings_locales = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Creamos la base de datos ChromaDB que se guardará en disco
    print("💾 Guardando en base de datos vectorial...")
    Chroma.from_documents(
        documents=trozos,
        embedding=embeddings_locales,
        persist_directory="./mi_base_de_datos"
    )
    print("✅ Proceso de ingesta completado con éxito.")

if __name__ == "__main__":
    procesar_pdf()