"""
Redis Manager for CCI Agent State Persistence
Replaces in-memory storage with Redis for production scalability
"""

import redis
import json
import os
import time
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class RedisStateManager:
    """
    Gestionnaire Redis pour la persistance de l'état des conversations
    """
    
    def __init__(self):
        """Initialize Redis connection"""
        # TTL pour les sessions (en secondes) - 3 semaines par défaut (21 jours)
        self.session_ttl = int(os.getenv("REDIS_SESSION_TTL", "1814400"))
        
        # Prefix pour les clés Redis
        self.key_prefix = os.getenv("REDIS_KEY_PREFIX", "cci_agent:")
        
        try:
            # Priorité à REDIS_URL si définie, sinon utilise l'URL par défaut de production
            redis_url = os.getenv("REDIS_URL", "redis://default:EwZ9BeDcqEW9jBhlMHnAc9SOmGP8fhDW@redis-14454.fcrce190.us-east-1-1.ec2.redns.redis-cloud.com:14454/0")
            
            if redis_url:
                # Connexion via URL (Redis Cloud, Heroku, etc.)
                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True
                )
                self.connection_info = f"URL: {redis_url.split('@')[-1] if '@' in redis_url else redis_url}"
                print(f"🔗 Connexion Redis via URL: {self.connection_info}")
            else:
                # Connexion via paramètres individuels (fallback)
                self.redis_host = os.getenv("REDIS_HOST", "localhost")
                self.redis_port = int(os.getenv("REDIS_PORT", "6379"))
                self.redis_password = os.getenv("REDIS_PASSWORD", None)
                self.redis_db = int(os.getenv("REDIS_DB", "0"))
                
                self.redis_client = redis.Redis(
                    host=self.redis_host,
                    port=self.redis_port,
                    password=self.redis_password,
                    db=self.redis_db,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True
                )
                self.connection_info = f"{self.redis_host}:{self.redis_port}"
                print(f"🔗 Connexion Redis via paramètres: {self.connection_info}")
            
            # Test de connexion
            self.redis_client.ping()
            print(f"✅ Redis connecté: {self.connection_info}")
            
        except Exception as e:
            print(f"❌ Erreur connexion Redis: {e}")
            print("🔄 Fallback vers stockage en mémoire")
            self.redis_client = None
            self.connection_info = "fallback_memory"
            self._memory_fallback = {}
    
    def _get_key(self, user_id: str) -> str:
        """Generate Redis key for user"""
        return f"{self.key_prefix}user:{user_id}"
    
    async def load_user_state(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Load user's conversation state from Redis
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Dict containing user's agent state or None if not found
        """
        try:
            if self.redis_client is None:
                # Fallback en mémoire si Redis indisponible
                return self._memory_fallback.get(user_id)
            
            key = self._get_key(user_id)
            data = self.redis_client.get(key)
            
            if data:
                state = json.loads(data)
                print(f"🔄 État chargé depuis Redis pour {user_id}")
                return state
            
            return None
            
        except Exception as e:
            print(f"⚠️ Erreur lecture Redis pour {user_id}: {e}")
            # Fallback en mémoire en cas d'erreur
            return self._memory_fallback.get(user_id)
    
    async def save_user_state(self, user_id: str, state: Dict[str, Any]) -> bool:
        """
        Save user's conversation state to Redis
        
        Args:
            user_id: Unique user identifier
            state: Agent state to save
            
        Returns:
            bool: True if saved successfully
        """
        try:
            if self.redis_client is None:
                # Fallback en mémoire si Redis indisponible
                self._memory_fallback[user_id] = state
                return True
            
            key = self._get_key(user_id)
            
            # Ajouter timestamp pour suivi
            state_with_meta = state.copy()
            state_with_meta["_last_updated"] = int(time.time())
            
            # Sauvegarder avec TTL
            success = self.redis_client.setex(
                key, 
                self.session_ttl, 
                json.dumps(state_with_meta)
            )
            
            if success:
                print(f"💾 État sauvegardé en Redis pour {user_id}")
                return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde Redis pour {user_id}: {e}")
            # Fallback en mémoire en cas d'erreur
            self._memory_fallback[user_id] = state
            return False
    
    async def delete_user_state(self, user_id: str) -> bool:
        """
        Delete user's conversation state
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            if self.redis_client is None:
                # Fallback en mémoire
                self._memory_fallback.pop(user_id, None)
                return True
            
            key = self._get_key(user_id)
            deleted = self.redis_client.delete(key)
            
            if deleted:
                print(f"🗑️ État supprimé de Redis pour {user_id}")
                return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ Erreur suppression Redis pour {user_id}: {e}")
            self._memory_fallback.pop(user_id, None)
            return False
    
    async def get_user_last_activity(self, user_id: str) -> Optional[int]:
        """
        Get user's last activity timestamp
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            int: Timestamp or None if not found
        """
        try:
            state = await self.load_user_state(user_id)
            if state:
                return state.get("_last_updated")
            return None
            
        except Exception as e:
            print(f"⚠️ Erreur lecture timestamp pour {user_id}: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get Redis connection stats
        
        Returns:
            dict: Connection and usage statistics
        """
        try:
            if self.redis_client is None:
                return {
                    "status": "fallback_memory",
                    "active_users": len(self._memory_fallback),
                    "redis_available": False
                }
            
            info = self.redis_client.info()
            pattern = f"{self.key_prefix}user:*"
            active_keys = len(self.redis_client.keys(pattern))
            
            return {
                "status": "connected",
                "redis_version": info.get("redis_version", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "unknown"),
                "active_users": active_keys,
                "redis_available": True,
                "connection_info": self.connection_info,
                "connection_type": "URL" if os.getenv("REDIS_URL") else "params"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "redis_available": False,
                "active_users": len(self._memory_fallback) if hasattr(self, '_memory_fallback') else 0
            }

# Instance globale singleton
_redis_manager = None

def get_redis_manager() -> RedisStateManager:
    """
    Get global Redis manager instance (singleton)
    
    Returns:
        RedisStateManager: Global Redis manager
    """
    global _redis_manager
    if _redis_manager is None:
        _redis_manager = RedisStateManager()
    return _redis_manager

# Fonctions de compatibilité pour l'API existante
async def load_user_state(user_id: str) -> Optional[Dict[str, Any]]:
    """Wrapper pour compatibilité avec l'API existante"""
    manager = get_redis_manager()
    return await manager.load_user_state(user_id)

async def save_user_state(user_id: str, state: Dict[str, Any]) -> None:
    """Wrapper pour compatibilité avec l'API existante"""
    manager = get_redis_manager()
    await manager.save_user_state(user_id, state)

async def reset_user_conversation(user_id: str) -> None:
    """Wrapper pour compatibilité avec l'API existante"""
    manager = get_redis_manager()
    await manager.delete_user_state(user_id) 