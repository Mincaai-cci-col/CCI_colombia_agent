"""
RAG (Retrieval Augmented Generation) for CCI France-Colombia
Integrates Pinecone vector database with OpenAI for intelligent information retrieval
"""

import os
import asyncio
from typing import List, Dict, Any
from openai import AsyncOpenAI
from pinecone import Pinecone

def get_pinecone_client():
    """
    Initialize Pinecone client with environment variables.
    
    Returns:
        Pinecone client instance
    """
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        raise ValueError("PINECONE_API_KEY environment variable not set")
    
    # Optional environment parameter
    environment = os.getenv("PINECONE_ENV")
    if environment:
        return Pinecone(api_key=api_key, environment=environment)
    else:
        return Pinecone(api_key=api_key)

async def get_embedding(text: str) -> List[float]:
    """
    Generate embedding for text using OpenAI.
    
    Args:
        text: Text to embed
        
    Returns:
        List of floats representing the embedding
    """
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    
    return response.data[0].embedding

async def query_rag(
    query: str,
    lang: str,
    top_k: int = 2,  # Réduit à 2 pour serverless (moins de données à traiter)
    namespace: str = None
) -> str:
    """
    Simple and efficient RAG query.
    
    Args:
        query: User query
        lang: Language for response ("fr" or "es")
        top_k: Number of documents to retrieve
        namespace: Optional Pinecone namespace
        
    Returns:
        str: Reformulated response based on retrieved documents
    """
    try:
        # Generate embedding for the query
        query_embedding = await get_embedding(query)
        
        # Initialize Pinecone and query
        client = get_pinecone_client()
        index_name = os.getenv("PINECONE_INDEX")
        
        if not index_name:
            raise ValueError("PINECONE_INDEX environment variable not set")
        
        index = client.Index(index_name)
        
        # Prepare search parameters
        search_params = {
            "vector": query_embedding,
            "top_k": top_k,
            "include_metadata": True
        }
        
        if namespace:
            search_params["namespace"] = namespace
        
        # Execute search
        results = index.query(**search_params)
        
        # Extract only essential text content, very compact
        context_parts = []
        for match in results.matches:
            if match.metadata and match.score > 0.7:  # Only high-quality matches
                # Get text content only
                text = (match.metadata.get('text') or 
                       match.metadata.get('content') or 
                       match.metadata.get('document', ''))
                if text:
                    # Keep only first 200 chars per document
                    context_parts.append(text[:200])
        
        context = " | ".join(context_parts)[:400]  # Max 400 chars total
        
        if lang == "es":
            system_prompt = "Eres MarIA de CCI Francia-Colombia. Usa el contexto para responder. Si no hay info suficiente: Bogotá: Valentina (+57 304 423 6731), Medellín: Laura (+57 304 400 2871)"
        else:
            system_prompt = "Tu es MarIA de CCI France-Colombie. Utilise le contexte pour répondre. Si pas assez d'info: Bogotá: Valentina (+57 304 423 6731), Medellín: Laura (+57 304 400 2871)"
        
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",  # Plus rapide que gpt-4.1-mini pour serverless
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{query}\n\nInfo: {context}"}  # Format ultra-compact
            ],
            temperature=0.1,  # Encore plus déterministe
            max_tokens=200    # Réduit encore plus
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        error_msg = f"Erreur lors de la recherche RAG : {str(e)}"
        if lang == "es":
            error_msg = f"Error durante la búsqueda RAG: {str(e)}"
        return error_msg
