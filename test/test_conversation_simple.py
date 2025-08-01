"""
Test simple : User ID → Prompt enrichi → Conversation
"""

import asyncio
from app.agents.whatsapp_handler import whatsapp_chat, get_contact_info
from app.agents.langchain_agent import CCILangChainAgent

async def main():
    print("🧪 TEST SIMPLE DE CONVERSATION ENRICHIE")
    print("=" * 50)
    
    # 1. Demander le user ID
    user_id = input("📞 User ID (numéro WhatsApp): ").strip()
    if not user_id:
        print("❌ User ID requis")
        return
    
    # 2. Créer agent avec contexte
    print(f"\n🔍 Recherche du contact pour {user_id}...")
    contact_info = await get_contact_info(user_id)
    
    agent = CCILangChainAgent()
    if contact_info:
        agent.set_client_context(contact_info)
        print(f"✅ Contact trouvé: {contact_info['empresa']}")
    else:
        print("❌ Contact non trouvé - agent sans contexte client")
    
    # 3. Montrer le prompt
    print(f"\n📄 PROMPT DE L'AGENT:")
    print("=" * 60)
    # Accéder correctement au contenu du prompt système
    system_message = agent.prompt.messages[0]
    if hasattr(system_message, 'prompt') and hasattr(system_message.prompt, 'template'):
        print(system_message.prompt.template)
    else:
        print("Le prompt est généré dynamiquement")
    print("=" * 60)
    
    # 4. Conversation
    print(f"\n💬 CONVERSATION AVEC L'AGENT")
    print("Tapez 'quit' pour terminer, 'prompt' pour revoir le prompt")
    print("-" * 50)
    
    while True:
        user_message = input(f"\n👤 Vous: ").strip()
        
        if user_message.lower() == 'quit':
            break
        elif user_message.lower() == 'prompt':
            print("\n📄 PROMPT ACTUEL:")
            print("=" * 60)
            system_message = agent.prompt.messages[0]
            if hasattr(system_message, 'prompt') and hasattr(system_message.prompt, 'template'):
                print(system_message.prompt.template)
            else:
                print("Le prompt est généré dynamiquement")
            print("=" * 60)
            continue
        elif not user_message:
            continue
        
        try:
            response = await agent.chat(user_message, user_id)
            print(f"🤖 Agent: {response}")
        except Exception as e:
            print(f"❌ Erreur: {e}")
            break

if __name__ == "__main__":
    asyncio.run(main()) 