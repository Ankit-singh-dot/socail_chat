import os
from typing import List
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest_models
from fastembed import TextEmbedding
from models import Chunk

class VectorStore:
    def __init__(self, collection_name="social_data_local"):
        # Initialize FastEmbed 
        print("Loading local embedding model...")
        self.embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        
        
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        
        if qdrant_url == 'memory':
            self.qdrant = QdrantClient(":memory:")
        else:
            try:
                self.qdrant = QdrantClient(url=qdrant_url)
            except Exception as e:
                print(f"Failed to connect to Qdrant at {qdrant_url}. Using memory instead. Error: {e}")
                self.qdrant = QdrantClient(":memory:")

        self.collection_name = collection_name
        self.vector_size = 384  # BAAI/bge-small-en-v1.5 dimension
        self._ensure_collection()

    def _ensure_collection(self):
        try:
            collections = self.qdrant.get_collections().collections
            if not any(c.name == self.collection_name for c in collections):
                self.qdrant.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=rest_models.VectorParams(
                        size=self.vector_size, 
                        distance=rest_models.Distance.COSINE
                    ),
                )
                
                self.qdrant.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="content_hash",
                    field_schema=rest_models.PayloadSchemaType.KEYWORD,
                )
        except Exception as e:
            print(f"Error ensuring collection exists: {e}")

    def embed_chunks(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        
        embeddings = list(self.embedding_model.embed(texts))
        return [embedding.tolist() for embedding in embeddings]

    def upsert_chunks(self, chunks: List[Chunk], batch_size=100) -> int:
        
        if not chunks:
            return 0

        total_upserted = 0
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]
            
            new_chunks = []
            for chunk in batch:
                result = self.qdrant.scroll(
                    collection_name=self.collection_name,
                    scroll_filter=rest_models.Filter(
                        must=[
                            rest_models.FieldCondition(
                                key="content_hash",
                                match=rest_models.MatchValue(value=chunk.content_hash)
                            )
                        ]
                    ),
                    limit=1,
                    with_payload=False,
                    with_vectors=False
                )
                
                if not result[0]:
                    new_chunks.append(chunk)

            if not new_chunks:
                continue

            texts = [c.content for c in new_chunks]
            embeddings = self.embed_chunks(texts)
            
            if not embeddings:
                print("Failed to generate embeddings. Skipping upsert.")
                continue

            points = []
            for j, chunk in enumerate(new_chunks):
                payload = chunk.model_dump()
                if payload['created_at']:
                    payload['created_at'] = payload['created_at'].isoformat()
                    
                import uuid
                # Use a deterministic UUID based on the hash so we can re-run safely if needed
                point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk.content_hash))
                
                points.append(rest_models.PointStruct(
                    id=point_id,
                    vector=embeddings[j],
                    payload=payload
                ))
            
            self.qdrant.upsert(
                collection_name=self.collection_name,
                points=points
            )
            total_upserted += len(new_chunks)
            
        return total_upserted

    def search(self, query: str, limit: int = 5) -> List[dict]:
        query_vector = self.embed_chunks([query])[0]
        
        search_result = self.qdrant.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            with_payload=True
        ).points
        
        results = []
        for scored_point in search_result:
            results.append({
                "score": scored_point.score,
                "payload": scored_point.payload
            })
            
        return results
