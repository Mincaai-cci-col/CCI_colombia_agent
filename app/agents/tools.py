"""
Tools for CCI LangChain Agent
All tools/functions that the agent can use
Bilingual support French/Spanish
"""

from langchain.tools import tool
from app.agents.rag import query_rag
from typing import Optional, Any

# Global variable to store detected language (will be updated by agent)
_current_language = "fr"

def set_tools_language(lang: str) -> None:
    """
    Update language for all tools.
    
    Args:
        lang: Language code ("fr" or "es")
    """
    global _current_language
    _current_language = lang
    print(f"🔧 Tools language set to: {lang}")

def get_current_language() -> str:
    """
    Get current language for tools.
    
    Returns:
        str: Current language code
    """
    return _current_language

# =============================================================================
# RAG TOOL
# =============================================================================

@tool
async def rag_search_tool(query: str) -> str:
    """
    Recherche d'informations sur la CCI France-Colombie avec RAG (Retrieval Augmented Generation).
    
    Utilise cette fonction pour répondre aux questions sur :
    - Les services de la CCI
    - L'histoire et mission de la CCI
    - Les événements et activités
    - Les contacts et informations pratiques
    - Tout ce qui concerne la CCI France-Colombie
    
    Args:
        query: Question ou mot-clé à rechercher
        
    Returns:
        Réponse informative basée sur la base de connaissances CCI
    """
    try:
        current_lang = get_current_language()
        print(f"🔍 RAG Search Query: '{query}' (lang: {current_lang})")
        
        response = await query_rag(query, current_lang)
        
        # Log the RAG result
        print(f"📚 RAG Result from Knowledge Base:")
        print(f"   Query: {query}")
        print(f"   Response: {response[:200]}{'...' if len(response) > 200 else ''}")
        print("   " + "="*50)
        
        return response
    except Exception as e:
        error_msg = f"Erreur lors de la recherche : {str(e)}"
        if get_current_language() == "es":
            error_msg = f"Error en la búsqueda: {str(e)}"
        print(f"❌ RAG Error: {error_msg}")
        return error_msg

# =============================================================================
# QUESTION COUNTER TOOL - SIMPLE
# =============================================================================

@tool
def question_asked() -> str:
    """
    Marque qu'une question du questionnaire a été posée.
    
    Utilise cette fonction juste après avoir posé une question du questionnaire
    (pas pour les questions générales sur la CCI).
    
    Returns:
        Confirmation que la question a été comptée
    """
    try:
        success_msg = "✅ Question comptée"
        if get_current_language() == "es":
            success_msg = "✅ Pregunta contada"
        return success_msg
    except Exception as e:
        error_msg = f"Erreur : {str(e)}"
        if get_current_language() == "es":
            error_msg = f"Error: {str(e)}"
        return error_msg

# =============================================================================
# TOOLS FACTORY
# =============================================================================

def get_agent_tools(agent_ref: Optional[Any] = None):
    """
    Get all available tools for the agent.
    
    Args:
        agent_ref: Reference to agent instance for dynamic tool creation
        
    Returns:
        List of LangChain tools
    """
    tools = [
        rag_search_tool,
        question_asked
    ]
    
    return tools 