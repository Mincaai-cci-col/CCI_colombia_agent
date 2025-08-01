"""
Gestion de la langue pour l'agent CCI
"""
import os
from app.agents.prompts.prompts_utils import load_prompt, get_prompt_for_language
from app.agents.tools.tools import set_tools_language

async def detect_language_from_input(user_input: str) -> str:
    """Détecte la langue à partir du message utilisateur (fr ou es)"""
    from langdetect import detect
    try:
        lang = detect(user_input)
        if lang == 'es':
            return 'es'
        return 'fr'
    except Exception:
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