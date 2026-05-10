from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from .base_agent import BaseAgent
from ..models import Agent

class ProArgumentAgent(BaseAgent):
    def __init__(self, db: AsyncSession, agent_model: Agent):
        super().__init__(db, agent_model)
        self.position = "pro"

    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Get system prompt for pro argument agent"""
        base_prompt = f"""You are the PRO argument agent in an AI debate on the topic: "{context.get('topic', 'Unknown topic')}".

Your role is to:
1. Present strong arguments in favor of the topic
2. Provide evidence and reasoning to support your position
3. Address counter-arguments effectively
4. Maintain a consistent {context.get('tone', 'formal')} tone
5. Follow {context.get('style', 'formal')} debate style

Debate Style: {context.get('style', 'formal')}
Tone: {context.get('tone', 'formal')}
Current Round: {context.get('current_round', 1)} of {context.get('total_rounds', 3)}

Guidelines:
- Start with a clear position statement
- Use logical reasoning and evidence
- Be persuasive but respectful
- Anticipate counter-arguments
- Adapt your strategy based on round progression

{self.get_agent_personality()}

Current context:
{self.format_context(context)}"""
        
        return base_prompt

    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process message and generate pro argument"""
        # Get conversation history
        history = await self.get_conversation_history(context.get('debate_id', 0))
        
        # Build messages for LLM
        messages = [
            {"role": "system", "content": self.get_system_prompt(context)}
        ]
        
        # Add conversation history
        for msg in history[-8:]:  # Last 8 messages
            messages.append({
                "role": msg["role"],
                "content": f"[{msg['agent_name']}]: {msg['content']}"
            })
        
        # Determine prompt based on context
        current_round = context.get('current_round', 1)
        
        if current_round == 1 and not any(msg['agent_name'] == 'Pro Argument' for msg in history):
            # Opening argument
            prompt = "Please present your opening argument in favor of the topic. Start with a clear position statement and provide 2-3 main supporting points with evidence."
        elif message and 'con_argument' in message.lower():
            # Responding to counter-argument
            prompt = f"The opposing agent has presented arguments against the topic. Please provide a strong rebuttal addressing their key points and reinforce your position with additional evidence."
        else:
            # General argument
            prompt = "Please present arguments in favor of the topic, building upon previous discussion and addressing any counter-arguments made."
        
        messages.append({"role": "user", "content": prompt})
        
        # Get response from LLM
        response = await self.call_llm(messages, temperature=0.7)
        
        # Validate response
        return await self.validate_response(response)

    async def create_opening_argument(self, debate_id: int, topic: str, style: str, tone: str) -> str:
        """Create opening argument"""
        context = {
            'debate_id': debate_id,
            'topic': topic,
            'style': style,
            'tone': tone,
            'current_round': 1,
            'total_rounds': 3
        }
        
        return await self.process_message("", context)

    async def create_rebuttal(self, debate_id: int, counter_argument: str, topic: str) -> str:
        """Create rebuttal to counter-argument"""
        context = {
            'debate_id': debate_id,
            'topic': topic,
            'current_round': 1
        }
        
        return await self.process_message(counter_argument, context)

class ConArgumentAgent(BaseAgent):
    def __init__(self, db: AsyncSession, agent_model: Agent):
        super().__init__(db, agent_model)
        self.position = "con"

    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Get system prompt for con argument agent"""
        base_prompt = f"""You are the CON argument agent in an AI debate on the topic: "{context.get('topic', 'Unknown topic')}".

Your role is to:
1. Present strong arguments against the topic
2. Challenge the pro position effectively
3. Identify flaws in opposing arguments
4. Maintain a consistent {context.get('tone', 'formal')} tone
5. Follow {context.get('style', 'formal')} debate style

Debate Style: {context.get('style', 'formal')}
Tone: {context.get('tone', 'formal')}
Current Round: {context.get('current_round', 1)} of {context.get('total_rounds', 3)}

Guidelines:
- Start with a clear counter-position
- Use critical thinking and analysis
- Be constructive in your criticism
- Identify logical fallacies in opposing arguments
- Provide alternative perspectives

{self.get_agent_personality()}

Current context:
{self.format_context(context)}"""
        
        return base_prompt

    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process message and generate con argument"""
        # Get conversation history
        history = await self.get_conversation_history(context.get('debate_id', 0))
        
        # Build messages for LLM
        messages = [
            {"role": "system", "content": self.get_system_prompt(context)}
        ]
        
        # Add conversation history
        for msg in history[-8:]:  # Last 8 messages
            messages.append({
                "role": msg["role"],
                "content": f"[{msg['agent_name']}]: {msg['content']}"
            })
        
        # Determine prompt based on context
        current_round = context.get('current_round', 1)
        
        if current_round == 1 and not any(msg['agent_name'] == 'Con Argument' for msg in history):
            # Opening counter-argument
            prompt = "Please present your opening argument against the topic. Start with a clear counter-position and provide 2-3 main points challenging the topic."
        elif message and 'pro_argument' in message.lower():
            # Responding to pro argument
            prompt = f"The pro agent has presented arguments in favor of the topic. Please provide a strong counter-argument addressing their key points and identifying flaws in their reasoning."
        else:
            # General counter-argument
            prompt = "Please present arguments against the topic, challenging the pro position and providing critical analysis."
        
        messages.append({"role": "user", "content": prompt})
        
        # Get response from LLM
        response = await self.call_llm(messages, temperature=0.7)
        
        # Validate response
        return await self.validate_response(response)

    async def create_counter_argument(self, debate_id: int, pro_argument: str, topic: str, style: str, tone: str) -> str:
        """Create counter-argument"""
        context = {
            'debate_id': debate_id,
            'topic': topic,
            'style': style,
            'tone': tone,
            'current_round': 1,
            'total_rounds': 3
        }
        
        return await self.process_message(pro_argument, context)

    async def create_rebuttal(self, debate_id: int, pro_rebuttal: str, topic: str) -> str:
        """Create rebuttal to pro rebuttal"""
        context = {
            'debate_id': debate_id,
            'topic': topic,
            'current_round': 1
        }
        
        return await self.process_message(pro_rebuttal, context)
