"""
Test for CCI LangChain Agent with MEMORY and BILINGUAL SUPPORT
Shows how the agent automatically detects language and adapts
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.langchain_agent import CCILangChainAgent
from app.agents.language import detect_language_from_input

def print_divider(title=""):
    """Print a visual divider"""
    print("=" * 70)
    if title:
        print(f" {title} ".center(70, "="))
        print("=" * 70)

async def test_bilingual_agent():
    """Interactive test of the bilingual agent"""
    
    print_divider("🤖 CCI LANGCHAIN AGENT TEST")
    print("💡 This agent has MEMORY and supports French/Spanish")
    print("🔍 Language detection: Automatic on first message")
    print("🎯 Main mission: Complete diagnostic questionnaire")
    print("🛠️  Available tools: RAG search, diagnostic collection")
    print("\nCommands:")
    print("- 'status' : View agent status")
    print("- 'memory' : View conversation memory") 
    print("- 'reset'  : Reset conversation")
    print("- 'quit'   : Exit")
    print_divider()
    
    # Create agent
    agent = CCILangChainAgent()
    
    print("🤖 Agent: Bonjour ! Je suis YY, votre assistant virtuel de la CCI France-Colombie.")
    print("Mon rôle est de mieux comprendre vos besoins en tant qu'adhérent(e).")
    print("📋 Ce petit échange comprend 8 questions simples, et ne vous prendra que quelques minutes.")
    print("Dites-moi quand vous êtes prêt(e), je suis à votre écoute ! 😊")
    
    conversation_count = 0
    
    while True:
        try:
            print(f"\n💬 Vous : ", end="")
            user_input = input().strip()
            
            if user_input.lower() == 'quit':
                print("👋 Au revoir !")
                break
            
            elif user_input.lower() == 'status':
                status = agent.get_status()
                print("\n📊 AGENT STATUS:")
                print(f"- Current question: {status['current_question']}/8")
                print(f"- Answers collected: {status['answers_collected']}")
                print(f"- Detected language: {status['detected_language']}")
                print(f"- Language detected: {status['language_detected']}")
                print(f"- Memory messages: {status['memory_messages']}")
                print(f"- Diagnostic complete: {status['is_diagnostic_complete']}")
                continue
            
            elif user_input.lower() == 'memory':
                memory_content = agent.get_memory_content()
                print(f"\n🧠 MEMORY CONTENT:\n{memory_content}")
                continue
            
            elif user_input.lower() == 'reset':
                agent.reset()
                print("🔄 Agent reset! New conversation started.")
                conversation_count = 0
                continue
            
            if not user_input:
                print("⚠️ Please enter a message!")
                continue
            
            # Process message with agent
            print("🤔 Processing...")
            response = await agent.chat(user_input, user_id="test_user")
            
            conversation_count += 1
            print(f"\n🤖 Agent: {response}")
            
            # Show basic progress
            status = agent.get_status()
            if status['answers_collected'] > 0:
                print(f"\n📈 Progress: {status['answers_collected']}/8 answers collected")
            
        except KeyboardInterrupt:
            print("\n\n👋 Session interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("🔄 You can continue the conversation or type 'quit' to exit.")

async def test_language_detection():
    """Test language detection separately"""
    print_divider("🌍 LANGUAGE DETECTION TEST")
    
    test_phrases = [
        "Bonjour, je suis prêt pour commencer",
        "Hola, estoy listo para empezar", 
        "Je voudrais des informations sur la CCI",
        "Quiero información sobre la CCI",
        "Comment ça marche ?",
        "¿Cómo funciona?"
    ]
    
    for phrase in test_phrases:
        try:
            detected = await detect_language_from_input(phrase)
            print(f"'{phrase}' → {detected}")
        except Exception as e:
            print(f"Error detecting language for '{phrase}': {e}")

async def test_agent_memory():
    """Test agent memory persistence"""
    print_divider("🧠 MEMORY PERSISTENCE TEST")
    
    agent = CCILangChainAgent()
    
    # Simulate conversation sequence
    messages = [
        "je suis prêt",
        "oui j'ai accédé à l'espace membre", 
        "j'ai participé à un événement networking",
        "status"  # Special command
    ]
    
    for i, msg in enumerate(messages):
        if msg == "status":
            status = agent.get_status()
            print(f"\n📊 After {i} messages:")
            print(f"- Answers collected: {status['answers_collected']}")
            print(f"- Current question: {status['current_question']}")
        else:
            print(f"\n👤 User: {msg}")
            response = await agent.chat(msg, f"test_user_{i}")
            print(f"🤖 Agent: {response[:100]}...")

def main():
    """Main test function"""
    print("🚀 Starting CCI LangChain Agent Tests")
    
    # Check environment variables
    required_vars = ["OPENAI_API_KEY", "PINECONE_API_KEY", "PINECONE_INDEX"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file")
        return
    
    print("✅ Environment variables loaded")
    
    # Menu
    while True:
        print("\n" + "="*50)
        print("Choose a test:")
        print("1. Interactive Agent Test")
        print("2. Language Detection Test") 
        print("3. Memory Persistence Test")
        print("4. Exit")
        print("="*50)
        
        choice = input("Your choice (1-4): ").strip()
        
        if choice == "1":
            asyncio.run(test_bilingual_agent())
        elif choice == "2":
            asyncio.run(test_language_detection())
        elif choice == "3":
            asyncio.run(test_agent_memory())
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main() 