"""
Agent LangChain CCI - Version refactorisée et modulaire avec détection de langue
Tools et prompts externalisés pour une meilleure maintenance
Support bilingue français/espagnol
"""

import os
import asyncio
from typing import List, Dict, Any, Literal
from pathlib import Path
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationSummaryBufferMemory

from app.agents.tools import get_agent_tools, set_tools_language
from app.agents.language import detect_language_from_input
from app.agents.prompts_utils import load_prompt, get_prompt_for_language

# =============================================================================
# UTILITAIRES
# =============================================================================

# =============================================================================
# CLASSE AGENT REFACTORISÉE BILINGUE
# =============================================================================

class CCILangChainAgent:
    """
    Agent LangChain CCI refactorisé avec mémoire conversationnelle et support bilingue.
    
    Architecture modulaire :
    - Tools : app/agents/tools.py
    - Prompts : app/agents/prompts/ (français + espagnol)
    - Language : app/utils/language.py
    - Agent : app/agents/langchain_agent.py (ce fichier)
    """
    
    def __init__(self, prompt_name: str = "diagnostic_prompt"):
        """
        Initialise l'agent avec configuration modulaire.
        
        Args:
            prompt_name: Nom du prompt à charger (sans extension)
        """
        # Configuration LLM
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # État de la conversation
        self.detected_language: Literal["fr", "es"] = "fr"  # Français par défaut
        self.language_detected = False  # Flag pour savoir si la langue a été détectée
        self.first_interaction = True
        
        # Charger le prompt système initial
        try:
            system_prompt = load_prompt(prompt_name)
        except Exception as e:
            print(f"⚠️ Erreur chargement prompt: {e}")
            print("🔄 Utilisation du prompt par défaut...")
            system_prompt = "Tu es un agent conversationnel expert de la CCI France-Colombie."
        
        # Mémoire conversationnelle avec résumé automatique
        self.memory = ConversationSummaryBufferMemory(
            llm=self.llm,
            max_token_limit=2000,
            return_messages=True,
            memory_key="chat_history",
            input_key="input",
            output_key="output"
        )
        
        # État du diagnostic
        self.diagnostic_answers: List[Dict[str, Any]] = []
        self.current_question = 1
        
        # Charger les tools depuis le module séparé
        self.tools = get_agent_tools(self)
        
        # Créer le prompt template avec mémoire
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad")
        ])
        
        # Créer l'agent LangChain
        self._rebuild_agent()
    
    def _rebuild_agent(self):
        """Reconstruit l'agent avec la configuration actuelle"""
        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # Executor avec mémoire et configuration
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            max_iterations=3,
            early_stopping_method="generate",
            return_intermediate_steps=True
        )
    
    async def _detect_and_adapt_language(self, user_input: str) -> None:
        """
        Détecte la langue et adapte l'agent si nécessaire
        
        Args:
            user_input: Premier message de l'utilisateur
        """
        if self.language_detected:
            return  # Langue déjà détectée
        
        print(f"🔍 Détection de langue en cours...")
        detected_lang = await detect_language_from_input(user_input)
        
        if detected_lang != self.detected_language:
            print(f"🌍 Langue détectée : {detected_lang}")
            self.detected_language = detected_lang
            
            # Synchroniser la langue avec les tools
            set_tools_language(detected_lang)
            
            # Adapter le prompt selon la langue
            prompt_name = get_prompt_for_language(detected_lang)
            try:
                new_system_prompt = load_prompt(prompt_name)
                
                # Recréer le prompt template
                self.prompt = ChatPromptTemplate.from_messages([
                    ("system", new_system_prompt),
                    MessagesPlaceholder("chat_history"),
                    ("human", "{input}"),
                    MessagesPlaceholder("agent_scratchpad")
                ])
                
                # Reconstruire l'agent
                self._rebuild_agent()
                
                print(f"✅ Agent et tools adaptés pour la langue : {detected_lang}")
                
            except Exception as e:
                print(f"⚠️ Erreur adaptation langue : {e}")
        
        self.language_detected = True
    
    async def chat(self, user_input: str, user_id: str = "demo_user") -> str:
        """
        Conversation avec l'agent bilingue.
        
        Args:
            user_input: Message de l'utilisateur
            user_id: ID utilisateur pour les logs
            
        Returns:
            str: Réponse de l'agent
        """
        try:
            # Détection de langue au premier message
            if self.first_interaction:
                await self._detect_and_adapt_language(user_input)
                self.first_interaction = False
            
            # Log user input - commenté pour l'instant
            # asyncio.create_task(
            #     log_interaction_async(user_id=user_id, role="user", content=user_input)
            # )
            
            # Appel à l'agent avec mémoire automatique
            result = await self.agent_executor.ainvoke({
                "input": user_input
            })
            
            agent_response = result["output"]
            
            # Log agent response - commenté pour l'instant
            # asyncio.create_task(
            #     log_interaction_async(user_id=user_id, role="agent", content=agent_response)
            # )
            
            # Traiter les tool calls pour mettre à jour l'état
            self._process_tool_calls(result)
            
            return agent_response
            
        except Exception as e:
            error_msg = f"Désolé, j'ai rencontré un problème technique. Pouvons-nous continuer ? (Erreur: {str(e)})"
            if self.detected_language == "es":
                error_msg = f"Disculpe, encontré un problema técnico. ¿Podemos continuar? (Error: {str(e)})"
            return error_msg
    
    def _process_tool_calls(self, result: Dict[str, Any]) -> None:
        """
        Traite les tool calls pour mettre à jour l'état interne.
        
        Args:
            result: Résultat de l'exécution de l'agent
        """
        if "intermediate_steps" not in result:
            return
            
        for step in result["intermediate_steps"]:
            action, observation = step
            
            # Collecte de réponse diagnostic
            if action.tool == "collect_diagnostic_answer":
                tool_input = action.tool_input
                self.diagnostic_answers.append({
                    "question": self.current_question,
                    "answer": tool_input.get("answer", ""),
                    "question_number": tool_input.get("question_number", self.current_question),
                    "language": self.detected_language
                })
                self.current_question = min(self.current_question + 1, 8)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Obtient le statut complet de l'agent et du diagnostic.
        
        Returns:
            dict: Informations sur l'état actuel
        """
        memory_history = self.memory.chat_memory.messages if self.memory.chat_memory else []
        
        return {
            "current_question": self.current_question,
            "answers_collected": len(self.diagnostic_answers),
            "diagnostic_answers": self.diagnostic_answers,
            "detected_language": self.detected_language,
            "language_detected": self.language_detected,
            "memory_messages": len(memory_history),
            "memory_summary": getattr(self.memory, 'moving_summary_buffer', 'Pas de résumé'),
            "is_diagnostic_complete": self.current_question > 8,
            "first_interaction": self.first_interaction
        }
    
    def serialize_state(self) -> Dict[str, Any]:
        """
        Sérialise l'état complet de l'agent pour la persistance (WhatsApp, Redis, DB)
        
        Returns:
            dict: État sérialisé de l'agent
        """
        # Sérialiser les messages de mémoire
        memory_messages = []
        if self.memory.chat_memory and self.memory.chat_memory.messages:
            for msg in self.memory.chat_memory.messages:
                memory_messages.append({
                    "type": msg.__class__.__name__,
                    "content": msg.content,
                    "role": getattr(msg, 'role', None)
                })
        
        # Obtenir le résumé de la mémoire
        memory_summary = ""
        try:
            memory_summary = getattr(self.memory, 'moving_summary_buffer', '')
        except:
            pass
        
        return {
            "current_question": self.current_question,
            "diagnostic_answers": self.diagnostic_answers,
            "detected_language": self.detected_language,
            "language_detected": self.language_detected,
            "first_interaction": self.first_interaction,
            "memory_messages": memory_messages,
            "memory_summary": memory_summary,
            "version": "1.0"  # Pour gestion des migrations futures
        }
    
    def load_state(self, state: Dict[str, Any]) -> None:
        """
        Charge l'état de l'agent depuis des données sérialisées (WhatsApp, Redis, DB)
        
        Args:
            state: État sérialisé de l'agent
        """
        if not state:
            return
        
        # Charger l'état basique
        self.current_question = state.get("current_question", 1)
        self.diagnostic_answers = state.get("diagnostic_answers", [])
        self.detected_language = state.get("detected_language", "fr")
        self.language_detected = state.get("language_detected", False)
        self.first_interaction = state.get("first_interaction", True)
        
        # Recharger la langue dans les tools si détectée
        if self.language_detected:
            set_tools_language(self.detected_language)
            
            # Adapter le prompt selon la langue
            prompt_name = get_prompt_for_language(self.detected_language)
            try:
                system_prompt = load_prompt(prompt_name)
                self.prompt = ChatPromptTemplate.from_messages([
                    ("system", system_prompt),
                    MessagesPlaceholder("chat_history"),
                    ("human", "{input}"),
                    MessagesPlaceholder("agent_scratchpad")
                ])
                self._rebuild_agent()
            except Exception as e:
                print(f"⚠️ Erreur rechargement prompt : {e}")
        
        # Recharger la mémoire de façon plus robuste
        try:
            # D'abord, essayer de recharger le résumé
            memory_summary = state.get("memory_summary", "")
            if memory_summary:
                self.memory.moving_summary_buffer = memory_summary
            
            # Ensuite, recharger les messages de l'historique
            memory_messages = state.get("memory_messages", [])
            if memory_messages:
                from langchain_core.messages import HumanMessage, AIMessage
                
                # Vider l'historique actuel
                self.memory.chat_memory.clear()
                
                # Recharger les messages
                for msg_data in memory_messages:
                    if msg_data.get("type") == "HumanMessage":
                        self.memory.chat_memory.add_message(HumanMessage(content=msg_data["content"]))
                    elif msg_data.get("type") == "AIMessage":
                        self.memory.chat_memory.add_message(AIMessage(content=msg_data["content"]))
                        
        except Exception as e:
            print(f"⚠️ Erreur rechargement mémoire : {e}")
            # En cas d'erreur, au moins garder le résumé
            try:
                memory_summary = state.get("memory_summary", "")
                if memory_summary:
                    self.memory.moving_summary_buffer = memory_summary
            except:
                pass
    
    @classmethod
    def from_state(cls, state: Dict[str, Any], prompt_name: str = "diagnostic_prompt") -> 'CCILangChainAgent':
        """
        Crée une instance d'agent depuis un état sérialisé (pour WhatsApp)
        
        Args:
            state: État sérialisé
            prompt_name: Nom du prompt à utiliser
            
        Returns:
            CCILangChainAgent: Instance configurée avec l'état chargé
        """
        # Créer une nouvelle instance
        agent = cls(prompt_name=prompt_name)
        
        # Charger l'état
        agent.load_state(state)
        
        return agent
    
    def get_memory_content(self) -> str:
        """
        Obtient le contenu de la mémoire pour debug.
        
        Returns:
            str: Contenu de la mémoire
        """
        try:
            return self.memory.buffer
        except:
            return "Mémoire vide"
    
    def reset(self) -> None:
        """Reset l'agent pour une nouvelle conversation"""
        self.memory.clear()
        self.diagnostic_answers = []
        self.current_question = 1
        self.detected_language = "fr"
        self.language_detected = False
        self.first_interaction = True
        
        # Reset la langue des tools au français
        set_tools_language("fr")
    
    def set_language(self, lang: Literal["fr", "es"]) -> bool:
        """
        Force une langue spécifique (utile pour les tests)
        
        Args:
            lang: Langue à utiliser
            
        Returns:
            bool: True si succès
        """
        try:
            self.detected_language = lang
            
            # Synchroniser la langue avec les tools
            set_tools_language(lang)
            
            prompt_name = get_prompt_for_language(lang)
            system_prompt = load_prompt(prompt_name)
            
            # Recréer le prompt template
            self.prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder("agent_scratchpad")
            ])
            
            # Reconstruire l'agent
            self._rebuild_agent()
            self.language_detected = True
            self.first_interaction = False
            
            return True
        except Exception as e:
            print(f"Erreur définition langue : {e}")
            return False

# =============================================================================
# FONCTION FACTORY
# =============================================================================

def create_cci_agent(prompt_name: str = "diagnostic_prompt") -> CCILangChainAgent:
    """
    Factory pour créer une instance de l'agent CCI bilingue.
    
    Args:
        prompt_name: Nom du prompt à utiliser
        
    Returns:
        CCILangChainAgent: Instance configurée de l'agent
    """
    return CCILangChainAgent(prompt_name=prompt_name) 