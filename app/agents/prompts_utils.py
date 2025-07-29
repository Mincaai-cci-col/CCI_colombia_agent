"""
Prompt utilities for CCI LangChain Agent
Centralized prompt loading and language-specific prompt selection
"""

from pathlib import Path
from typing import Literal

def load_prompt(prompt_name: str) -> str:
    """
    Load a prompt file from the prompts directory.
    
    Args:
        prompt_name: Name of the prompt file (without .txt extension)
        
    Returns:
        str: Content of the prompt file
        
    Raises:
        FileNotFoundError: If prompt file doesn't exist
    """
    prompt_path = Path(__file__).parent / "prompts" / f"{prompt_name}.txt"
    
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read().strip()

def get_prompt_for_language(lang: Literal["fr", "es"]) -> str:
    """
    Get the appropriate prompt name based on detected language.
    
    Args:
        lang: Detected language code
        
    Returns:
        str: Prompt file name to use
    """
    if lang == "es":
        return "diagnostic_prompt_es"
    else:
        return "diagnostic_prompt"  # French by default 