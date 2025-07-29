"""
Tools pour l'agent LangChain CCI
Tous les outils/fonctions que l'agent peut utiliser
Support bilingue français/espagnol
"""

from langchain.tools import tool
from app.agents.rag import query_rag
from typing import Optional, Any

# Variable globale pour stocker la langue détectée (sera mise à jour par l'agent)
_current_language = "fr"

def set_tools_language(lang: str) -> None:
    """
    Définit la langue courante pour tous les tools
    
    Args:
        lang: Langue à utiliser ("fr" ou "es")
    """
    global _current_language
    _current_language = lang

def get_tools_language() -> str:
    """
    Retourne la langue courante des tools
    
    Returns:
        str: Langue courante
    """
    global _current_language
    return _current_language

# =============================================================================
# TOOLS PRINCIPAUX
# =============================================================================

@tool
async def rag_search_tool(query: str) -> str:
    """
    Recherche d'informations spécifiques sur la CCI France-Colombie.
    
    Utilise ce tool pour répondre aux questions sur :
    - Les services de la CCI (formations, conseil, accompagnement, etc.)
    - Les événements et networking
    - Les contacts et conseillers
    - L'espace membre et son accès
    - Les offres et programmes spécifiques
    - Les modalités d'adhésion
    - Les informations pratiques CCI
    
    Args:
        query: La question ou recherche à effectuer sur la CCI
        
    Returns:
        str: Informations trouvées dans la base de connaissances CCI
    """
    try:
        # Utiliser la langue détectée par l'agent
        current_lang = get_tools_language()
        # Utiliser le RAG simple
        result = await query_rag(
            query=query,
            lang=current_lang
        )
        return result
    except Exception as e:
        if get_tools_language() == "es":
            return f"Disculpe, no pude buscar esta información en este momento. Error: {str(e)}"
        else:
            return f"Désolé, impossible de rechercher cette information pour le moment. Erreur: {str(e)}"

@tool 
def collect_diagnostic_answer(answer: str, question_number: int) -> str:
    """
    Collecte une réponse au diagnostic relationnel.
    
    Utilise ce tool UNIQUEMENT quand l'utilisateur répond clairement 
    à une question spécifique du diagnostic.
    
    Args:
        answer: La réponse exacte de l'utilisateur
        question_number: Le numéro de la question (1-8)
        
    Returns:
        str: Confirmation de la collecte
    """
    if get_tools_language() == "es":
        return f"✅ Respuesta recopilada para la pregunta {question_number}: '{answer}'"
    else:
        return f"✅ Réponse collectée pour la question {question_number}: '{answer}'"

def create_progress_tool(agent_ref: Optional[Any] = None):
    """
    Crée dynamiquement le tool de progression avec accès à l'état interne de l'agent si fourni.
    """
    from langchain.tools import tool
    
    @tool
    def get_diagnostic_progress() -> str:
        """Obtient le progrès actuel du diagnostic"""
        if agent_ref is not None:
            progress = f"""ÉTAT DU DIAGNOSTIC :\n- Question actuelle : {agent_ref.current_question}/8\n- Réponses collectées : {len(agent_ref.diagnostic_answers)}\n- Langue détectée : {agent_ref.detected_language}\n- Dernières réponses : {[r['answer'] for r in agent_ref.diagnostic_answers[-3:]] if agent_ref.diagnostic_answers else 'Aucune encore'}"""
            return progress
        # fallback générique
        if get_tools_language() == "es":
            return "Usa esta herramienta para conocer el progreso del diagnóstico"
        else:
            return "Utilise ce tool pour connaître le progrès du diagnostic"
    return get_diagnostic_progress


# =============================================================================
# TOOLS UTILITAIRES (pour extensions futures)
# =============================================================================

@tool
def check_user_eligibility(membership_type: str) -> str:
    """
    Vérifie l'éligibilité d'un utilisateur selon son type d'adhésion.
    
    Args:
        membership_type: Type d'adhésion (membre, partenaire, etc.)
        
    Returns:
        str: Informations sur l'éligibilité
    """
    if get_tools_language() == "es":
        eligibility_info = {
            "membre": "Acceso completo a todos los servicios de la CCI",
            "partenaire": "Acceso privilegiado a eventos y servicios premium", 
            "prospect": "Acceso a información general y eventos públicos"
        }
        return eligibility_info.get(membership_type, "Tipo de membresía no reconocido")
    else:
        eligibility_info = {
            "membre": "Accès complet à tous les services CCI",
            "partenaire": "Accès privilégié aux événements et services premium", 
            "prospect": "Accès aux informations générales et événements publics"
        }
        return eligibility_info.get(membership_type, "Type d'adhésion non reconnu")

@tool
def schedule_callback(contact_info: str, topic: str) -> str:
    """
    Programme un rappel avec un conseiller CCI.
    
    Args:
        contact_info: Informations de contact de l'utilisateur
        topic: Sujet pour lequel l'utilisateur souhaite être recontacté
        
    Returns:
        str: Confirmation de la demande de rappel
    """
    if get_tools_language() == "es":
        return f"✅ Solicitud de llamada registrada para '{topic}'. Contacto: {contact_info}"
    else:
        return f"✅ Demande de rappel enregistrée pour '{topic}'. Contact: {contact_info}"

# =============================================================================
# LISTE DES TOOLS POUR L'AGENT
# =============================================================================

def get_agent_tools(agent_ref: Optional[Any] = None):
    """
    Retourne la liste des tools disponibles pour l'agent.
    Si agent_ref est fourni, le tool de progression aura accès à l'état de l'agent.
    """
    tools = [
        rag_search_tool,
        collect_diagnostic_answer
    ]
    # Ajout dynamique du tool de progression
    tools.append(create_progress_tool(agent_ref))
    # Décommenter pour activer les tools utilitaires :
    # tools.append(check_user_eligibility)
    # tools.append(schedule_callback)
    return tools 