"""
Gestion de la langue pour l'agent CCI
"""
import os
from app.agents.prompts.prompts_utils import load_prompt, get_prompt_for_language
from app.agents.tools.tools import set_tools_language

async def detect_language_from_input(user_input: str) -> str:
    """Détecte la langue à partir du message utilisateur (fr ou es) en utilisant LLM"""
    from openai import AsyncOpenAI
    import os
    
    try:
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        system_prompt = """Tu es un détecteur de langue expert. 
        Analyse le texte fourni et détermine s'il est en français (fr) ou en espagnol (es).
        Réponds UNIQUEMENT avec 'fr' ou 'es', rien d'autre.
        
        Exemples:
        - "Hola, como estas?" → es
        - "Buenos días" → es  
        - "Bonjour, comment allez-vous?" → fr
        - "Merci beaucoup" → fr
        - "Sí, tengo tiempo" → es
        - "Oui, j'ai du temps" → fr"""
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",  # Plus rapide et moins cher pour cette tâche simple
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Texte à analyser: '{user_input}'"}
            ],
            temperature=0,  # Déterministe
            max_tokens=5   # Juste assez pour "fr" ou "es"
        )
        
        detected_lang = response.choices[0].message.content.strip().lower()
        print(f"🤖 LLM détection: '{user_input}' → '{detected_lang}'")
        
        # Validation de la réponse
        if detected_lang == 'es':
            return 'es'
        elif detected_lang == 'fr':
            return 'fr'
        else:
            # Fallback au cas où le LLM répond autre chose
            print(f"⚠️ LLM a répondu '{detected_lang}', utilisation fallback français")
            return 'fr'
            
    except Exception as e:
        print(f"⚠️ Erreur détection langue LLM: {e}")
        # Fallback simple en cas d'erreur
        if any(word in user_input.lower() for word in ['hola', 'si', 'soy', 'tengo', 'buenos', 'gracias']):
            return 'es'
        return 'fr'

def set_agent_language(agent, lang: str):
    """Adapte l'agent à la langue donnée (fr ou es)"""
    agent.detected_language = lang
    set_tools_language(lang)
    prompt_name = get_prompt_for_language(lang)
    agent.base_system_prompt = load_prompt(prompt_name)
    agent.base_prompt_name = prompt_name
    agent.prompt = agent._build_dynamic_prompt()
    agent._rebuild_agent()
    agent.language_detected = True
    agent.first_interaction = False 