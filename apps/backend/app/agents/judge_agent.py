from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from .base_agent import BaseAgent
from ..models import Agent, Message
from ..services.message_service import MessageService

class JudgeAgent(BaseAgent):
    def __init__(self, db: AsyncSession, agent_model: Agent):
        super().__init__(db, agent_model)
        self.role = "judge"
        self.message_service = MessageService(db)

    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Get system prompt for judge agent"""
        base_prompt = f"""You are the Judge for an AI debate on topic: "{context.get('topic', 'Unknown topic')}".

Your role is to:
1. Evaluate argument quality and effectiveness
2. Assess logical consistency and evidence quality
3. Score debate performance objectively
4. Provide final verdict with detailed reasoning
5. Identify strengths and weaknesses of each position

Scoring Criteria (0-100 points each):
- Argument Quality: Logic, structure, clarity
- Evidence Support: Quality and relevance of evidence
- Rebuttal Effectiveness: Success in countering opponent
- Persuasiveness: Overall impact and convincing power
- Consistency: Maintaining position throughout debate

Debate Style: {context.get('style', 'formal')}
Tone: {context.get('tone', 'formal')}
Total Rounds: {context.get('total_rounds', 3)}

{self.get_agent_personality()}

Current context:
{self.format_context(context)}"""
        
        return base_prompt

    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process message and generate judgment"""
        # Get full debate history
        debate_id = context.get('debate_id', 0)
        all_messages, _ = await self.message_service.get_debate_messages(
            debate_id=debate_id,
            user_id=None,  # We'll handle user verification at service level
            skip=0,
            limit=100
        )
        
        # Analyze debate performance
        analysis = await self.analyze_debate_performance(all_messages, context)
        
        # Generate final verdict
        verdict = await self.generate_verdict(analysis, context)
        
        return verdict

    async def analyze_debate_performance(self, messages: List[Message], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance of both sides"""
        pro_messages = []
        con_messages = []
        
        for msg in messages:
            if msg.agent and 'pro_argument' in msg.agent.role.value:
                pro_messages.append(msg)
            elif msg.agent and 'con_argument' in msg.agent.role.value:
                con_messages.append(msg)
        
        # Analyze each side
        pro_analysis = await self.analyze_side_performance(pro_messages, "pro")
        con_analysis = await self.analyze_side_performance(con_messages, "con")
        
        return {
            "pro": pro_analysis,
            "con": con_analysis,
            "total_messages": len(messages),
            "topic": context.get('topic', ''),
            "style": context.get('style', 'formal')
        }

    async def analyze_side_performance(self, messages: List[Message], side: str) -> Dict[str, Any]:
        """Analyze performance of one side"""
        if not messages:
            return {
                "side": side,
                "argument_quality": 0,
                "evidence_support": 0,
                "rebuttal_effectiveness": 0,
                "persuasiveness": 0,
                "consistency": 0,
                "total_score": 0,
                "message_count": 0,
                "total_tokens": 0
            }
        
        # Combine all messages for analysis
        combined_text = " ".join([msg.content for msg in messages])
        total_tokens = sum(msg.token_count for msg in messages)
        
        # Use LLM to analyze performance
        analysis_prompt = f"""
Analyze the {side} side's debate performance based on these messages:

{combined_text[:4000]}  # Limit to prevent token overflow

Evaluate on these criteria (0-100 scale):
1. Argument Quality: Logic, structure, clarity
2. Evidence Support: Quality and relevance of evidence  
3. Rebuttal Effectiveness: Success in countering opponent
4. Persuasiveness: Overall impact and convincing power
5. Consistency: Maintaining position throughout debate

Respond in JSON format:
{{
  "argument_quality": 0-100,
  "evidence_support": 0-100,
  "rebuttal_effectiveness": 0-100,
  "persuasiveness": 0-100,
  "consistency": 0-100,
  "strengths": ["strength1", "strength2"],
  "weaknesses": ["weakness1", "weakness2"],
  "key_arguments": ["arg1", "arg2"],
  "overall_assessment": "brief assessment"
}}"""
        
        messages_for_llm = [
            {"role": "system", "content": "You are a debate judge analyzing performance. Be objective and thorough."},
            {"role": "user", "content": analysis_prompt}
        ]
        
        try:
            response = await self.call_llm(messages_for_llm, temperature=0.2)
            import json
            analysis = json.loads(response)
            
            # Calculate total score
            total_score = (
                analysis.get("argument_quality", 0) +
                analysis.get("evidence_support", 0) +
                analysis.get("rebuttal_effectiveness", 0) +
                analysis.get("persuasiveness", 0) +
                analysis.get("consistency", 0)
            ) / 5
            
            return {
                "side": side,
                "argument_quality": analysis.get("argument_quality", 0),
                "evidence_support": analysis.get("evidence_support", 0),
                "rebuttal_effectiveness": analysis.get("rebuttal_effectiveness", 0),
                "persuasiveness": analysis.get("persuasiveness", 0),
                "consistency": analysis.get("consistency", 0),
                "total_score": round(total_score, 1),
                "message_count": len(messages),
                "total_tokens": total_tokens,
                "strengths": analysis.get("strengths", []),
                "weaknesses": analysis.get("weaknesses", []),
                "key_arguments": analysis.get("key_arguments", []),
                "overall_assessment": analysis.get("overall_assessment", "")
            }
            
        except Exception as e:
            print(f"Error analyzing performance: {e}")
            return {
                "side": side,
                "argument_quality": 50,
                "evidence_support": 50,
                "rebuttal_effectiveness": 50,
                "persuasiveness": 50,
                "consistency": 50,
                "total_score": 50,
                "message_count": len(messages),
                "total_tokens": total_tokens,
                "strengths": [],
                "weaknesses": ["Analysis failed"],
                "key_arguments": [],
                "overall_assessment": "Unable to complete analysis"
            }

    async def generate_verdict(self, analysis: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate final verdict"""
        pro_score = analysis["pro"]["total_score"]
        con_score = analysis["con"]["total_score"]
        
        # Determine winner
        if pro_score > con_score + 5:  # 5 point margin for decisive win
            winner = "Pro Position"
            winner_analysis = analysis["pro"]
            loser_analysis = analysis["con"]
        elif con_score > pro_score + 5:
            winner = "Con Position"
            winner_analysis = analysis["con"]
            loser_analysis = analysis["pro"]
        else:
            winner = "Draw/No Clear Winner"
            winner_analysis = analysis["pro"]
            loser_analysis = analysis["con"]
        
        # Generate verdict
        verdict_prompt = f"""
Based on this debate analysis, generate a comprehensive final verdict:

Topic: {analysis['topic']}
Style: {analysis['style']}

Pro Position Score: {pro_score}/100
Con Position Score: {con_score}/100
Winner: {winner}

Pro Analysis:
{json.dumps(analysis['pro'], indent=2)}

Con Analysis:
{json.dumps(analysis['con'], indent=2)}

Generate a final verdict that includes:
1. Clear winner announcement
2. Detailed scoring breakdown
3. Key strengths of each side
4. Areas for improvement
5. Overall debate quality assessment
6. Final thoughts on the topic

Be thorough but concise (500-800 words)."""
        
        messages_for_llm = [
            {"role": "system", "content": "You are a debate judge delivering final verdict. Be authoritative, fair, and insightful."},
            {"role": "user", "content": verdict_prompt}
        ]
        
        try:
            verdict = await self.call_llm(messages_for_llm, temperature=0.3)
            return verdict
        except Exception as e:
            print(f"Error generating verdict: {e}")
            return f"""
# Final Verdict

**Winner: {winner}**

**Final Scores:**
- Pro Position: {pro_score}/100
- Con Position: {con_score}/100

**Summary:**
This debate featured strong arguments from both sides. The {winner.lower()} demonstrated superior argumentation and evidence support.

**Key Observations:**
- Total messages exchanged: {analysis['total_messages']}
- Debate style: {analysis['style']}
- Topic: {analysis['topic']}

Both sides presented compelling arguments, making this a thought-provoking discussion.
"""

    async def deliver_final_judgment(self, debate_id: int, topic: str, style: str) -> str:
        """Deliver final judgment for completed debate"""
        context = {
            'debate_id': debate_id,
            'topic': topic,
            'style': style,
            'action': 'final_judgment'
        }
        
        return await self.process_message("", context)

    async def provide_interim_feedback(self, debate_id: int, round_number: int) -> str:
        """Provide interim feedback during debate"""
        context = {
            'debate_id': debate_id,
            'current_round': round_number,
            'action': 'interim_feedback'
        }
        
        # Get recent messages for feedback
        recent_messages, _ = await self.message_service.get_debate_messages(
            debate_id=debate_id,
            user_id=None,
            skip=0,
            limit=10
        )
        
        if not recent_messages:
            return "Debate is just beginning. Awaiting more arguments for feedback."
        
        feedback_prompt = f"""
Provide brief interim feedback on Round {round_number} of this debate:

Recent messages:
{[msg.content for msg in recent_messages[-5:]]}

Focus on:
1. Argument quality so far
2. Evidence strength
3. Areas needing improvement
4. Suggestions for next round

Keep it concise and constructive (200-300 words)."""
        
        messages_for_llm = [
            {"role": "system", "content": "You are a debate judge providing interim feedback. Be constructive and helpful."},
            {"role": "user", "content": feedback_prompt}
        ]
        
        try:
            feedback = await self.call_llm(messages_for_llm, temperature=0.4)
            return feedback
        except Exception as e:
            print(f"Error generating feedback: {e}")
            return f"Round {round_number} is progressing well. Continue with strong arguments and evidence."
