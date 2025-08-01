#!/usr/bin/env python3
"""
Test script pour vérifier l'intégration Redis
"""

import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire du projet au path
sys.path.append(str(Path(__file__).parent.parent))

from app.agents.redis_manager import get_redis_manager
from app.agents.whatsapp_handler import whatsapp_chat, get_user_status, get_redis_stats

async def test_redis_integration():
    """Test complet de l'intégration Redis"""
    print("🧪 TEST INTÉGRATION REDIS")
    print("=" * 50)
    
    # Test 1: Vérifier la connexion Redis
    print("\n1️⃣ Test connexion Redis...")
    manager = get_redis_manager()
    stats = manager.get_stats()
    
    print(f"   Status: {stats['status']}")
    print(f"   Redis disponible: {stats['redis_available']}")
    
    if stats['redis_available']:
        print(f"   Connexion: {stats.get('connection_info', 'N/A')}")
        print(f"   Version: {stats.get('redis_version', 'N/A')}")
        print("   ✅ Redis connecté")
    else:
        print("   ⚠️ Redis indisponible - mode fallback")
    
    # Test 2: Test de stockage/récupération d'état
    print("\n2️⃣ Test stockage d'état...")
    test_user_id = "test_user_redis_123"
    
    # État de test
    test_state = {
        "current_question": 3,
        "detected_language": "fr",
        "language_detected": True,
        "first_interaction": False,
        "test_data": "redis_integration_test"
    }
    
    # Sauvegarder
    save_success = await manager.save_user_state(test_user_id, test_state)
    print(f"   Sauvegarde: {'✅ Succès' if save_success else '❌ Échec'}")
    
    # Récupérer
    loaded_state = await manager.load_user_state(test_user_id)
    
    if loaded_state:
        print("   ✅ État récupéré")
        print(f"   Question actuelle: {loaded_state.get('current_question')}")
        print(f"   Langue: {loaded_state.get('detected_language')}")
        
        # Vérifier que les données correspondent
        if loaded_state.get('test_data') == test_state['test_data']:
            print("   ✅ Données cohérentes")
        else:
            print("   ❌ Données incohérentes")
    else:
        print("   ❌ Impossible de récupérer l'état")
    
    # Test 3: Test conversation complète
    print("\n3️⃣ Test conversation avec persistance...")
    
    # Premier message
    response1 = await whatsapp_chat(test_user_id, "Bonjour, je suis une nouvelle entreprise")
    print(f"   Premier message: {'✅' if response1 else '❌'}")
    
    # Statut après premier message
    status = await get_user_status(test_user_id)
    print(f"   Utilisateur existe: {status['exists']}")
    print(f"   Langue détectée: {status['language']}")
    
    # Deuxième message (doit récupérer l'état)
    response2 = await whatsapp_chat(test_user_id, "Nous sommes dans le secteur technologique")
    print(f"   Deuxième message: {'✅' if response2 else '❌'}")
    
    # Test 4: Nettoyage
    print("\n4️⃣ Nettoyage...")
    delete_success = await manager.delete_user_state(test_user_id)
    print(f"   Suppression: {'✅ Succès' if delete_success else '❌ Échec'}")
    
    # Test 5: Statistiques finales
    print("\n5️⃣ Statistiques finales...")
    final_stats = await get_redis_stats()
    print(f"   Utilisateurs actifs: {final_stats.get('active_users', 0)}")
    print(f"   Mémoire utilisée: {final_stats.get('used_memory_human', 'N/A')}")
    
    print("\n" + "=" * 50)
    print("🎉 Test terminé!")
    
    if stats['redis_available']:
        print("✅ Votre configuration Redis est opérationnelle")
    else:
        print("⚠️ Redis non disponible - l'application fonctionne en mode fallback")
        print("   Consultez redis_config.md pour installer Redis")

if __name__ == "__main__":
    asyncio.run(test_redis_integration()) 