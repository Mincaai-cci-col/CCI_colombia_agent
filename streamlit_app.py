"""
Interface Streamlit pour tester l'agent CCI WhatsApp
Interface simple avec chat et gestion automatique des user_id
"""

# IMPORTANT: Charger le .env en premier
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import asyncio
import uuid
from datetime import datetime
from app.agents.whatsapp_handler import whatsapp_chat, reset_user_conversation, get_user_status

# Configuration de la page
st.set_page_config(
    page_title="Test Agent CCI",
    page_icon="🤖",
    layout="centered"
)

# Initialisation de la session
if "user_id" not in st.session_state:
    st.session_state.user_id = f"test_{uuid.uuid4().hex[:8]}"
    st.session_state.conversation_started = False
    
    # Message de bienvenue bilingue à ajouter à l'historique
    welcome_msg = """👋 Bonjour ! Je suis YY, votre **assistant virtuel de la CCI France-Colombie**.

Mon rôle est de **mieux comprendre vos besoins** en tant qu'adhérent(e) et de vous **accompagner si vous avez la moindre question concernant nos offres, services, événements.**

📝 Ce petit échange comprend 7 **questions simples**, et ne vous prendra que **quelques minutes**.

**Dites-moi quand vous êtes prêt(e), je suis à votre écoute**

---

👋 ¡Hola! Soy YY, tu **asistente virtual de la CCI Francia-Colombia**.

Mi objetivo es **comprender mejor tus necesidades** como miembro y **acompañarte si tienes cualquier duda sobre nuestras ofertas, servicios o eventos**.

📝 Este breve intercambio contiene **7 preguntas sencillas** y solo te tomará **unos minutos**.

**Dime cuándo estés listo(a), estoy aquí para ayudarte** 😊"""
    
    st.session_state.messages = [{
        "role": "assistant", 
        "content": welcome_msg,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }]

def reset_conversation():
    """Reset la conversation (nouveau user_id)"""
    # Générer un nouveau user_id
    old_user_id = st.session_state.user_id
    st.session_state.user_id = f"test_{uuid.uuid4().hex[:8]}"
    
    # Reset l'état de l'agent pour l'ancien user
    asyncio.run(reset_user_conversation(old_user_id))
    
    # Message de bienvenue bilingue
    welcome_msg = """👋 Bonjour ! Je suis YY, votre **assistant virtuel de la CCI France-Colombie**.

Mon rôle est de **mieux comprendre vos besoins** en tant qu'adhérent(e) et de vous **accompagner si vous avez la moindre question concernant nos offres, services, événements.**

📝 Ce petit échange comprend 7 **questions simples**, et ne vous prendra que **quelques minutes**.

**Dites-moi quand vous êtes prêt(e), je suis à votre écoute**

---

👋 ¡Hola! Soy YY, tu **asistente virtual de la CCI Francia-Colombia**.

Mi objetivo es **comprender mejor tus necesidades** como miembro y **acompañarte si tienes cualquier duda sobre nuestras ofertas, servicios o eventos**.

📝 Este breve intercambio contiene **7 preguntas sencillas** y solo te tomará **unos minutos**.

**Dime cuándo estés listo(a), estoy aquí para ayudarte** 😊"""
    
    # Reset l'interface avec le message de bienvenue
    st.session_state.messages = [{
        "role": "assistant", 
        "content": welcome_msg,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }]
    st.session_state.conversation_started = False
    
    st.success("✅ Nouvelle conversation démarrée !")
    st.rerun()

async def send_message(user_input: str) -> str:
    """Envoie un message à l'agent"""
    try:
        response = await whatsapp_chat(st.session_state.user_id, user_input)
        return response
    except Exception as e:
        return f"❌ Erreur: {str(e)}"

def main():
    # Vérification des variables d'environnement
    import os
    if not os.getenv("OPENAI_API_KEY"):
        st.error("❌ Variable OPENAI_API_KEY manquante ! Vérifiez votre fichier .env")
        st.stop()
    if not os.getenv("PINECONE_API_KEY"):
        st.error("❌ Variable PINECONE_API_KEY manquante ! Vérifiez votre fichier .env") 
        st.stop()
    
    # Header
    st.title("🤖 Test Agent CCI Colombia")


    
    # Sidebar avec infos et contrôles
    with st.sidebar:
        st.markdown("### 🔧 Contrôles")
        
        # Bouton nouvelle conversation
        if st.button("🔄 Nouvelle conversation", type="primary"):
            reset_conversation()
    
    # Zone de chat
    chat_container = st.container()
    
    # Affichage des messages
    with chat_container:
        # Afficher l'historique des messages (y compris le message de bienvenue)
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message["role"] == "assistant" and "timestamp" in message:
                    st.caption(f" {message['timestamp']}")
    
    # Input utilisateur
    user_input = st.chat_input("Tapez votre message ici...")
    
    if user_input:
        # Ajouter le message utilisateur
        st.session_state.messages.append({
            "role": "user", 
            "content": user_input,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        st.session_state.conversation_started = True
        
        # Afficher le message utilisateur
        with st.chat_message("user"):
            st.write(user_input)
        
        # Obtenir la réponse de l'agent
        with st.chat_message("assistant"):
            with st.spinner("L'agent réfléchit..."):
                response = asyncio.run(send_message(user_input))
            
            st.write(response)
            timestamp = datetime.now().strftime("%H:%M:%S")
            st.caption(f"⏱️ {timestamp}")
        
        # Ajouter la réponse de l'agent
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response,
            "timestamp": timestamp
        })
        
        # Auto-scroll vers le bas
        st.rerun()

if __name__ == "__main__":
    main() 