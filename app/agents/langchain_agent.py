"""
LangChain CCI Agent - Refactored and modular version with language detection
Tools and prompts externalized for better maintenance
Bilingual support French/Spanish
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
# UTILITIES
# =============================================================================

# =============================================================================
# REFACTORED BILINGUAL AGENT CLASS
# =============================================================================

class CCILangChainAgent:
    """
    Refactored CCI LangChain Agent with conversational memory and bilingual support.
    
    Modular architecture:
    - Tools: app/agents/tools.py
    - Prompts: app/agents/prompts/ (French + Spanish)
    - Language: app/utils/language.py
    - Agent: app/agents/langchain_agent.py (this file)
    """
    
    def __init__(self, prompt_name: str = "diagnostic_prompt"):
        """
        Initialize the agent with modular configuration.
        
        Args:
            prompt_name: Name of the prompt to load (without extension)
        """
        # LLM configuration
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Conversation state
        self.detected_language: Literal["fr", "es"] = "fr"  # French by default
        self.language_detected = False  # Flag to know if language has been detected
        self.first_interaction = True
        
        # Load initial system prompt
        try:
            system_prompt = load_prompt(prompt_name)
        except Exception as e:
            print(f"⚠️ Erreur chargement prompt: {e}")
            print("🔄 Utilisation du prompt par défaut...")
            system_prompt = "Tu es un agent conversationnel expert de la CCI France-Colombie."
        
        # Conversational memory with automatic summarization
        self.memory = ConversationSummaryBufferMemory(
            llm=self.llm,
            max_token_limit=2000,
            return_messages=True,
            memory_key="chat_history",
            input_key="input",
            output_key="output"
        )
        
        # Diagnostic state - simplified
        self.current_question = 1
        
        # Load tools from separate module
        self.tools = get_agent_tools(self)
        
        # Create prompt template with memory
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad")
        ])
        
        # Create LangChain agent
        self._rebuild_agent()
    
    def _rebuild_agent(self):
        """Rebuild agent with current configuration"""
        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # Executor with memory and configuration
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
        Detect language and adapt agent if necessary
        
        Args:
            user_input: First user message
        """
        if self.language_detected:
            return  # Language already detected
        
        print(f"🔍 Détection de langue en cours...")
        detected_lang = await detect_language_from_input(user_input)
        
        if detected_lang != self.detected_language:
            print(f"🌍 Langue détectée : {detected_lang}")
            self.detected_language = detected_lang
            
            # Synchronize language with tools
            set_tools_language(detected_lang)
            
            # Adapt prompt according to language
            prompt_name = get_prompt_for_language(detected_lang)
            try:
                new_system_prompt = load_prompt(prompt_name)
                
                # Recreate prompt template
                self.prompt = ChatPromptTemplate.from_messages([
                    ("system", new_system_prompt),
                    MessagesPlaceholder("chat_history"),
                    ("human", "{input}"),
                    MessagesPlaceholder("agent_scratchpad")
                ])
                
                # Rebuild agent
                self._rebuild_agent()
                
                print(f"✅ Agent et tools adaptés pour la langue : {detected_lang}")
                
            except Exception as e:
                print(f"⚠️ Erreur adaptation langue : {e}")
        
        self.language_detected = True
    
    async def chat(self, user_input: str, user_id: str = "demo_user") -> str:
        """
        Conversation with bilingual agent.
        
        Args:
            user_input: User message
            user_id: User ID for logs
            
        Returns:
            str: Agent response
        """
        try:
            # Language detection on first message
            if self.first_interaction:
                await self._detect_and_adapt_language(user_input)
                self.first_interaction = False
            
            # Log user input - commented for now
            # asyncio.create_task(
            #     log_interaction_async(user_id=user_id, role="user", content=user_input)
            # )
            
            # Call agent with automatic memory
            result = await self.agent_executor.ainvoke({
                "input": user_input
            })
            
            agent_response = result["output"]
            
            # Log agent response - commented for now
            # asyncio.create_task(
            #     log_interaction_async(user_id=user_id, role="agent", content=agent_response)
            # )
            
            # Process tool calls to update state
            self._process_tool_calls(result)
            
            return agent_response
            
        except Exception as e:
            error_msg = f"Désolé, j'ai rencontré un problème technique. Pouvons-nous continuer ? (Erreur: {str(e)})"
            if self.detected_language == "es":
                error_msg = f"Disculpe, encontré un problema técnico. ¿Podemos continuar? (Error: {str(e)})"
            return error_msg
    
    def _process_tool_calls(self, result: Dict[str, Any]) -> None:
        """
        Process tool calls to update internal state.
        
        Args:
            result: Agent execution result
        """
        if "intermediate_steps" not in result:
            print(f"⚠️ No intermediate_steps in result. Current question: {self.current_question}")
            return
            
        print(f"🔍 Processing {len(result['intermediate_steps'])} tool calls. Current question: {self.current_question}")
        
        for step in result["intermediate_steps"]:
            action, observation = step
            print(f"🔧 Tool used: {action.tool}")
            
            # Simple question counter
            if action.tool == "question_asked":
                self.current_question = min(self.current_question + 1, 9)  # Max 8 questions
                print(f"📊 Question asked! Now at question {self.current_question}/8")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get complete status of agent and diagnostic.
        
        Returns:
            dict: Current state information
        """
        memory_history = self.memory.chat_memory.messages if self.memory.chat_memory else []
        
        questions_asked = max(0, self.current_question - 1)  # Since we start at 1
        
        return {
            "current_question": self.current_question,
            "questions_asked": questions_asked,
            "detected_language": self.detected_language,
            "language_detected": self.language_detected,
            "memory_messages": len(memory_history),
            "is_diagnostic_complete": questions_asked >= 8,
            "first_interaction": self.first_interaction
        }
    
    def serialize_state(self) -> Dict[str, Any]:
        """
        Serialize complete agent state for persistence (WhatsApp, Redis, DB)
        
        Returns:
            dict: Serialized agent state
        """
        # Serialize memory messages
        memory_messages = []
        if self.memory.chat_memory and self.memory.chat_memory.messages:
            for msg in self.memory.chat_memory.messages:
                memory_messages.append({
                    "type": msg.__class__.__name__,
                    "content": msg.content,
                    "role": getattr(msg, 'role', None)
                })
        
        # Get memory summary
        memory_summary = ""
        try:
            memory_summary = getattr(self.memory, 'moving_summary_buffer', '')
        except:
            pass
        
        return {
            "current_question": self.current_question,
            "detected_language": self.detected_language,
            "language_detected": self.language_detected,
            "first_interaction": self.first_interaction,
            "memory_messages": memory_messages,
            "memory_summary": memory_summary,
            "version": "2.0"  # Updated version for simplified state
        }
    
    def load_state(self, state: Dict[str, Any]) -> None:
        """
        Load agent state from serialized data (WhatsApp, Redis, DB)
        
        Args:
            state: Serialized agent state
        """
        if not state:
            return
        
        # Load basic state
        self.current_question = state.get("current_question", 1)
        self.detected_language = state.get("detected_language", "fr")
        self.language_detected = state.get("language_detected", False)
        self.first_interaction = state.get("first_interaction", True)
        
        # Reload language in tools if detected
        if self.language_detected:
            set_tools_language(self.detected_language)
            
            # Adapt prompt according to language
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
        
        # Reload memory more robustly
        try:
            # First, try to reload summary
            memory_summary = state.get("memory_summary", "")
            if memory_summary:
                self.memory.moving_summary_buffer = memory_summary
            
            # Then, reload message history
            memory_messages = state.get("memory_messages", [])
            if memory_messages:
                from langchain_core.messages import HumanMessage, AIMessage
                
                # Clear current history
                self.memory.chat_memory.clear()
                
                # Reload messages
                for msg_data in memory_messages:
                    if msg_data.get("type") == "HumanMessage":
                        self.memory.chat_memory.add_message(HumanMessage(content=msg_data["content"]))
                    elif msg_data.get("type") == "AIMessage":
                        self.memory.chat_memory.add_message(AIMessage(content=msg_data["content"]))
                        
        except Exception as e:
            print(f"⚠️ Erreur rechargement mémoire : {e}")
            # In case of error, at least keep the summary
            try:
                memory_summary = state.get("memory_summary", "")
                if memory_summary:
                    self.memory.moving_summary_buffer = memory_summary
            except:
                pass
    
    @classmethod
    def from_state(cls, state: Dict[str, Any], prompt_name: str = "diagnostic_prompt") -> 'CCILangChainAgent':
        """
        Create agent instance from serialized state (for WhatsApp)
        
        Args:
            state: Serialized state
            prompt_name: Prompt name to use
            
        Returns:
            CCILangChainAgent: Instance configured with loaded state
        """
        # Create new instance
        agent = cls(prompt_name=prompt_name)
        
        # Load state
        agent.load_state(state)
        
        return agent
    
    def get_memory_content(self) -> str:
        """
        Get memory content for debug.
        
        Returns:
            str: Memory content
        """
        try:
            return self.memory.buffer
        except:
            return "Mémoire vide"
    
    def reset(self) -> None:
        """Reset agent for new conversation"""
        self.memory.clear()
        self.current_question = 1
        self.detected_language = "fr"
        self.language_detected = False
        self.first_interaction = True
        
        # Reset tools language to French
        set_tools_language("fr")
    
    def set_language(self, lang: Literal["fr", "es"]) -> bool:
        """
        Force specific language (useful for tests)
        
        Args:
            lang: Language to use
            
        Returns:
            bool: True if successful
        """
        try:
            self.detected_language = lang
            
            # Synchronize language with tools
            set_tools_language(lang)
            
            prompt_name = get_prompt_for_language(lang)
            system_prompt = load_prompt(prompt_name)
            
            # Recreate prompt template
            self.prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder("agent_scratchpad")
            ])
            
            # Rebuild agent
            self._rebuild_agent()
            self.language_detected = True
            self.first_interaction = False
            
            return True
        except Exception as e:
            print(f"Erreur définition langue : {e}")
            return False

# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_cci_agent(prompt_name: str = "diagnostic_prompt") -> CCILangChainAgent:
    """
    Factory to create CCI bilingual agent instance.
    
    Args:
        prompt_name: Prompt name to use
        
    Returns:
        CCILangChainAgent: Configured agent instance
    """
    return CCILangChainAgent(prompt_name=prompt_name) 