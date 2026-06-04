import os
from groq import Groq
from vector_store import VectorStore
from models import QueryResponse

class RAGService:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        
        api_key = os.getenv("GROQ_API_KEY")
        self.groq_client = Groq(api_key=api_key) if api_key else None
        
    def query(self, user_question: str) -> QueryResponse:
        if not self.groq_client:
            return QueryResponse(
                answer="Groq API Key not configured. Please set GROQ_API_KEY environment variable.",
                sources=[]
            )
            
        # 1. Retrieve context from Qdrant
        search_results = self.vector_store.search(user_question, limit=5)
        
        if not search_results:
            return QueryResponse(
                answer="I couldn't find any relevant information in the knowledge base to answer your question.",
                sources=[]
            )
            
        # 2. Format Context
        context_parts = []
        sources = []
        for i, res in enumerate(search_results):
            payload = res['payload']
            content = payload.get('content', '')
            platform = payload.get('platform') or 'unknown'
            date = payload.get('created_at') or 'unknown date'
            source_file = payload.get('source_file') or 'unknown file'
            
            context_parts.append(f"[Source {i+1}] ({platform}, {date}): {content}")
            
            sources.append({
                "platform": platform,
                "date": date,
                "excerpt": content[:100] + "..." if len(content) > 100 else content,
                "source_file": source_file,
                "relevance_score": res['score']
            })
            
        context_str = "\n\n".join(context_parts)
        
        # 3. Construct Prompt
        system_prompt = """
        You are an AI assistant answering questions based strictly on the provided knowledge base.
        Your answer must be grounded *only* in the Context below. If the answer is not in the context, say you don't know.
        Be helpful and conversational. If the context contains related information (like a question or a fact) even if it's not a direct opinion, summarize what the context says about the topic!
        Use [Source X] citations inline in your answer when referencing facts from the context.
        """
        
        user_prompt = f"Context:\n{context_str}\n\nQuestion: {user_question}"
        
        # 4. Call LLM
        try:
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model="llama-3.1-8b-instant",
                temperature=0.0,
            )
            answer_text = response.choices[0].message.content
        except Exception as e:
            print(f"LLM Error: {e}")
            answer_text = "Sorry, there was an error generating the answer."
        
        return QueryResponse(
            answer=answer_text,
            sources=sources
        )
