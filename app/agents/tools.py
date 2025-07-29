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
        response = await query_rag(query, current_lang)
        return response
    except Exception as e:
        error_msg = f"Erreur lors de la recherche : {str(e)}"
        if get_current_language() == "es":
            error_msg = f"Error en la búsqueda: {str(e)}"
        return error_msg

# =============================================================================
# DIAGNOSTIC COLLECTION TOOL
# =============================================================================

@tool
def collect_diagnostic_answer(answer: str, question_number: int) -> str:
    """
    Collecte et sauvegarde une réponse au questionnaire d'accompagnement.
    
    Utilise cette fonction SEULEMENT quand l'utilisateur répond à une des 8 questions du questionnaire.
    Ne l'utilise PAS pour les questions générales sur la CCI.
    
    Args:
        answer: Réponse complète de l'utilisateur à la question
        question_number: Numéro de la question (1 à 8)
        
    Returns:
        Confirmation de la collecte
    """
    try:
        # The agent will handle the actual storage via _process_tool_calls
        success_msg = f"✅ Réponse collectée pour la question {question_number}: '{answer}'"
        if get_current_language() == "es":
            success_msg = f"✅ Respuesta recopilada para la pregunta {question_number}: '{answer}'"
        return success_msg
    except Exception as e:
        error_msg = f"Erreur collecte : {str(e)}"
        if get_current_language() == "es":
            error_msg = f"Error en recopilación: {str(e)}"
        return error_msg

# =============================================================================
# DIAGNOSTIC PROGRESS TOOL
# =============================================================================

def create_progress_tool(agent_ref: Optional[Any] = None):
    """
    Create diagnostic progress tool with agent reference.
    
    Args:
        agent_ref: Reference to the agent instance
        
    Returns:
        LangChain tool function
    """
    @tool
    def get_diagnostic_progress() -> str:
        """
        Vérifie l'état d'avancement du questionnaire d'accompagnement.
        
        Utilise cette fonction pour savoir :
        - À quelle question on en est (1 à 8)
        - Combien de réponses ont été collectées
        - Un résumé des dernières réponses
        
        Returns:
            État détaillé du questionnaire
        """
        try:
            if agent_ref is None:
                return "Agent non disponible"
            
            status = agent_ref.get_status()
            
            if get_current_language() == "es":
                progress_info = f"""ESTADO DEL CUESTIONARIO:
- Pregunta actual: {status['current_question']}/8
- Respuestas recopiladas: {status['answers_collected']}
- Idioma detectado: {status['detected_language']}
- Últimas respuestas: {', '.join([ans['answer'][:50] + '...' if len(ans['answer']) > 50 else ans['answer'] for ans in status['diagnostic_answers'][-2:]]) if status['diagnostic_answers'] else 'Ninguna aún'}"""
            else:
                progress_info = f"""ÉTAT DU DIAGNOSTIC :
- Question actuelle : {status['current_question']}/8
- Réponses collectées : {status['answers_collected']}
- Langue détectée : {status['detected_language']}
- Dernières réponses : {', '.join([ans['answer'][:50] + '...' if len(ans['answer']) > 50 else ans['answer'] for ans in status['diagnostic_answers'][-2:]]) if status['diagnostic_answers'] else 'Aucune encore'}"""
            
            return progress_info
            
        except Exception as e:
            error_msg = f"Erreur état diagnostic : {str(e)}"
            if get_current_language() == "es":
                error_msg = f"Error estado cuestionario: {str(e)}"
            return error_msg
    
    return get_diagnostic_progress

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
        collect_diagnostic_answer
    ]
    
    # Add dynamic progress tool with agent reference
    tools.append(create_progress_tool(agent_ref))
    
    return tools 