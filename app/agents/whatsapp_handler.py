"""
WhatsApp Handler for CCI Agent
Stateless wrapper for agent state management and WhatsApp deployment
Manages user state persistence for multi-turn conversations
"""

import asyncio
from typing import Dict, Any, Optional, Tuple, Literal
from app.agents.langchain_agent import CCILangChainAgent
from app.agents.prompts.prompts_utils import get_prompt_for_mode_and_language, load_prompt
import requests
import os

# Redis state management - replaces in-memory storage for production scalability
from app.agents.redis_manager import (
    load_user_state, 
    save_user_state, 
    get_redis_manager
)

async def reset_user_conversation(user_id: str) -> None:
    """
    Reset user's conversation (new conversation).
    
    Args:
        user_id: Unique user identifier
    """
    manager = get_redis_manager()
    await manager.delete_user_state(user_id)

async def get_user_status(user_id: str) -> Dict[str, Any]:
    """
    Get user's conversation status.
    
    Args:
        user_id: Unique user identifier
        
    Returns:
        Dict containing user status information
    """
    state = await load_user_state(user_id)
    if not state:
        return {
            "exists": False,
            "current_question": 1,
            "answers_collected": 0,
            "language": "fr"
        }
    
    return {
        "exists": True,
        "current_question": state.get("current_question", 1),
        "answers_collected": state.get("questions_asked", 0),  # Use questions_asked from state
        "language": state.get("detected_language", "fr"),
        "diagnostic_complete": state.get("current_question", 1) > 8
    }

async def get_redis_stats() -> Dict[str, Any]:
    """
    Get Redis connection and usage statistics.
    
    Returns:
        dict: Redis statistics
    """
    manager = get_redis_manager()
    return manager.get_stats()

async def whatsapp_chat(user_id: str, user_input: str) -> str:
    """
    Main function for WhatsApp conversations with dual mode support.
    Handles questionnaire mode (default) and assistance mode (after questionnaire completion).
    Stateless: loads state, processes message, saves state.
    
    Args:
        user_id: Unique user identifier (WhatsApp phone number)
        user_input: User's message
        
    Returns:
        Agent's response
    """
    try:
        # Load existing user state (no restart triggers needed)
        user_state = await load_user_state(user_id)
        
        # Determine agent mode and appropriate prompt
        agent_mode, prompt_name = await determine_agent_mode_and_prompt(user_state, user_input)
        
        if user_state:
            # Restore agent from saved state with appropriate prompt
            agent = CCILangChainAgent(prompt_name=prompt_name)
            agent.load_state(user_state)
            
            # Update mode if it changed (e.g., transition to assistance)
            agent.agent_mode = agent_mode
        else:
            # Create new agent for new user (questionnaire mode by default)
            agent = CCILangChainAgent(prompt_name=prompt_name)
            agent.agent_mode = agent_mode
            
            # For new users, try to set client context from contact database
            contact_info = await get_contact_info(user_id)
            if contact_info:
                agent.set_client_context(contact_info)
        
        # Process user message
        response = await agent.chat(user_input, user_id)
        
        # Check if questionnaire should transition to assistance
        if agent.agent_mode == "questionnaire" and should_transition_to_assistance_mode(response):
            agent.mark_questionnaire_completed()
            
            # CRITIQUE: Rebuild agent avec le nouveau prompt assistance
            new_prompt_name = get_prompt_for_mode_and_language("assistance", agent.detected_language)
            try:
                agent.base_system_prompt = load_prompt(new_prompt_name)
                agent.base_prompt_name = new_prompt_name
                agent.prompt = agent._build_dynamic_prompt()
                agent._rebuild_agent()
                pass  # Silent transition for performance
            except Exception as e:
                pass  # Silent error for performance
        
        # Save updated state
        new_state = agent.serialize_state()
        await save_user_state(user_id, new_state)
        
        return response
        
    except Exception as e:
        return f"Désolé, j'ai rencontré un problème technique. Pouvez-vous réessayer ?"

async def get_contact_info(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve contact information for a WhatsApp user ID.
    
    Args:
        user_id: WhatsApp phone number
        
    Returns:
        Dict with contact information or None if not found
    """
    # try:
    #     from whatsapp_contact.contacts_manager import get_contacts_manager
    #     contacts_manager = get_contacts_manager()
        
    #     if not contacts_manager.contacts_loaded:
    #         # Try to load contacts if not already loaded
    #         # You can set a default path here or use environment variable
    #         import os
    #         excel_path = os.getenv('CONTACTS_EXCEL_PATH', 'whatsapp_contact/Base de datos proyecto IA (1).xlsx')
    #         contacts_manager.load_contacts(excel_path)
        
    #     if contacts_manager.contacts_loaded:
    #         contact_info = contacts_manager.find_contact_by_phone(user_id)
    #         if contact_info:
    #             print(f"📇 Contact trouvé pour {user_id}: {contact_info.get('empresa', 'Entreprise inconnue')}")
    #             return contact_info
    #         else:
    #             print(f"📇 Aucun contact trouvé pour {user_id}")
    #     else:
    #         print("⚠️ Base de données de contacts non disponible")
            
    # except Exception as e:
    #     print(f"⚠️ Erreur lors de la recherche de contact : {e}")
    
    backend_url = os.getenv('BACKEND_URL')
    if not backend_url:
        # No backend URL configured - skip contact lookup (for testing)
        return None
    
    try:
        response = requests.get(f"{backend_url}/api/v1/whatsapp/info/{user_id}")
        if response.status_code == 200:
            contact_info = response.json()
            if contact_info:
                return contact_info if contact_info else None
    except Exception as e:
        pass  # Silent error for performance
    
    return None

def configure_contacts_database(excel_file_path: str) -> bool:
    """
    Configure the contacts database with a specific Excel file.
    
    Args:
        excel_file_path: Path to the contacts Excel file
        
    Returns:
        bool: True if configuration successful
    """
    try:
        contacts_manager = get_contacts_manager()
        return contacts_manager.load_contacts(excel_file_path)
    except Exception as e:
        print(f"❌ Erreur configuration base contacts : {e}")
        return False

async def determine_agent_mode_and_prompt(user_state: Optional[Dict[str, Any]], user_input: str) -> Tuple[Literal["questionnaire", "assistance"], str]:
    """
    Determine the appropriate agent mode and prompt based on user state.
    
    Simple logic:
    - Default mode: questionnaire
    - Assistance mode: only if questionnaire was completed (WhatsApp link sent)
    
    Args:
        user_state: Current user state from Redis
        user_input: Current user message (not used in decision)
        
    Returns:
        Tuple of (agent_mode, prompt_name)
    """
    # Default language
    detected_language = "fr"
    
    if user_state:
        detected_language = user_state.get("detected_language", "fr")
        questionnaire_completed = user_state.get("questionnaire_completed", False)
        
        if questionnaire_completed:
            # User has completed questionnaire (WhatsApp link was sent) → assistance mode
            mode = "assistance"
        else:
            # Questionnaire not completed → questionnaire mode
            mode = "questionnaire"
    else:
        # New user → questionnaire mode by default
        mode = "questionnaire"
    
    # Get appropriate prompt name
    prompt_name = get_prompt_for_mode_and_language(mode, detected_language)
    
    return mode, prompt_name

def should_transition_to_assistance_mode(agent_response: str) -> bool:
    """
    Analyze agent response to determine if questionnaire is completed based on actual prompt patterns.
    Supports both French and Spanish patterns.
    
    Args:
        agent_response: The agent's response to analyze
        
    Returns:
        bool: True if transition to assistance mode should occur
    """
    response_lower = agent_response.lower()
    
    # Patterns from the actual prompts that indicate final recommendations
    final_recommendation_patterns = [
        # French patterns
        "je vous recommande vivement",
        "je vous recommande notre service",
        "je pense que notre service",
        "je pense que le service",
        "super ! je pense que le service",
        # Spanish patterns
        "te recomiendo encarecidamente",
        "te recomiendo nuestro servicio",
        "creo que nuestro servicio",
        "creo que el servicio",
        "¡súper! creo que el servicio"
    ]
    
    # Next step patterns that indicate final recommendation
    next_step_patterns = [
        # French patterns
        "🚀 la suite est simple",
        "🚀 la prochaine étape",
        "👉 la prochaine étape",
        "la suite est très simple",
        "écrivez directement à",
        # Spanish patterns
        "🚀 la continuación es simple",
        "🚀 el siguiente paso",
        "👉 el siguiente paso",
        "la continuación es muy simple",
        "escribe directamente a"
    ]
    
    # WhatsApp contact patterns (definitive sign of final recommendation)
    whatsapp_patterns = [
        "https://wa.me/",
        "wa.me/",
        "whatsapp"
    ]
    
    # Contact person patterns (same names in both languages)
    contact_patterns = [
        "yasmine azlabi",
        "nicolás velásquez", 
        "valentina copete",
        "laura morales",
        "anouk esnault"
    ]
    
    # Check for recommendation patterns
    has_recommendation = any(pattern in response_lower for pattern in final_recommendation_patterns)
    
    # Check for next step/action patterns
    has_next_step = any(pattern in response_lower for pattern in next_step_patterns)
    
    # Check for WhatsApp links (strongest indicator)
    has_whatsapp_link = any(pattern in response_lower for pattern in whatsapp_patterns)
    
    # Check for specific contact person mentioned
    has_contact_person = any(pattern in response_lower for pattern in contact_patterns)
    
    # Transition should occur if:
    # 1. Has recommendation AND (next step OR whatsapp link OR contact person)
    # 2. OR has whatsapp link (definitive indicator)
    return (has_recommendation and (has_next_step or has_whatsapp_link or has_contact_person)) or has_whatsapp_link

