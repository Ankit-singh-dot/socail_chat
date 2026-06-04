from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import glob

from parsers import LinkedInParser, TwitterParser, InstagramParser
from chunker import SemanticChunker
from vector_store import VectorStore
from rag import RAGService
from models import QueryResponse

from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="Social Data RAG API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vector_store = VectorStore()
chunker = SemanticChunker()
rag_service = RAGService(vector_store)

class ChatRequest(BaseModel):
    query: str

class IngestResponse(BaseModel):
    status: str
    message: str

def process_ingestion(data_dir: str):
    
    if not os.path.exists(data_dir):
        print(f"Directory {data_dir} does not exist.")
        return

    print(f"Starting ingestion from {data_dir}")
    
    total_new_chunks = 0
    
    
    for filepath in glob.glob(f"{data_dir}/*"):
        if os.path.isdir(filepath):
            continue
            
        filename = os.path.basename(filepath).lower()
        parser = None
        
        if 'linkedin' in filename or filename.endswith('.csv'):
            parser = LinkedInParser(filepath)
        elif 'twitter' in filename or 'tweet' in filename:
            parser = TwitterParser(filepath)
        elif 'instagram' in filename or filename.endswith('.html'):
            parser = InstagramParser(filepath)
        elif filename.endswith('.json'):
            
            parser = TwitterParser(filepath)
            
        if not parser:
            print(f"Skipping {filename}, no suitable parser found.")
            continue
            
        print(f"Parsing {filename}...")
        
        doc_gen = parser.parse()
        
        chunks_batch = []
        for doc in doc_gen:
            doc_chunks = chunker.chunk_document(doc)
            chunks_batch.extend(doc_chunks)
            
            if len(chunks_batch) >= 100:
                new_added = vector_store.upsert_chunks(chunks_batch)
                total_new_chunks += new_added
                chunks_batch = []
                
        if chunks_batch:
            new_added = vector_store.upsert_chunks(chunks_batch)
            total_new_chunks += new_added
            
    print(f"Ingestion complete. Added {total_new_chunks} new chunks.")

@app.post("/ingest", response_model=IngestResponse)
async def ingest_data(background_tasks: BackgroundTasks):
    data_dir = os.path.join(os.path.dirname(__file__), "data_exports")
    os.makedirs(data_dir, exist_ok=True)
    
    background_tasks.add_task(process_ingestion, data_dir)
    
    return IngestResponse(
        status="processing",
        message=f"Started ingestion background task. Make sure exports are in {data_dir}"
    )

@app.post("/chat", response_model=QueryResponse)
async def chat(request: ChatRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
        
    return rag_service.query(request.query)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
