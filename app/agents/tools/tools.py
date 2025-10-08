"""
Tools for CCI LangChain Agent
All tools/functions that the agent can use
Bilingual support French/Spanish
"""

from langchain.tools import tool
from app.agents.tools.rag import query_rag
from typing import Optional, Any
from datetime import datetime
import pytz

# Global variables for performance optimization
_current_language = "fr"
# Timezone cache - safe for API environment as it's read-only and immutable
_colombia_tz = pytz.timezone('America/Bogota')

def set_tools_language(lang: str) -> None:
    """
    Update language for all tools.
    
    Args:
        lang: Language code ("fr" or "es")
    """
    # WARNING: This global approach is not thread-safe for API environment
    # The language should be passed as parameter to tools instead
    global _current_language
    _current_language = lang
    # print(f"🔧 Tools language set to: {lang}")  # Commented for performance

def get_current_language() -> str:
    """
    Get current language for tools.
    
    Returns:
        str: Current language code
    """
    # WARNING: This global approach is not thread-safe for API environment
    return _current_language

def get_colombia_current_date() -> str:
    """
    Get the current date and time in Colombia timezone.
    
    Returns:
        str: Simple formatted date and time (DD/MM/YYYY HH:MM)
    """
    # Use cached timezone object for better performance
    now = datetime.now(_colombia_tz)
    return now.strftime('%d/%m/%Y %H:%M')

# =============================================================================
# RAG TOOL
# =============================================================================

@tool
async def rag_search_tool(query: str) -> str:
    """
    Recherche d'informations dans la base de connaissances avec RAG (Retrieval Augmented Generation).
    
    Utilise cette fonction pour répondre aux questions sur :
    - Les services disponibles
    - L'histoire et mission
    - Les événements et activités
    - Les contacts et informations pratiques
    - Toute information générale
    
    Args:
        query: Question ou mot-clé à rechercher (utilise des termes simples et directs)
        
    Returns:
        Réponse informative basée sur la base de connaissances
    """
    try:
        # Use global language (not ideal for API but functional for now)
        # TODO: Refactor to pass language as parameter from agent context
        current_lang = get_current_language()
        # print(f"🔍 RAG Search Query: '{query}' (lang: {current_lang})")  # Commented for performance
        
        response = await query_rag(query, current_lang)
        
        # Log the RAG result (commented for performance)
        # print(f"📚 RAG Result from Knowledge Base:")
        # print(f"   Query: {query}")
        # print(f"   Response: {response[:200]}{'...' if len(response) > 200 else ''}")
        # print("   " + "="*50)
        
        return response
    except Exception as e:
        # Cache language check for better performance
        current_lang = get_current_language()
        if current_lang == "es":
            error_msg = f"Error en la búsqueda: {str(e)}"
        else:
            error_msg = f"Erreur lors de la recherche : {str(e)}"
        # print(f"❌ RAG Error: {error_msg}")  # Commented for performance
        return error_msg

# Question counter tool removed - using natural conversation flow instead

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
        rag_search_tool
    ]
    
    return tools 