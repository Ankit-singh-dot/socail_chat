# Social Knowledge Base (Social Chat)

Welcome to **Social Chat**! This is a full-stack, AI-powered Retrieval-Augmented Generation (RAG) application that lets you "chat" directly with your own social media data (LinkedIn, Twitter, and Instagram exports). 

Instead of building just another wrapper around expensive closed-source APIs, this architecture is intentionally designed to be **blazing fast, fully local/open-source where it matters, and 100% free to host**.

##  The Tech Stack (What & Why)

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

##  Deployment Strategy

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

## Key Architectural Features

- **The Normalization Layer:** Instead of forcing the Vector DB to understand three different raw data exports (CSV, JSON, HTML), all parsers pipe into a unified `NormalizedDocument` schema. Adding a fourth platform (like Reddit) simply requires writing a new parser—no downstream database migrations needed.
- **Incremental Upserts:** The chunker generates a SHA-256 hash of the content. During ingestion, we query Qdrant for this hash first; if it exists, we skip embedding it. This prevents duplicating data and saves massive amounts of computation on subsequent uploads.

---

## Architecture Write-up (Assignment Answers)

### What does your system do, and what are the two or three most important architecture decisions you made?
This system allows users to upload data exports from LinkedIn, Twitter, and Instagram directly through a Next.js UI, parses and embeds the data locally using open-weight models, stores it in Qdrant, and serves grounded answers via a Groq-powered RAG chat interface. The three most critical architecture decisions were: 
1. **The Normalization Layer**: Pipping all distinct CSV/JSON/HTML parsers into a unified `NormalizedDocument` schema so the DB and Chunker never care about where the data came from. 
2. **Local FastEmbed over Paid APIs**: Shifting from paid embedding APIs to running `fastembed` (BGE-Small) via ONNX on the FastAPI server to eliminate rate-limits, reduce latency, and keep the service 100% free. 
3. **Decoupled Deployment**: Isolating the ML-heavy Python backend onto Render and the lightweight Next.js frontend onto Vercel, allowing each to scale efficiently according to their specific compute and memory constraints.

### Where is the bottleneck at 10x data volume? What breaks first?
At 10x data volume (e.g., uploading massive 500MB+ zip exports), the immediate bottleneck is the **synchronous embedding loop** inside the FastAPI background task. While using local `fastembed` eliminates network bottlenecks, generating 100,000+ dense vectors concurrently on a single small Render server (with 0.1 CPU and 512MB RAM) will severely bottleneck CPU and eventually exhaust the 512MB memory limit, causing the container to OOM (Out of Memory) crash. 

### What did you consciously cut to stay in the 4 to 6 hour window, and what would you build next?
To stay within the timeframe, I cut **Asynchronous Task Queues** and **Multi-Tenancy**. Right now, the file upload and ingestion run as a simple FastAPI background task, and the Qdrant index is a single pool of data. If I had more time, I would build a distributed Celery/Redis queue to handle massive concurrent uploads without locking the web server, and I would add User IDs to the Qdrant payloads to filter queries securely by user.

### If you had to make this architecture 10x better (not iterate on it, but rethink it), what would you change and why?
I would completely rethink ingestion by moving to an **Event-Driven Architecture**. Instead of forcing users to manually download and upload static `.zip` files (which are instantly stale), I would set up OAuth integrations to stream data directly from the social platforms via webhooks or daily polling into an event bus like **Kafka**. A scalable pool of worker microservices would consume these events, embed them, and sink them into Qdrant asynchronously. This ensures the vector DB is always a real-time, living reflection of the user's digital footprint.
