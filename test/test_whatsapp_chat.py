"""
Test simple avec la fonction whatsapp_chat()
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.whatsapp_handler import whatsapp_chat

async def main():
    print("💬 TEST WHATSAPP CHAT")
    print("=" * 40)
    
    # Demander le user ID
    user_id = input("📞 User ID (numéro WhatsApp): ").strip()
    if not user_id:
        print("❌ User ID requis")
        return
    
    print(f"\n💬 Conversation WhatsApp avec {user_id}")
    print("Tapez 'quit' pour terminer")
    print("-" * 40)
    
    while True:
        user_message = input(f"\n👤 Vous: ").strip()
        
        if user_message.lower() == 'quit':
            break
        elif not user_message:
            continue
        
        try:
            # Utiliser directement whatsapp_chat
            response = await whatsapp_chat(user_id, user_message)
            print(f"🤖 Agent: {response}")
        except Exception as e:
            print(f"❌ Erreur: {e}")
            break

if __name__ == "__main__":
    asyncio.run(main()) 