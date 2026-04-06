# File: rag_system.py
"""
In-memory RAG system using OpenAI embeddings
Now loads Stripe documentation
"""

import numpy as np
from openai import OpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv()

def get_stripe_documents():
    """Load Stripe docs from stripe_knowledge_base.json"""
    with open('stripe_knowledge_base.json', 'r') as f:
        docs = json.load(f)
    
    # Convert to same format RAG expects
    formatted_docs = []
    for doc in docs:
        formatted_docs.append({
            "doc_id": doc["doc_id"],
            "title": doc["title"],
            "content": doc["content"],
            "url": doc["url"]
        })
    
    return formatted_docs

class StripeRAG:
    """
    Simple RAG system with in-memory vector store
    
    COMPONENTS:
    1. Embedding: Convert text to vectors using OpenAI
    2. Retrieval: Find most similar docs using cosine similarity
    3. Generation: Use GPT-4 to generate answer from retrieved docs
    """
    
    def __init__(self, embedding_model="text-embedding-3-small"):
        self.embedding_model = embedding_model
        """Initialize RAG system with Stripe documents"""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Load Stripe documents
        print("📚 Loading Stripe documentation...")
        self.documents = get_stripe_documents()
        print(f"✅ Loaded {len(self.documents)} Stripe documents")
        
        # Create embeddings for all documents
        print("🔄 Creating embeddings...")
        self.doc_embeddings = self._create_embeddings()
        print("✅ Embeddings created")
    
    def _create_embeddings(self):
        """Create embeddings for all documents"""
        embeddings = []
        
        for doc in self.documents:
            # Combine title and content for embedding
            text = f"{doc['title']}\n\n{doc['content']}"
            
            # Get embedding from OpenAI
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            
            embeddings.append(np.array(response.data[0].embedding))
        
        return embeddings
    
    def _get_query_embedding(self, query: str):
        """Get embedding for user query"""
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=query
        )
        return np.array(response.data[0].embedding)
    
    def _cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors"""
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    def retrieve(self, query: str, top_k: int = 3):
        """
        Retrieve most relevant documents for query
        
        PROCESS:
        1. Convert query to embedding
        2. Calculate similarity with all doc embeddings
        3. Return top K most similar docs
        
        Returns:
            List of (doc, similarity_score) tuples
        """
        # Get query embedding
        query_embedding = self._get_query_embedding(query)
        
        # Calculate similarities
        similarities = []
        for i, doc_embedding in enumerate(self.doc_embeddings):
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            similarities.append((self.documents[i], float(similarity)))
        
        # Sort by similarity and return top K
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def generate_answer(self, query: str, retrieved_docs: list):
        """
        Generate answer using GPT-4 based on retrieved documents
        
        Args:
            query: User question
            retrieved_docs: List of (doc, similarity) tuples
        
        Returns:
            Generated answer
        """
        # Prepare context from retrieved docs
        context = "\n\n---\n\n".join([
            f"Document: {doc['title']}\nContent: {doc['content']}"
            for doc, _ in retrieved_docs
        ])
        
        # Create prompt
        prompt = f"""You are a Stripe documentation assistant. Provide accurate, concise answers.

DOCUMENTATION:
{context}

USER QUESTION: {query}

ANSWER GUIDELINES:
1. STRUCTURE: Lead with the direct answer in 1-2 sentences, then add details if needed
2. PARTIAL INFO: If docs cover only part of the question, answer that part and clarify what's missing
3. OUT OF SCOPE: Only say "not in documentation" if truly nothing relevant exists
4. CONCISENESS: Keep answers focused - aim for 2-3 sentences unless complexity requires more
5. STRIPE SPECIFICITY: Use exact Stripe terminology (PaymentIntent, not "payment object")

ANSWER:""" 
        
        # Generate answer
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful Stripe documentation assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1  # Low temperature for consistency
        )
        
        return response.choices[0].message.content
    
    def query(self, question: str, top_k: int = 3):
        """
        Complete RAG query: retrieve + generate
        
        Args:
            question: User question
            top_k: Number of documents to retrieve
        
        Returns:
            Dictionary with answer and sources
        """
        # Retrieve relevant documents
        retrieved_docs = self.retrieve(question, top_k=top_k)
        
        # Generate answer
        answer = self.generate_answer(question, retrieved_docs)
        
        # Format sources for return
        sources = [
            {
                "doc_id": doc["doc_id"],
                "title": doc["title"],
                "similarity": similarity,
                "url": doc.get("url", "")
            }
            for doc, similarity in retrieved_docs
        ]
        
        return {
            "answer": answer,
            "sources": sources,
            "question": question
        }

# Test the system
if __name__ == "__main__":
    print("\n" + "="*70)
    print("TESTING STRIPE RAG SYSTEM")
    print("="*70)
    
    # Initialize RAG
    rag = StripeRAG()
    
    # Test query
    test_question = "How do I create a refund in Stripe?"
    print(f"\n❓ Question: {test_question}")
    
    result = rag.query(test_question, top_k=3)
    
    print(f"\n💬 Answer:\n{result['answer']}")
    
    print(f"\n📚 Sources:")
    for source in result['sources']:
        print(f"  - {source['title']} (similarity: {source['similarity']:.3f})")
        print(f"    {source['url']}")
