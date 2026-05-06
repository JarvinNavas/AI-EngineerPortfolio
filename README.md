# 🤖 DocuMind: RAG AI Assistant

A high-performance **Retrieval-Augmented Generation (RAG)** engine that allows you to chat with PDF documents locally and securely.

## 🚀 Technical Stack
- **Framework:** LangChain (LCEL)
- **LLM:** Llama 3.3 via Groq (Ultra-low latency)
- **Embeddings:** HuggingFace (Local)
- **Vector Store:** ChromaDB
- **Interface:** Streamlit

## 🛠️ How to Run
1. Add your `GROQ_API_KEY` to a `.env` file.
2. Run `python ingest.py` to process your PDF.
3. Run `streamlit run app.py` to start the chat.