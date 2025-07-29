import os
from openai import AsyncOpenAI
from typing import Literal

LANGUAGE_DETECTION_PROMPT = """Tu es un expert en détection de langue. 

L'utilisateur répond à ce message d'accueil :
"👋 Bonjour ! Je suis YY, votre assistant virtuel de la CCI France-Colombie. Mon rôle est de mieux comprendre vos besoins en tant qu'adhérent(e) et de vous accompagner si vous avez la moindre question concernant nos offres, services, événements. 📝 Ce petit échange comprend 8 questions simples, et ne vous prendra que quelques minutes. Dites-moi quand vous êtes prêt(e), je suis à votre écoute 🎯"

Analyse la réponse de l'utilisateur et détermine s'il répond en français ou en espagnol.

Réponds UNIQUEMENT par "fr" ou "es". Rien d'autre.

Exemples :
- "oui" → fr
- "sí" → es  
- "je suis prêt" → fr
- "estoy listo" → es
- "ok" → fr (par défaut si ambiguë)
- "d'accord" → fr
- "perfecto" → es
- "allons-y" → fr
- "vamos" → es"""

async def detect_language_from_input(user_input: str) -> Literal["fr", "es"]:
    """
    Détecte la langue d'un input utilisateur en utilisant OpenAI GPT-4.
    Plus robuste qu'une détection par mots-clés.
    """
    try:
        # Création directe du client avec la clé du .env
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": LANGUAGE_DETECTION_PROMPT},
                {"role": "user", "content": f"Réponse de l'utilisateur : {user_input}"}
            ],
            temperature=0,
            max_tokens=5  # On attend juste "fr" ou "es"
        )
        
        detected_lang = response.choices[0].message.content.strip().lower()
        
        # Validation et fallback
        if detected_lang in ["fr", "es"]:
            return detected_lang
        else:
            return "fr"  # Fallback par défaut
            
    except Exception as e:
        print(f"Erreur détection langue : {e}")
        # Fallback simple en cas d'erreur OpenAI
        return "fr" if any(word in user_input.lower() for word in ["oui", "prêt", "d'accord"]) else "fr"


def get_welcome_message_static() -> str:
    """
    Retourne le message d'accueil statique (pour référence).
    Ce message sera affiché côté client avant le premier input.
    """
    return """👋 Bonjour ! Je suis YY, votre **assistant virtuel de la CCI France-Colombie**.

Mon rôle est de **mieux comprendre vos besoins** en tant qu'adhérent(e) et de vous **accompagner si vous avez la moindre question concernant nos offres, services, événements.**

📝 Ce petit échange comprend 8 **questions simples**, et ne vous prendra que **quelques minutes**.

**Dites-moi quand vous êtes prêt(e), je suis à votre écoute** 🎯"""