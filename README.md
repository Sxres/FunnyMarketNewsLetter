---
 


# 📈 Stock Market News RAG Pipeline with LLM Integration

This project delivers **real-time stock market news summaries and commentary** using a **Retrieval-Augmented Generation (RAG) pipeline** connected to an LLM via **Ollama**. The system automates news ingestion, processes articles, and serves context-aware insights through a backend API.

---

## 🚀 Features
- Daily **news ingestion** via **Google Cloud Scheduler + Alpha Vantage News API**.
- Raw and processed data stored in **Google Cloud Storage buckets**.
- JSON parsing and cleaning with **Python (Pandas)**.
- Article summarization with **newspaper3k** before embedding.
- Embedding storage in a **vector database** for similarity search.
- Integrated **LLM via Ollama** for retrieval-augmented answers.
- Backend powered by **FastAPI**, deployed on **Google Cloud Run**.

---

## 🛠️ Tech Stack
- **Languages & Libraries:** Python, Pandas, newspaper3k  
- **Frameworks:** FastAPI, Ollama  
- **Cloud Services:** Google Cloud Run, Cloud Scheduler, Cloud Storage  
- **Databases:** Vector database (e.g., FAISS/Pinecone/PGVector)
