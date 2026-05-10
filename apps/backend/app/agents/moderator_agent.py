from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from .base_agent import BaseAgent
from ..models import Agent, Debate

class ModeratorAgent(BaseAgent):
    def __init__(self, db: AsyncSession, agent_model: Agent):
        super().__init__(db, agent_model)
        self.role = "moderator"

    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Get system prompt for moderator agent"""
        base_prompt = f"""You are the Moderator for an AI debate on the topic: "{context.get('topic', 'Unknown topic')}".

Your role is to:
1. Introduce the debate topic and format
2. Ensure the debate stays on track
3. Enforce debate rules and timing
4. Provide summaries after each round
5. Maintain a respectful and productive atmosphere

Debate Style: {context.get('style', 'formal')}
Tone: {context.get('tone', 'formal')}
Current Round: {context.get('current_round', 1)} of {context.get('total_rounds', 3)}

Guidelines:
- Be impartial and fair to all participants
- Keep introductions concise but engaging
- Summarize key points objectively
- Intervene if discussions go off-topic
- Maintain the agreed-upon debate format

{self.get_agent_personality()}

Current context:
{self.format_context(context)}"""
        
        return base_prompt

    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process message as moderator"""
        # Get conversation history
        history = await self.get_conversation_history(context.get('debate_id', 0))
        
        # Build messages for LLM
        messages = [
            {"role": "system", "content": self.get_system_prompt(context)}
        ]
        
        # Add conversation history
        for msg in history[-10:]:  # Last 10 messages
            messages.append({
                "role": msg["role"],
                "content": f"[{msg['agent_name']}]: {msg['content']}"
            })
        
        # Add current message if provided
        if message:
            messages.append({
                "role": "user",
                "content": message
            })
        
        # Determine moderator action based on context
        current_round = context.get('current_round', 1)
        total_rounds = context.get('total_rounds', 3)
        
        if current_round == 1 and not history:
            # First message - introduce debate
            prompt = "Please introduce this debate, explain the format, and invite the first speaker to begin."
        elif context.get('action') == 'summarize_round':
            # Summarize current round
            prompt = "Please provide a concise summary of the key arguments and counter-arguments made in this round."
        elif context.get('action') == 'next_round':
            # Transition to next round
            prompt = f"Please transition to Round {current_round + 1} and outline the focus for this round."
        elif context.get('action') == 'conclude_debate':
            # Conclude debate
            prompt = "Please provide closing remarks and thank all participants for their contributions."
        else:
            # Default moderation
            prompt = "Please provide appropriate moderation based on the current state of the debate."
        
        messages.append({"role": "user", "content": prompt})
        
        # Get response from LLM
        response = await self.call_llm(messages, temperature=0.3)
        
        # Validate response
        return await self.validate_response(response)

    async def introduce_debate(self, debate_id: int, topic: str, style: str, tone: str) -> str:
        """Introduce the debate"""
        context = {
            'debate_id': debate_id,
            'topic': topic,
            'style': style,
            'tone': tone,
            'current_round': 1,
            'total_rounds': 3,
            'action': 'introduce'
        }
        
        return await self.process_message("", context)

    async def summarize_round(
        self, 
        debate_id: int, 
        round_number: int, 
        topic: str
    ) -> str:
        """Summarize a debate round"""
        context = {
            'debate_id': debate_id,
            'topic': topic,
            'current_round': round_number,
            'action': 'summarize_round'
        }
        
        return await self.process_message("", context)

    async def transition_to_next_round(
        self, 
        debate_id: int, 
        next_round: int, 
        topic: str
    ) -> str:
        """Transition to the next round"""
        context = {
            'debate_id': debate_id,
            'topic': topic,
            'current_round': next_round,
            'action': 'next_round'
        }
        
        return await self.process_message("", context)

    async def conclude_debate(self, debate_id: int, topic: str) -> str:
        """Conclude the debate"""
        context = {
            'debate_id': debate_id,
            'topic': topic,
            'action': 'conclude_debate'
        }
        
        return await self.process_message("", context)

    async def moderate_discussion(
        self, 
        debate_id: int, 
        issue: str = ""
    ) -> str:
        """Moderate ongoing discussion"""
        context = {
            'debate_id': debate_id,
            'issue': issue
        }
        
        return await self.process_message(issue, context)
