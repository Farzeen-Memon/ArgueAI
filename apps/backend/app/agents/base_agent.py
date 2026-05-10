from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
import openai
import google.generativeai as genai
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from ..core.config import settings
from ..models import Agent, Message, Debate
from ..services.message_service import MessageService

class BaseAgent(ABC):
    def __init__(self, db: AsyncSession, agent_model: Agent):
        self.db = db
        self.agent_model = agent_model
        self.message_service = MessageService(db)
        
        # Initialize LLM based on preference or default
        self.llm = self._initialize_llm()
        
    def _initialize_llm(self):
        """Initialize the appropriate LLM"""
        if settings.OPENAI_API_KEY:
            return ChatOpenAI(
                openai_api_key=settings.OPENAI_API_KEY,
                model="gpt-4-turbo-preview",
                temperature=0.7,
                max_tokens=2000
            )
        elif settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            return ChatGoogleGenerativeAI(
                model="gemini-pro",
                temperature=0.7,
                max_output_tokens=2000
            )
        else:
            raise ValueError("No LLM API key configured")

    @abstractmethod
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process incoming message and generate response"""
        pass

    @abstractmethod
    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Get system prompt for the agent"""
        pass

    async def get_conversation_history(
        self, 
        debate_id: int, 
        limit: int = 10
    ) -> List[Dict[str, str]]:
        """Get recent conversation history"""
        messages, _ = await self.message_service.get_debate_messages(
            debate_id=debate_id,
            user_id=None,  # We'll handle user verification at service level
            skip=0,
            limit=limit
        )
        
        history = []
        for msg in messages:
            role = "assistant" if msg.agent else "user"
            history.append({
                "role": role,
                "content": msg.content,
                "agent_name": msg.agent.name if msg.agent else "User",
                "message_type": msg.message_type
            })
        
        return history

    async def create_message(
        self, 
        debate_id: int, 
        content: str, 
        message_type: str = "argument"
    ) -> Message:
        """Create a new message in the debate"""
        from ..schemas.debate import MessageCreate
        
        message_data = MessageCreate(
            content=content,
            message_type=message_type,
            agent_id=self.agent_model.id
        )
        
        # We'll need user_id - for now, we'll get it from the debate
        debate = await self.db.get(Debate, debate_id)
        return await self.message_service.create_message(
            debate_id=debate_id,
            message_data=message_data,
            user_id=debate.user_id
        )

    async def call_llm(
        self, 
        messages: List[Dict[str, str]], 
        temperature: Optional[float] = None
    ) -> str:
        """Call the LLM with messages"""
        try:
            # Convert messages to LangChain format
            langchain_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    langchain_messages.append(SystemMessage(content=msg["content"]))
                elif msg["role"] == "user":
                    langchain_messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    langchain_messages.append(AIMessage(content=msg["content"]))
            
            # Call LLM
            if temperature:
                self.llm.temperature = temperature
            
            response = await self.llm.ainvoke(langchain_messages)
            return response.content
            
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"

    def format_context(self, context: Dict[str, Any]) -> str:
        """Format context for the agent"""
        formatted_context = []
        
        if "topic" in context:
            formatted_context.append(f"Debate Topic: {context['topic']}")
        
        if "style" in context:
            formatted_context.append(f"Debate Style: {context['style']}")
        
        if "tone" in context:
            formatted_context.append(f"Tone: {context['tone']}")
        
        if "current_round" in context:
            formatted_context.append(f"Current Round: {context['current_round']}")
        
        if "total_rounds" in context:
            formatted_context.append(f"Total Rounds: {context['total_rounds']}")
        
        return "\n".join(formatted_context)

    async def validate_response(self, response: str) -> str:
        """Validate and potentially modify the response"""
        # Basic validation - ensure response is not empty
        if not response or not response.strip():
            return "I apologize, but I don't have a response at this time."
        
        # Length validation
        if len(response) > 5000:
            response = response[:5000] + "... (response truncated)"
        
        return response.strip()

    def get_agent_personality(self) -> str:
        """Get agent personality description"""
        return self.agent_model.personality or ""

    def get_agent_role(self) -> str:
        """Get agent role"""
        return self.agent_model.role.value
