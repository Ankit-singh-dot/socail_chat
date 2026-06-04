import hashlib
from typing import List
from models import NormalizedDocument, Chunk

class SemanticChunker:
    
    def __init__(self, max_chunk_size=1500):
        self.max_chunk_size = max_chunk_size

    def chunk_document(self, doc: NormalizedDocument) -> List[Chunk]:
        content = doc.content.strip()
        if not content:
            return []

        chunks = []
        
        # Determine if we need to split based on length
        if len(content) <= self.max_chunk_size:
            # Already small enough, semantic boundary = the whole post
            chunks.append(content)
        else:
            # It's a long article or post, split by paragraphs
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            current_chunk = ""
            for p in paragraphs:
                if len(current_chunk) + len(p) < self.max_chunk_size:
                    current_chunk += p + "\n\n"
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    
                    if len(p) > self.max_chunk_size:
                        
                        for i in range(0, len(p), self.max_chunk_size):
                            chunks.append(p[i:i+self.max_chunk_size])
                        current_chunk = ""
                    else:
                        current_chunk = p + "\n\n"
            
            if current_chunk:
                chunks.append(current_chunk.strip())

        
        result_chunks = []
        for i, chunk_text in enumerate(chunks):
            
            hash_input = f"{doc.platform}_{doc.id}_{i}_{chunk_text}"
            content_hash = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
            
            result_chunks.append(Chunk(
                chunk_id=f"{doc.id}_{i}",
                doc_id=doc.id,
                platform=doc.platform,
                source_type=doc.source_type,
                content=chunk_text,
                content_hash=content_hash,
                chunk_index=i,
                created_at=doc.created_at,
                author=doc.author
            ))
            
        return result_chunks
