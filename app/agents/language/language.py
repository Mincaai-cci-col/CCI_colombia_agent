"""
Language detection utilities for CCI Agent
Automatic French/Spanish detection using OpenAI
"""

import os
from typing import Literal
from openai import AsyncOpenAI

async def detect_language_from_input(user_input: str) -> Literal["fr", "es"]:
    """
    Detect language from user input using OpenAI.
    
    Args:
        user_input: Text to analyze
        
    Returns:
        "fr" for French, "es" for Spanish
    """
    try:
        # Create client directly with .env key
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "Détecte la langue du texte : réponds seulement 'fr' pour français ou 'es' pour espagnol."
                },
                {"role": "user", "content": user_input}
            ],
            max_tokens=5  # We only expect "fr" or "es"
        )
        
        detected = response.choices[0].message.content.strip().lower()
        
        # Validation and fallback
        if detected == "es":
            return "es"
        else:
            return "fr"  # Default fallback
            
    except Exception as e:
        print(f"Erreur détection langue : {e}")
        # Simple fallback in case of OpenAI error
        if any(word in user_input.lower() for word in ["hola", "estoy", "soy", "quiero", "necesito", "gracias"]):
            return "es"
        return "fr"

def get_welcome_message_static() -> str:
    """
    Get static bilingual welcome message.
    
    Returns:
        Bilingual welcome message
    """
    return """👋 Bonjour ! Je suis YY, votre assistant virtuel de la CCI France-Colombie.

Mon rôle est de mieux comprendre vos besoins en tant qu'adhérent(e) et de vous accompagner si vous avez la moindre question concernant nos offres, services, événements.

📋 Ce petit échange comprend 8 questions simples, et ne vous prendra que quelques minutes.

Dites-moi quand vous êtes prêt(e), je suis à votre écoute ! 😊

---

👋 ¡Hola! Soy YY, tu asistente virtual de la CCI Francia-Colombia.

Mi objetivo es comprender mejor tus necesidades como miembro y acompañarte si tienes cualquier duda sobre nuestras ofertas, servicios o eventos.

📋 Este breve intercambio contiene 8 preguntas sencillas y solo te tomará unos minutos.

¡Dime cuándo estés listo(a), estoy aquí para ayudarte! 😊"""