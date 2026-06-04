from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class NormalizedDocument(BaseModel):
    
    id: str  # Unique identifier for the document
    platform: str  # e.g., 'linkedin', 'twitter', 'instagram'
    source_type: str  # e.g., 'post', 'tweet', 'article', 'caption'
    content: str  # The raw text content
    created_at: Optional[datetime] = None
    author: Optional[str] = None
    source_file: str  # Which export file this came from

class Chunk(BaseModel):
    """
    Represents a piece of a document ready for embedding.
    """
    chunk_id: str
    doc_id: str
    platform: str
    source_type: str
    content: str
    content_hash: str  # Used for incremental upserts (deduplication)
    chunk_index: int
    created_at: Optional[datetime] = None
    author: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
