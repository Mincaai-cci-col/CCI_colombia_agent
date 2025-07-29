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
    top_k: int = 3,
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
        
        # Extract relevant documents
        documents = []
        for match in results.matches:
            if match.metadata:
                # Try different metadata fields for text content
                text_content = (
                    match.metadata.get('text') or 
                    match.metadata.get('content') or 
                    match.metadata.get('document') or 
                    str(match.metadata)
                )
                documents.append(text_content)
        
        if not documents:
            if lang == "es":
                return "No encontré información específica sobre este tema en nuestra base de conocimientos."
            else:
                return "Je n'ai pas trouvé d'informations spécifiques sur ce sujet dans notre base de connaissances."
        
        # Reformulate response with OpenAI
        context = "\n\n".join(documents)
        
        if lang == "es":
            system_prompt = """Eres un asistente experto de la CCI Francia-Colombia. 
            Basándote en la información proporcionada, responde de manera clara, útil y profesional.
            Reformula la información de manera natural y conversacional."""
        else:
            system_prompt = """Tu es un assistant expert de la CCI France-Colombie. 
            En te basant sur les informations fournies, réponds de manière claire, utile et professionnelle.
            Reformule les informations de manière naturelle et conversationnelle."""
        
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Question: {query}\n\nInformations: {context}"}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        error_msg = f"Erreur lors de la recherche RAG : {str(e)}"
        if lang == "es":
            error_msg = f"Error durante la búsqueda RAG: {str(e)}"
        return error_msg
