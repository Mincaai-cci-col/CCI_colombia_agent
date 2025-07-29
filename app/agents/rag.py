# Query to Pinecone and result processing 

import os
import logging
from typing import List
from pinecone import Pinecone
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

# Lazy client init
_pinecone_client = None

def get_pinecone_client() -> Pinecone:
    global _pinecone_client
    if _pinecone_client is None:
        PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
        if not PINECONE_API_KEY:
            logger.error("Missing PINECONE_API_KEY environment variable")
            raise ValueError("Missing Pinecone API key")
        
        # Optionnel : utiliser PINECONE_ENV si défini (pour certaines configurations)
        pinecone_env = os.getenv("PINECONE_ENV")
        if pinecone_env:
            logger.info(f"Using Pinecone environment: {pinecone_env}")
        
        _pinecone_client = Pinecone(api_key=PINECONE_API_KEY)
    return _pinecone_client

async def get_embedding(text: str) -> List[float]:
    """Génère l'embedding d'un texte avec OpenAI"""
    try:
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = await client.embeddings.create(
            input=text,
            model="text-embedding-3-small"  # Modèle d'embedding OpenAI
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Erreur génération embedding : {e}")
        raise

async def query_rag(
    query: str, 
    lang: str, 
    top_k: int = 3, 
    namespace: str = None
) -> str:
    """
    RAG complet avec Pinecone :
    1. Génère l'embedding de la requête
    2. Interroge Pinecone pour récupérer les documents pertinents
    3. Reformule la réponse avec OpenAI
    """
    try:
        # 1. Générer l'embedding de la requête
        query_embedding = await get_embedding(query)
        
        # 2. Configurer Pinecone
        client = get_pinecone_client()
        index_name = os.getenv("PINECONE_INDEX")
        if not index_name:
            raise ValueError("Missing PINECONE_INDEX environment variable")
        
        index = client.Index(index_name)
        
        # 3. Requête Pinecone
        search_params = {
            "vector": query_embedding,
            "top_k": top_k,
            "include_metadata": True
        }
        
        # Ajouter namespace si spécifié
        if namespace:
            search_params["namespace"] = namespace
            
        results = index.query(**search_params)
        
        # 4. Extraire les documents pertinents
        if not results.matches:
            return "Aucune information pertinente trouvée dans la base de connaissances CCI."
        
        # Récupérer le texte des documents (adapter selon votre structure metadata)
        documents = []
        for match in results.matches:
            # Essayer différents champs possibles pour le texte
            text = None
            if 'text' in match.metadata:
                text = match.metadata['text']
            elif 'content' in match.metadata:
                text = match.metadata['content']
            elif 'document' in match.metadata:
                text = match.metadata['document']
            
            if text:
                documents.append(f"Document (score: {match.score:.2f}): {text}")
        
        if not documents:
            return "Les documents trouvés ne contiennent pas de texte exploitable."
        
        # 5. Reformuler avec OpenAI
        context = "\n\n".join(documents)
        
        # Prompt système adapté à la langue
        if lang == "es":
            system_prompt = """Eres un asistente experto de la CCI Francia-Colombia. 
Responde de manera precisa y útil basándote únicamente en la información proporcionada.
Si la información no está disponible, dilo claramente."""
        else:
            system_prompt = """Tu es un assistant expert de la CCI France-Colombie.
Réponds de manière précise et utile en te basant uniquement sur les informations fournies.
Si l'information n'est pas disponible, dis-le clairement."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""Question : {query}

Informations disponibles dans la base CCI :
{context}

Réponds à la question en te basant sur ces informations."""}
        ]
        
        openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.2,
            max_tokens=500
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.error(f"Erreur RAG avec Pinecone : {e}")
        if lang == "es":
            return f"Disculpe, encontré un problema al buscar información. Error: {str(e)}"
        else:
            return f"Désolé, j'ai rencontré un problème lors de la recherche. Erreur: {str(e)}"
