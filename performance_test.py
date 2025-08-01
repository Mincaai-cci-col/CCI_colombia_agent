import time
import json
from app.agents.whatsapp_handler import whatsapp_chat
from whatsapp_contact.contacts_manager import get_contacts_manager

def measure_performance():
    """Mesure les temps de réponse de l'agent"""
    
    print("🔍 Test de performance de l'agent...")
    
    # Test cases
    test_cases = [
        {"message": "Bonjour", "user_id": "+573001234567"},
        {"message": "J'ai un problème avec mon ordinateur", "user_id": "+573001234567"},
        {"message": "Merci pour votre aide", "user_id": "+573001234567"}
    ]
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📊 Test {i}/3: '{test['message'][:30]}...'")
        
        start_time = time.time()
        
        # Mesurer le temps de contact lookup
        contact_start = time.time()
        contacts_manager = get_contacts_manager()
        contact = contacts_manager.find_contact_by_phone(test['user_id'])
        contact_time = time.time() - contact_start
        
        # Mesurer le temps total
        try:
            response = whatsapp_chat(test['message'], test['user_id'])
            total_time = time.time() - start_time
            
            result = {
                'test_num': i,
                'message': test['message'],
                'contact_lookup_time': round(contact_time * 1000, 2),  # ms
                'total_time': round(total_time, 2),  # seconds
                'llm_time': round(total_time - contact_time, 2),  # seconds
                'response_length': len(response),
                'success': True
            }
            
            print(f"  ⏱️  Contact lookup: {result['contact_lookup_time']}ms")
            print(f"  ⏱️  LLM + Agent: {result['llm_time']}s")
            print(f"  ⏱️  Total: {result['total_time']}s")
            print(f"  📝 Réponse: {len(response)} caractères")
            
            if total_time > 8:
                print(f"  ⚠️  TROP LENT pour Manychat! ({total_time}s > 8s)")
            else:
                print(f"  ✅ OK pour Manychat ({total_time}s < 8s)")
                
        except Exception as e:
            result = {
                'test_num': i,
                'message': test['message'],
                'error': str(e),
                'success': False
            }
            print(f"  ❌ Erreur: {e}")
        
        results.append(result)
        
        # Pause entre les tests
        if i < len(test_cases):
            time.sleep(1)
    
    # Résumé
    print("\n" + "="*50)
    print("📈 RÉSUMÉ PERFORMANCE")
    print("="*50)
    
    successful_tests = [r for r in results if r.get('success')]
    if successful_tests:
        avg_total = sum(r['total_time'] for r in successful_tests) / len(successful_tests)
        avg_contact = sum(r['contact_lookup_time'] for r in successful_tests) / len(successful_tests)
        avg_llm = sum(r['llm_time'] for r in successful_tests) / len(successful_tests)
        
        print(f"⏱️  Temps moyen total: {avg_total:.2f}s")
        print(f"⏱️  Temps moyen contact: {avg_contact:.2f}ms")
        print(f"⏱️  Temps moyen LLM: {avg_llm:.2f}s")
        
        if avg_total < 6:
            print("✅ Performance EXCELLENTE!")
        elif avg_total < 8:
            print("🟡 Performance OK pour Manychat")
        else:
            print("🔴 Performance TROP LENTE - Optimisations nécessaires!")
    
    # Sauvegarder les résultats
    with open('performance_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Résultats sauvés dans 'performance_results.json'")
    
    return results

if __name__ == "__main__":
    try:
        # Précharger les contacts
        print("🔄 Préchargement des contacts...")
        contacts_manager = get_contacts_manager('whatsapp_contact/Base de datos proyecto IA (1).xlsx')
        print(f"✅ {contacts_manager.get_stats()['total_contacts']} contacts chargés")
        
        # Lancer les tests
        results = measure_performance()
        
    except Exception as e:
        print(f"❌ Erreur during test: {e}") 