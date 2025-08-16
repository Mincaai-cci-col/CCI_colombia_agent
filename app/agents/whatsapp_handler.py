"""
WhatsApp Handler for CCI Agent
Stateless wrapper for agent state management and WhatsApp deployment
Manages user state persistence for multi-turn conversations
"""

import asyncio
from typing import Dict, Any, Optional
from app.agents.langchain_agent import CCILangChainAgent
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
    Main function for WhatsApp conversations.
    Stateless: loads state, processes message, saves state.
    Automatically enriches agent's system prompt with contact information if available.
    
    Args:
        user_id: Unique user identifier (WhatsApp phone number)
        user_input: User's message
        
    Returns:
        Agent's response
    """
    try:
        # Load existing user state
        user_state = await load_user_state(user_id)
        print(f"🔍 Chargement de l'état utilisateur pour {user_id}: {user_state}")
        
        if user_state:
            # Restore agent from saved state
            agent = CCILangChainAgent.from_state(user_state)
        else:
            # Create new agent for new user
            agent = CCILangChainAgent()
            
            # For new users, try to set client context from contact database
            contact_info = await get_contact_info(user_id)
            if contact_info:
                agent.set_client_context(contact_info)
        
        # Process user message (agent has enriched prompt if contact found)
        response = await agent.chat(user_input, user_id)
        
        # Save updated state
        new_state = agent.serialize_state()
        await save_user_state(user_id, new_state)
        
        return response
        
    except Exception as e:
        error_msg = f"Désolé, j'ai rencontré un problème technique. Pouvez-vous réessayer ? (Erreur: {str(e)})"
        return error_msg

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
    
    response = requests.get(f"{os.getenv('BACKEND_URL')}/api/v1/whatsapp/info/{user_id}")
    if response.status_code == 200:
        contact_info = response.json()
        if contact_info:
            return contact_info if contact_info else None
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

