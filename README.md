# 🤖 DocuMind: High-Performance RAG Assistant

DocuMind is a **Retrieval-Augmented Generation (RAG)** solution that enables private, real-time conversations with PDF documents. It bypasses context window limits by using a vectorized local knowledge base.

## 🏗️ Architecture Flow
1. **Ingestion (`ingest.py`):** PDF → Text Splitting (Recursive) → Vector Embeddings (HuggingFace) → Vector Store (ChromaDB).
2. **Inference (`app.py`):** User Query → Semantic Search → Context Injection → LLM Response (Llama 3.3 via Groq).

## 🛠️ Tech Stack
- **Orchestration:** LangChain (LCEL)
- **LLM:** Llama-3.3-70b-versatile (Groq Cloud)
- **Vector Database:** ChromaDB
- **Embeddings:** sentence-transformers/all-MiniLM-L6-v2 (Local)
- **Frontend:** Streamlit

## ⚡ Key Features
- **Semantic Precision:** Uses overlap chunking to maintain context integrity.
- **Source Attribution:** Every response includes the specific page numbers used as reference.
- **Zero-Latency:** Powered by Groq's LPU inference engine.
- **Privacy First:** Document processing and embedding generation occur locally.

## ⚙️ Setup
1. Clone the repo and create a virtual environment.
2. Install dependencies: `pip install -r requirements.txt`.
3. Create a `.env` file with your `GROQ_API_KEY`.
4. Run `python ingest.py` to index your `manual.pdf`.
5. Start the chat: `streamlit run app.py`.