from pathlib import Path
from typing import Literal

def load_prompt(prompt_name: str) -> str:
    """
    Charge un prompt depuis le dossier prompts/
    Args:
        prompt_name: Nom du fichier prompt (sans extension)
    Returns:
        str: Contenu du prompt
    """
    prompt_path = Path(__file__).parent / "prompts" / f"{prompt_name}.txt"
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        raise FileNotFoundError(f"Prompt '{prompt_name}' non trouvé dans {prompt_path}")
    except Exception as e:
        raise Exception(f"Erreur lors du chargement du prompt '{prompt_name}': {e}")

def get_prompt_for_language(lang: Literal["fr", "es"]) -> str:
    """
    Retourne le nom du prompt selon la langue détectée
    Args:
        lang: Langue détectée ("fr" ou "es")
    Returns:
        str: Nom du fichier prompt à charger
    """
    if lang == "es":
        return "diagnostic_prompt_es"
    else:
        return "diagnostic_prompt"  # français par défaut 