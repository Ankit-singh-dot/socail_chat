# Social Knowledge Base (Social Chat)

Welcome to **Social Chat**! This is a full-stack, AI-powered Retrieval-Augmented Generation (RAG) application that lets you "chat" directly with your own social media data (LinkedIn, Twitter, and Instagram exports). 

Instead of building just another wrapper around expensive closed-source APIs, this architecture is intentionally designed to be **blazing fast, fully local/open-source where it matters, and 100% free to host**.

## 🛠️ The Tech Stack (What & Why)

Here is a breakdown of the technologies powering this app and the reasoning behind each choice:

### 1. The Brains: Groq & Llama 3.1
* **What it is:** We use Groq's API to run Meta's open-source Llama 3.1 model.
* **Why we chose it:** By switching away from OpenAI/Gemini to Groq, we get near-zero latency inference speeds. Furthermore, using open-weight models protects us from vendor lock-in and unexpected deprecations, all while staying entirely free.

### 2. The Embeddings: FastEmbed (BAAI/bge-small-en-v1.5)
* **What it is:** A lightweight, CPU-optimized Python library that runs the BGE-Small embedding model entirely locally in our backend via ONNX.
* **Why we chose it:** Originally, the app relied on paid APIs to generate vector embeddings. By pulling this process entirely in-house with `fastembed`, we eliminated API rate limits, improved privacy, and reduced costs to $0. The BGE-Small model strikes the perfect balance between high retrieval accuracy and a low memory footprint (~130MB).

### 3. The Memory: Qdrant Cloud
* **What it is:** A highly scalable, rust-based Vector Database.
* **Why we chose it:** We chose Qdrant over alternatives like Chroma or Pinecone because its metadata filtering and payload indexing are genuinely production-grade. Because we need to filter citations by platform and date, payload indexing is critical. 

### 4. The Backend: FastAPI (Python)
* **What it is:** A modern, high-performance web framework for Python.
* **Why we chose it:** Python is the undisputed king of ML ecosystems. FastAPI gives us robust asynchronous routing, background tasks (perfect for our data ingestion pipeline), and built-in Pydantic validation.

### 5. The Frontend: Next.js & TailwindCSS
* **What it is:** A React framework for building the user interface.
* **Why we chose it:** Next.js provides a clean, reactive chat UI, while Tailwind gives us the flexibility to create a professional, minimal black-and-white aesthetic without bloated CSS files.

---

## 🚀 Deployment Strategy

This application is decoupled into three distinct services, perfectly optimized for free-tier cloud hosting:

### 1. Vector Database -> Qdrant Cloud ☁️
Instead of managing Docker containers ourselves, the vector database is fully managed by **Qdrant Cloud**. 
* **Location:** AWS Region (sa-east-1)
* **How it connects:** The backend authenticates via a secure `QDRANT_API_KEY` stored in the `.env` file.

### 2. Backend -> Render.com ⚙️
The FastAPI Python backend is deployed as a Web Service on **Render**.
* **Why Render over Vercel?** Vercel's serverless functions are great for web APIs, but they struggle with ML workloads. Because our backend uses `fastembed` to download and load a 130MB ML model into RAM, it exceeds Vercel's 250MB size limit. Render provides a continuous Linux container (512MB RAM) that can comfortably hold the model in memory.
* **Location:** Oregon (US West)

### 3. Frontend -> Vercel 🖥️
The Next.js user interface is deployed directly to **Vercel**.
* **How it connects:** The Vercel project is configured with a `NEXT_PUBLIC_API_URL` environment variable that points directly to the live Render backend URL. It's completely decoupled, meaning the UI can scale infinitely via Vercel's Edge Network.

---

## 🧠 Key Architectural Features

- **The Normalization Layer:** Instead of forcing the Vector DB to understand three different raw data exports (CSV, JSON, HTML), all parsers pipe into a unified `NormalizedDocument` schema. Adding a fourth platform (like Reddit) simply requires writing a new parser—no downstream database migrations needed.
- **Incremental Upserts:** The chunker generates a SHA-256 hash of the content. During ingestion, we query Qdrant for this hash first; if it exists, we skip embedding it. This prevents duplicating data and saves massive amounts of computation on subsequent uploads.
