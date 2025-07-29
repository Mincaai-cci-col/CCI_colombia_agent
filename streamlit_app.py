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
from datetime import datetime
from app.agents.whatsapp_handler import whatsapp_chat, reset_user_conversation, get_user_status

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
    
    st.success("✅ Variables d'environnement chargées")

def reset_conversation():
    """Reset conversation and generate new user ID"""
    # Generate new user ID
    st.session_state.user_id = f"streamlit_user_{uuid.uuid4().hex[:8]}"
    
    # Welcome message to display
    welcome_msg = """👋 Bonjour ! Je suis YY, votre **assistant virtuel de la CCI France-Colombie**.

Mon rôle est de mieux comprendre vos besoins en tant qu'adhérent(e) et de vous accompagner si vous avez la moindre question concernant nos offres, services, événements.

📋 Ce petit échange comprend 8 questions simples, et ne vous prendra que quelques minutes.

**Dites-moi quand vous êtes prêt(e), je suis à votre écoute** 😊

---

👋 ¡Hola! Soy YY, tu **asistente virtual de la CCI Francia-Colombia**.

Mi objetivo es comprender mejor tus necesidades como miembro y acompañarte si tienes cualquier duda sobre nuestras ofertas, servicios o eventos.

📋 Este breve intercambio contiene 8 preguntas sencillas y solo te tomará unos minutos.

**Dime cuándo estés listo(a), estoy aquí para ayudarte** 😊"""
    
    # Reset conversation state
    st.session_state.messages = [{
        "role": "assistant",
        "content": welcome_msg,
        "timestamp": datetime.now().strftime("%H:%M:%S")
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
    st.markdown("*Interface de test pour l'agent conversationnel CCI*")
    
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
        
        # Display user status
        try:
            status = asyncio.run(get_user_status(st.session_state.user_id))
            st.markdown("### 📊 Statut")
            if status["exists"]:
                st.markdown(f"- **Question:** {status['current_question']}/8")
                st.markdown(f"- **Réponses:** {status['answers_collected']}")
                st.markdown(f"- **Langue:** {status['language']}")
                if status["diagnostic_complete"]:
                    st.success("✅ Diagnostic terminé")
            else:
                st.info("Nouvelle conversation")
        except Exception as e:
            st.error(f"Erreur statut: {e}")
    
    # Main chat interface
    st.markdown("### 💬 Conversation")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "timestamp" in message:
                st.caption(f"⏰ {message['timestamp']}")
    
    # Chat input
    if prompt := st.chat_input("Tapez votre message..."):
        # Add user message to chat
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.messages.append({
            "role": "user", 
            "content": prompt,
            "timestamp": timestamp
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
            st.caption(f"⏰ {timestamp}")
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("L'agent réfléchit..."):
                try:
                    response = asyncio.run(whatsapp_chat(st.session_state.user_id, prompt))
                    st.markdown(response)
                    
                    # Add to session state
                    response_timestamp = datetime.now().strftime("%H:%M:%S")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "timestamp": response_timestamp
                    })
                    st.caption(f"⏰ {response_timestamp}")
                    
                except Exception as e:
                    error_msg = f"❌ Erreur: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })

if __name__ == "__main__":
    main() 