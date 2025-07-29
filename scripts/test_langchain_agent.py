"""
Test de l'agent LangChain CCI avec MÉMOIRE et SUPPORT BILINGUE
Montre comment l'agent détecte automatiquement la langue et s'adapte
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.langchain_agent import create_cci_agent
from app.agents.language import get_welcome_message_static

async def test_langchain_agent():
    """Test interactif de l'agent LangChain CCI avec mémoire et support bilingue"""
    
    print("🧠🌍 Test de l'Agent LangChain CCI avec MÉMOIRE et SUPPORT BILINGUE")
    print("💡 L'agent détecte automatiquement la langue et s'adapte !")
    print("Tapez 'quit' pour sortir, 'memory' pour voir la mémoire, 'status' pour l'état")
    print("🇫🇷 Essayez en français : 'je suis prêt', 'oui', 'd'accord'")
    print("🇪🇸 Essayez en espagnol : 'estoy listo', 'sí', 'perfecto'")
    print("=" * 80)
    
    # Créer l'agent avec mémoire et support bilingue
    agent = create_cci_agent()
    
    # Message de bienvenue bilingue
    welcome_message = get_welcome_message_static()
    print(f"\nAgent : {welcome_message}")
    
    conversation_count = 0
    
    # Boucle de conversation
    while True:
        try:
            # Input utilisateur
            print(f"\nVous : ", end="")
            user_input = input().strip()
            
            if user_input.lower() == 'quit':
                print("👋 À bientôt ! / ¡Hasta luego!")
                break
            
            # Commandes spéciales
            if user_input.lower() == 'memory':
                print("\n🧠 === CONTENU DE LA MÉMOIRE ===")
                memory_content = agent.get_memory_content()
                status = agent.get_status()
                
                print(f"📊 Messages en mémoire : {status['memory_messages']}")
                print(f"🌍 Langue détectée : {status['detected_language']} ({'Français' if status['detected_language'] == 'fr' else 'Español'})")
                print(f"📝 Réponses collectées : {status['answers_collected']}")
                print(f"❓ Question actuelle : {status['current_question']}/8")
                
                if status['diagnostic_answers']:
                    print(f"\n📋 Réponses du diagnostic :")
                    for i, answer in enumerate(status['diagnostic_answers'], 1):
                        lang_flag = "🇫🇷" if answer.get('language') == 'fr' else "🇪🇸"
                        print(f"  {i}. {lang_flag} {answer['answer']}")
                
                print(f"\n💭 Résumé de la mémoire : {status['memory_summary']}")
                print("\n" + "="*60)
                continue
            
            if user_input.lower() == 'status':
                status = agent.get_status()
                print(f"\n📊 === STATUT DE L'AGENT ===")
                print(f"🌍 Langue détectée : {status['detected_language']} ({'✅ Détectée' if status['language_detected'] else '❌ Non détectée'})")
                print(f"❓ Question : {status['current_question']}/8")
                print(f"📝 Réponses : {status['answers_collected']}")
                print(f"🎯 Diagnostic complet : {'✅ Oui' if status['is_diagnostic_complete'] else '❌ Non'}")
                print("="*40)
                continue
            
            if not user_input:
                continue
            
            conversation_count += 1
            
            # Appel à l'agent LangChain avec détection automatique de langue
            if conversation_count == 1:
                print(f"\n🔍 Première interaction : détection de langue automatique...")
            else:
                print(f"\n🤖 Agent en cours de réflexion (mémoire + langue)...")
            
            response = await agent.chat(user_input)
            
            # Afficher la réponse
            print(f"\nAgent : {response}")
            
            # Debug status compact avec langue
            status = agent.get_status()
            lang_emoji = "🇫🇷" if status['detected_language'] == 'fr' else "🇪🇸"
            print(f"[Debug] {lang_emoji} Langue: {status['detected_language']} | 🧠 Mémoire: {status['memory_messages']} msg | 📝 Réponses: {status['answers_collected']}/8 | ❓ Question: {status['current_question']}/8")
            
            # Vérifier si diagnostic terminé
            if status['current_question'] > 8 or "diagnostic" in response.lower() and ("terminé" in response.lower() or "terminado" in response.lower()):
                print(f"\n🎉 Diagnostic terminé avec succès !")
                print(f"📝 Toutes les réponses collectées : {len(status['diagnostic_answers'])}")
                
                # Afficher toutes les réponses avec langue
                if status['diagnostic_answers']:
                    print(f"\n📋 === RÉSUMÉ DU DIAGNOSTIC BILINGUE ===")
                    for i, answer in enumerate(status['diagnostic_answers'], 1):
                        lang_flag = "🇫🇷" if answer.get('language') == 'fr' else "🇪🇸"
                        print(f"Question {i}: {lang_flag} {answer['answer']}")
                    print("="*50)
                
                # Proposer de continuer
                lang = status['detected_language']
                if lang == "es":
                    print(f"\n¿Quiere hacer más preguntas? (escriba 'memory' para ver la memoria)")
                else:
                    print(f"\nVoulez-vous poser d'autres questions ? (tapez 'memory' pour voir la mémoire)")
                
        except KeyboardInterrupt:
            print("\n👋 À bientôt ! / ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Erreur : {e}")
            print("Essayons de continuer...")

if __name__ == "__main__":
    print("🔧 Initialisation de l'agent bilingue avec mémoire LangChain...")
    asyncio.run(test_langchain_agent()) 