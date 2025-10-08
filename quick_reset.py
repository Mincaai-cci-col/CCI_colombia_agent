#!/usr/bin/env python3
"""
Script rapide pour reset la mémoire de l'agent
Usage: python quick_reset.py
"""

import asyncio
from app.agents.redis_manager import get_redis_manager

async def quick_reset():
    """Reset rapide de toute la mémoire"""
    manager = get_redis_manager()
    
    print("🔄 Reset de la mémoire de l'agent...")
    
    if manager.redis_client is None:
        print("⚠️ Redis non disponible - nettoyage mémoire locale")
        if hasattr(manager, '_memory_fallback'):
            manager._memory_fallback.clear()
        print("✅ Mémoire locale nettoyée")
        return
    
    # Compter les utilisateurs avant
    pattern = f"{manager.key_prefix}user:*"
    keys = manager.redis_client.keys(pattern)
    
    if not keys:
        print("✅ Aucune mémoire à supprimer")
        return
    
    print(f"📊 Trouvé {len(keys)} utilisateur(s) en mémoire")
    
    # Supprimer toutes les clés
    deleted = manager.redis_client.delete(*keys)
    print(f"✅ {deleted} conversation(s) supprimée(s)")
    
    # Vérifier
    new_keys = manager.redis_client.keys(pattern)
    print(f"📊 Utilisateurs restants: {len(new_keys)}")

if __name__ == "__main__":
    asyncio.run(quick_reset())



