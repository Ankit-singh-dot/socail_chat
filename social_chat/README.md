# Social Knowledge Base Architecture

## What does your system do, and what are the two or three most important architecture decisions you made?
This system ingests data exports from LinkedIn, Twitter, and Instagram, stores them in a highly optimized vector knowledge base, and serves grounded answers to user questions via a Next.js chat interface. 
Three critical architecture decisions:
1. **The Normalization Layer**: Instead of forcing the Vector DB to understand three different data models, all parsers pipe into a unified `NormalizedDocument` schema. Adding a fourth source (like Reddit) simply requires a new parser outputting this schema—no downstream changes needed.
2. **Incremental Upserts via Content Hashing**: Instead of blindly re-embedding a 50MB LinkedIn export every time, the chunker generates a SHA-256 hash of the content. We query Qdrant for this hash first; if it exists, we skip it. This saves massive API costs and processing time.
3. **No LangChain & Qdrant Choice**: I built a custom pipeline (`Parser -> Normalizer -> Chunker -> Vector Store -> Retriever -> LLM`) to ensure full control over the ingestion mechanics and citations without relying on opaque abstractions. Qdrant was chosen over Chroma because its metadata filtering and payload indexing are production-grade.

## Where is the bottleneck at 10x data volume? What breaks first?
At 10x data volume (e.g., 500MB+ of CSV/JSON), the immediate bottleneck is the **synchronous embedding generation and upsert loop** within the FastAPI backend process. Even though we batch, keeping this loop tied to a single Python thread/process doing sequential HTTP calls to Gemini API will eventually throttle or time out. Memory is less of a concern because we use generators to read files, but the network I/O for embeddings will choke the system. 

## What did you consciously cut to stay in the 4 to 6 hour window, and what would you build next?
1. **Asynchronous Task Queues**: I cut Celery/Redis for background processing. Right now, ingestion runs in a FastAPI background task. Next, I would offload parsing and embedding to a distributed Celery queue to handle massive concurrent uploads.
2. **Authentication & Multi-Tenancy**: The current Qdrant index is a single pool of data. I cut multi-tenancy. Next, I would add User IDs to the Qdrant payload and filter by `user_id` at query time.
3. **Advanced RAG (Hybrid Search/Reranking)**: I used standard cosine similarity. Next, I'd implement hybrid search (BM25 + Dense) and a reranker (like Cohere) to improve retrieval accuracy.

## If you had to make this architecture 10x better (not iterate on it, but rethink it), what would you change and why?
I would completely decouple ingestion into an event-driven architecture. 
Instead of users uploading static zips, I would set up OAuth integrations to stream data directly from platforms (via webhooks or daily polling) into an event bus like **Kafka**. A scalable pool of worker microservices would consume these events, parse them, embed them, and sink them into Qdrant asynchronously. This eliminates the "upload a 50MB CSV" problem entirely, ensuring the vector DB is always a real-time, living reflection of the user's digital footprint.
