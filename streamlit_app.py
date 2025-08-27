"""
Streamlit interface for testing CCI WhatsApp agent
Simple interface with chat and automatic user_id management
"""

# IMPORTANT: Load .env first
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import asyncio
import uuid
from app.agents.whatsapp_handler import whatsapp_chat, reset_user_conversation, get_user_status
from app.agents.redis_manager import load_user_state

def check_environment():
    """Check if required environment variables are set"""
    import os
    
    required_vars = ["OPENAI_API_KEY", "PINECONE_API_KEY", "PINECONE_INDEX"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        st.error(f"❌ Variables d'environnement manquantes : {', '.join(missing_vars)}")
        st.error("Veuillez vérifier votre fichier .env")
        st.stop()
    
    # Removed the green success message

def reset_conversation():
    """Reset conversation and generate new user ID"""
    # Generate new user ID
    st.session_state.user_id = f"streamlit_user_{uuid.uuid4().hex[:8]}"
    
    # Welcome message to display
    welcome_msg = """👋 Bonjour ! Je suis MarIA, votre **assistant virtuel de la CCI France-Colombie**.

Mon rôle est de mieux comprendre vos besoins en tant qu'adhérent(e) et de vous accompagner si vous avez la moindre question concernant nos offres, services, événements.

📋 Ce petit échange comprend 6 questions simples, et ne vous prendra que quelques minutes.

**Dites-moi quand vous êtes prêt(e), je suis à votre écoute** 😊

---

👋 ¡Hola! Soy MarIA, tu **asistente virtual de la CCI Francia-Colombia**.

Mi objetivo es comprender mejor tus necesidades como miembro y acompañarte si tienes cualquier duda sobre nuestras ofertas, servicios o eventos.

📋 Este breve intercambio contiene 6 preguntas sencillas y solo te tomará unos minutos.

**Dime cuándo estés listo(a), estoy aquí para ayudarte** 😊"""
    
    # Reset conversation state - removed timestamp
    st.session_state.messages = [{
        "role": "assistant",
        "content": welcome_msg
    }]
    
    # Reset user conversation in backend
    asyncio.run(reset_user_conversation(st.session_state.user_id))

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="Test Agent CCI",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Test Agent CCI WhatsApp")
    
    # Check environment variables
    check_environment()
    
    # Initialize session state
    if "user_id" not in st.session_state:
        reset_conversation()
    
    if "messages" not in st.session_state:
        reset_conversation()
    
    # Sidebar with controls
    with st.sidebar:
        st.header("🎛️ Contrôles")
        
        st.markdown(f"**User ID:** `{st.session_state.user_id[:16]}...`")
        
        if st.button("🔄 Nouvelle conversation", type="primary"):
            reset_conversation()
            st.rerun()
        
        # Quick test buttons
        st.markdown("### 🧪 Tests Rapides")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💬 Question Export", help="Teste une question typique"):
                test_message = "Je travaille dans l'export de café vers la France"
                st.session_state.test_message = test_message
        
        with col2:
            if st.button("❓ Question Libre", help="Teste mode assistance"):
                test_message = "Quels sont vos services de formation ?"
                st.session_state.test_message = test_message
        
        # Display user status with agent mode
        try:
            status = asyncio.run(get_user_status(st.session_state.user_id))
            user_state = asyncio.run(load_user_state(st.session_state.user_id))
            
            st.markdown("### 📊 Statut Agent")
            
            if user_state:
                # Display agent mode with colored badge
                agent_mode = user_state.get("agent_mode", "questionnaire")
                questionnaire_completed = user_state.get("questionnaire_completed", False)
                detected_language = user_state.get("detected_language", "fr")
                
                if agent_mode == "questionnaire":
                    st.markdown("🎯 **Mode:** `questionnaire`", help="L'agent pose des questions pour comprendre vos besoins")
                else:
                    st.markdown("🤖 **Mode:** `assistance`", help="L'agent répond à vos questions libres")
                
                st.markdown(f"🌍 **Langue:** `{detected_language.upper()}`")
                
                if questionnaire_completed:
                    st.success("✅ Questionnaire terminé")
                else:
                    st.info("📋 Questionnaire en cours")
                
                # Show memory
                memory_count = len(user_state.get("memory_messages", []))
                st.markdown(f"💭 **Mémoire:** {memory_count} messages")
                
            else:
                st.markdown("🎯 **Mode:** `questionnaire` (défaut)")
                st.info("🆕 Nouvelle conversation")
                
        except Exception as e:
            st.error(f"Erreur statut: {e}")
    
    # Main chat interface
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # Removed timestamp display
    
    # Handle test messages from sidebar
    if "test_message" in st.session_state:
        prompt = st.session_state.test_message
        del st.session_state.test_message
    else:
        prompt = None
    
    # Chat input
    if not prompt:
        prompt = st.chat_input("Tapez votre message...")
    
    if prompt:
        # Add user message to chat - removed timestamp
        st.session_state.messages.append({
            "role": "user", 
            "content": prompt
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
            # Removed timestamp display
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("L'agent réfléchit..."):
                try:
                    response = asyncio.run(whatsapp_chat(st.session_state.user_id, prompt))
                    st.markdown(response)
                    
                    # Check agent mode after response
                    user_state = asyncio.run(load_user_state(st.session_state.user_id))
                    if user_state:
                        agent_mode = user_state.get("agent_mode", "questionnaire")
                        questionnaire_completed = user_state.get("questionnaire_completed", False)
                        
                        # Show mode transition if it happened
                        if questionnaire_completed and agent_mode == "assistance":
                            st.success("🔄 **Transition automatique vers mode assistance!**")
                            st.info("L'agent va maintenant répondre à vos questions libres avec son outil RAG.")
                    
                    # Add to session state - removed timestamp
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })
                    
                    # Force refresh of sidebar to show updated mode
                    st.rerun()
                    
                except Exception as e:
                    error_msg = f"❌ Erreur: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })

if __name__ == "__main__":
    main() 