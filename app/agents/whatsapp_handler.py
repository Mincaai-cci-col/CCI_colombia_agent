"""
Handler WhatsApp pour l'agent CCI
Fonction stateless qui gère la persistance et l'état utilisateur
"""

import json
import asyncio
from typing import Dict, Any, Optional
from app.agents.langchain_agent import CCILangChainAgent

# Stockage temporaire en mémoire (à remplacer par Redis/DB en production)
_user_states: Dict[str, Dict[str, Any]] = {}

async def load_user_state(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Charge l'état d'un utilisateur depuis le stockage
    
    Args:
        user_id: ID utilisateur WhatsApp
        
    Returns:
        dict: État utilisateur ou None si nouveau
    """
    # TODO: Remplacer par Redis/DB
    # Exemple Redis:
    # redis_client = get_redis_client()
    # state_json = await redis_client.get(f"user_state:{user_id}")
    # return json.loads(state_json) if state_json else None
    
    return _user_states.get(user_id)

async def save_user_state(user_id: str, state: Dict[str, Any]) -> None:
    """
    Sauvegarde l'état d'un utilisateur
    
    Args:
        user_id: ID utilisateur WhatsApp
        state: État à sauvegarder
    """
    # TODO: Remplacer par Redis/DB
    # Exemple Redis:
    # redis_client = get_redis_client()
    # await redis_client.set(f"user_state:{user_id}", json.dumps(state), ex=86400)  # 24h TTL
    
    _user_states[user_id] = state

async def whatsapp_chat(user_id: str, user_input: str) -> str:
    """
    Fonction principale pour WhatsApp - STATELESS
    
    Args:
        user_id: ID utilisateur WhatsApp (numéro de téléphone)
        user_input: Message de l'utilisateur
        
    Returns:
        str: Réponse de l'agent CCI
    """
    try:
        # 1. Charger l'état utilisateur
        user_state = await load_user_state(user_id)
        
        # 2. Créer ou reconfigurer l'agent
        if user_state:
            # Utilisateur existant : charger son état
            agent = CCILangChainAgent.from_state(user_state)
        else:
            # Nouvel utilisateur : créer un agent vierge
            agent = CCILangChainAgent()
        
        # 3. Traiter le message
        response = await agent.chat(user_input, user_id)
        
        # 4. Sauvegarder le nouvel état
        new_state = agent.serialize_state()
        await save_user_state(user_id, new_state)
        
        return response
        
    except Exception as e:
        # Log l'erreur (remplacer par un vrai logger en production)
        print(f"❌ Erreur WhatsApp pour user {user_id}: {e}")
        
        # Réponse d'erreur selon la langue probable
        if user_state and user_state.get("detected_language") == "es":
            return "Disculpe, encontré un problema técnico. ¿Puede intentar de nuevo?"
        else:
            return "Désolé, j'ai rencontré un problème technique. Pouvez-vous réessayer ?"

async def reset_user_conversation(user_id: str) -> bool:
    """
    Reset la conversation d'un utilisateur (utile pour les tests ou support)
    
    Args:
        user_id: ID utilisateur WhatsApp
        
    Returns:
        bool: True si succès
    """
    try:
        # Supprimer l'état utilisateur
        if user_id in _user_states:
            del _user_states[user_id]
            
        # TODO: En production avec Redis/DB:
        # redis_client = get_redis_client()
        # await redis_client.delete(f"user_state:{user_id}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur reset user {user_id}: {e}")
        return False

async def get_user_status(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Obtient le statut d'un utilisateur (utile pour le support/debug)
    
    Args:
        user_id: ID utilisateur WhatsApp
        
    Returns:
        dict: Statut utilisateur ou None si pas trouvé
    """
    try:
        user_state = await load_user_state(user_id)
        if not user_state:
            return None
            
        # Créer un agent temporaire pour obtenir le statut complet
        agent = CCILangChainAgent.from_state(user_state)
        return agent.get_status()
        
    except Exception as e:
        print(f"❌ Erreur status user {user_id}: {e}")
        return None

# Fonction utilitaire pour les webhooks WhatsApp
def extract_whatsapp_data(webhook_data: Dict[str, Any]) -> tuple[str, str]:
    """
    Extrait user_id et message depuis les données webhook WhatsApp
    
    Args:
        webhook_data: Données du webhook WhatsApp
        
    Returns:
        tuple: (user_id, user_message)
    """
    # Exemple structure WhatsApp Business API
    # À adapter selon votre provider (Twilio, WhatsApp Cloud API, etc.)
    try:
        # Structure générique
        user_id = webhook_data.get("from", "")
        message = webhook_data.get("text", {}).get("body", "")
        return user_id, message
    except Exception:
        return "", ""

# Exemple d'utilisation
async def main_test():
    """Test de la fonction WhatsApp"""
    user_id = "+33123456789"
    
    # Première interaction
    response1 = await whatsapp_chat(user_id, "je suis prêt")
    print(f"Agent: {response1}")
    
    # Deuxième interaction
    response2 = await whatsapp_chat(user_id, "oui j'ai accédé à l'espace membre")
    print(f"Agent: {response2}")
    
    # Voir le statut
    status = await get_user_status(user_id)
    print(f"Status: {status}")

if __name__ == "__main__":
    asyncio.run(main_test()) 