"""
WhatsApp Handler for CCI Agent
Stateless wrapper for agent state management and WhatsApp deployment
Manages user state persistence for multi-turn conversations
"""

import asyncio
from typing import Dict, Any, Optional
from app.agents.langchain_agent import CCILangChainAgent

# In-memory storage for user states (replace with Redis/DB in production)
# TODO: Replace with Redis or database for production deployment
_user_states: Dict[str, Dict[str, Any]] = {}

async def load_user_state(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Load user's conversation state.
    
    Args:
        user_id: Unique user identifier
        
    Returns:
        Dict containing user's agent state or None if not found
    """
    return _user_states.get(user_id)

async def save_user_state(user_id: str, state: Dict[str, Any]) -> None:
    """
    Save user's conversation state.
    
    Args:
        user_id: Unique user identifier
        state: Agent state to save
    """
    _user_states[user_id] = state

async def reset_user_conversation(user_id: str) -> None:
    """
    Reset user's conversation (new conversation).
    
    Args:
        user_id: Unique user identifier
    """
    if user_id in _user_states:
        del _user_states[user_id]

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
        "answers_collected": len(state.get("diagnostic_answers", [])),
        "language": state.get("detected_language", "fr"),
        "diagnostic_complete": state.get("current_question", 1) > 8
    }

async def whatsapp_chat(user_id: str, user_input: str) -> str:
    """
    Main function for WhatsApp conversations.
    Stateless: loads state, processes message, saves state.
    
    Args:
        user_id: Unique user identifier  
        user_input: User's message
        
    Returns:
        Agent's response
    """
    try:
        # Load existing user state
        user_state = await load_user_state(user_id)
        
        if user_state:
            # Restore agent from saved state
            agent = CCILangChainAgent.from_state(user_state)
        else:
            # Create new agent for new user
            agent = CCILangChainAgent()
        
        # Process user message
        response = await agent.chat(user_input, user_id)
        
        # Save updated state
        new_state = agent.serialize_state()
        await save_user_state(user_id, new_state)
        
        return response
        
    except Exception as e:
        error_msg = f"Désolé, j'ai rencontré un problème technique. Pouvez-vous réessayer ? (Erreur: {str(e)})"
        return error_msg

