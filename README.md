# Stock Market News RAG Pipeline with LLM Integration

This project provides real-time stock market news summaries and commentary using a Retrieval-Augmented Generation (RAG) pipeline connected to an LLM through Ollama. The pipeline automates news ingestion, processes articles, and delivers context-aware insights through a backend API.

---

## Features
- Automated daily news ingestion with **Google Cloud Scheduler** and the **Alpha Vantage News API**  
- Storage of raw and processed data in **Google Cloud Storage**  
- Data parsing and cleaning with **Python** and **Pandas**  
- Article summarization using **newspaper3k** prior to embedding  
- Embedding storage in a **vector database** for similarity search  
- Integration with **Ollama** for retrieval-augmented LLM responses  
- Backend built with **FastAPI** and deployed on **Google Cloud Run**  

---

## Tech Stack
- **Languages & Libraries:** Python, Pandas, newspaper3k  
- **Frameworks:** FastAPI, Ollama  
- **Cloud Services:** Google Cloud Run, Cloud Scheduler, Cloud Storage  
- **Databases:** Vector database (FAISS, Pinecone, or PGVector)  

