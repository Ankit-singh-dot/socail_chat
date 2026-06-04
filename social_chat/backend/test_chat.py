import os
from dotenv import load_dotenv
load_dotenv()
from vector_store import VectorStore
from rag import RAGService

v = VectorStore()
r = RAGService(v)
print(r.query("remote work").model_dump_json())
