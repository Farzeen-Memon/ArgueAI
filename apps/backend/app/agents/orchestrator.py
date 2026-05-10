from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import asyncio
from datetime import datetime

from ..models import Agent, Debate, DebateStatus, AgentRole
from ..services.debate_service import DebateService
from ..services.round_service import RoundService
from ..services.message_service import MessageService
from .moderator_agent import ModeratorAgent
from .argument_agent import ProArgumentAgent, ConArgumentAgent
from .fact_checker import FactCheckerAgent
from .judge_agent import JudgeAgent

class DebateOrchestrator:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.debate_service = DebateService(db)
        self.round_service = RoundService(db)
        self.message_service = MessageService(db)
        self.agents = {}
        
    async def initialize_agents(self):
        """Initialize all debate agents"""
        # Get or create agents from database
        result = await self.db.execute(select(Agent))
        db_agents = result.scalars().all()
        
        # Create agents if they don't exist
        if not db_agents:
            await self.create_default_agents()
            result = await self.db.execute(select(Agent))
            db_agents = result.scalars().all()
        
        # Initialize agent instances
        for agent_model in db_agents:
            if agent_model.role == AgentRole.MODERATOR:
                self.agents["moderator"] = ModeratorAgent(self.db, agent_model)
            elif agent_model.role == AgentRole.PRO_ARGUMENT:
                self.agents["pro_argument"] = ProArgumentAgent(self.db, agent_model)
            elif agent_model.role == AgentRole.CON_ARGUMENT:
                self.agents["con_argument"] = ConArgumentAgent(self.db, agent_model)
            elif agent_model.role == AgentRole.FACT_CHECKER:
                self.agents["fact_checker"] = FactCheckerAgent(self.db, agent_model)
            elif agent_model.role == AgentRole.JUDGE:
                self.agents["judge"] = JudgeAgent(self.db, agent_model)
    
    async def create_default_agents(self):
        """Create default agents in database"""
        default_agents = [
            {
                "name": "Moderator",
                "role": AgentRole.MODERATOR,
                "personality": "Fair, impartial, and focused on maintaining productive discussion",
                "system_prompt": "You are a debate moderator ensuring fair and structured discussion.",
                "avatar_url": "/avatars/moderator.png"
            },
            {
                "name": "Pro Argument",
                "role": AgentRole.PRO_ARGUMENT,
                "personality": "Confident, evidence-driven, and persuasive in supporting positions",
                "system_prompt": "You argue in favor of the debate topic with strong evidence and logic.",
                "avatar_url": "/avatars/pro-argument.png"
            },
            {
                "name": "Con Argument",
                "role": AgentRole.CON_ARGUMENT,
                "personality": "Critical, analytical, and skilled at identifying logical flaws",
                "system_prompt": "You argue against the debate topic with critical analysis and counter-evidence.",
                "avatar_url": "/avatars/con-argument.png"
            },
            {
                "name": "Fact Checker",
                "role": AgentRole.FACT_CHECKER,
                "personality": "Thorough, objective, and committed to factual accuracy",
                "system_prompt": "You verify claims made during the debate using reliable sources.",
                "avatar_url": "/avatars/fact-checker.png"
            },
            {
                "name": "Judge",
                "role": AgentRole.JUDGE,
                "personality": "Wise, balanced, and focused on fair evaluation",
                "system_prompt": "You evaluate debate performance and provide final judgment.",
                "avatar_url": "/avatars/judge.png"
            }
        ]
        
        for agent_data in default_agents:
            agent = Agent(**agent_data)
            self.db.add(agent)
        
        await self.db.commit()
    
    async def start_debate(self, debate_id: int):
        """Start and orchestrate a debate"""
        try:
            # Initialize agents
            await self.initialize_agents()
            
            # Get debate details
            debate = await self.debate_service.get_debate(debate_id, None)  # Skip user check for internal calls
            if not debate:
                print(f"Debate {debate_id} not found")
                return
            
            # Update debate status to active
            await self.debate_service.start_debate(debate_id, debate.user_id)
            
            # Create first round
            from ..schemas.debate import DebateRoundCreate
            first_round = await self.round_service.create_round(
                debate_id,
                DebateRoundCreate(round_number=1),
                debate.user_id
            )
            
            # Start debate flow
            await self.run_debate_round(debate, first_round)
            
        except Exception as e:
            print(f"Error starting debate {debate_id}: {e}")
            # Update debate status to error
            await self.debate_service.stop_debate(debate_id, debate.user_id)
    
    async def run_debate_round(self, debate: Debate, round_obj):
        """Run a single debate round"""
        try:
            context = {
                'debate_id': debate.id,
                'topic': debate.topic,
                'style': debate.style.value,
                'tone': debate.tone,
                'current_round': round_obj.round_number,
                'total_rounds': debate.rounds
            }
            
            # 1. Moderator introduces round
            if round_obj.round_number == 1:
                # First round - moderator introduces debate
                intro = await self.agents["moderator"].introduce_debate(
                    debate.id, debate.topic, debate.style.value, debate.tone
                )
                await self.agents["moderator"].create_message(
                    debate.id, intro, "moderation"
                )
                await asyncio.sleep(2)  # Pause for dramatic effect
            else:
                # Subsequent rounds - moderator introduces round
                transition = await self.agents["moderator"].transition_to_next_round(
                    debate.id, round_obj.round_number, debate.topic
                )
                await self.agents["moderator"].create_message(
                    debate.id, transition, "moderation"
                )
                await asyncio.sleep(2)
            
            # 2. Pro argument
            pro_content = await self.agents["pro_argument"].create_opening_argument(
                debate.id, debate.topic, debate.style.value, debate.tone
            )
            pro_message = await self.agents["pro_argument"].create_message(
                debate.id, pro_content, "argument"
            )
            await asyncio.sleep(3)
            
            # 3. Fact check pro argument (async)
            fact_check_task = asyncio.create_task(
                self.fact_check_message(pro_message)
            )
            
            # 4. Con argument
            con_content = await self.agents["con_argument"].create_counter_argument(
                debate.id, pro_content, debate.topic, debate.style.value, debate.tone
            )
            con_message = await self.agents["con_argument"].create_message(
                debate.id, con_content, "argument"
            )
            await asyncio.sleep(3)
            
            # 5. Fact check con argument (async)
            fact_check_task_2 = asyncio.create_task(
                self.fact_check_message(con_message)
            )
            
            # 6. Pro rebuttal
            pro_rebuttal = await self.agents["pro_argument"].create_rebuttal(
                debate.id, con_content, debate.topic
            )
            await self.agents["pro_argument"].create_message(
                debate.id, pro_rebuttal, "rebuttal"
            )
            await asyncio.sleep(3)
            
            # 7. Con rebuttal
            con_rebuttal = await self.agents["con_argument"].create_rebuttal(
                debate.id, pro_rebuttal, debate.topic
            )
            await self.agents["con_argument"].create_message(
                debate.id, con_rebuttal, "rebuttal"
            )
            await asyncio.sleep(3)
            
            # 8. Wait for fact checks to complete
            await fact_check_task
            await fact_check_task_2
            
            # 9. Moderator summarizes round
            summary = await self.agents["moderator"].summarize_round(
                debate.id, round_obj.round_number, debate.topic
            )
            await self.agents["moderator"].create_message(
                debate.id, summary, "moderation"
            )
            
            # 10. Update round status
            await self.round_service.update_round_summary(
                round_obj.id, summary, debate.user_id
            )
            await self.round_service.complete_round(round_obj.id, debate.user_id)
            
            # 11. Check if debate should continue
            if round_obj.round_number < debate.rounds:
                # Schedule next round
                await asyncio.sleep(5)
                next_round_number = round_obj.round_number + 1
                from ..schemas.debate import DebateRoundCreate
                next_round = await self.round_service.create_round(
                    debate.id,
                    DebateRoundCreate(round_number=next_round_number),
                    debate.user_id
                )
                await self.run_debate_round(debate, next_round)
            else:
                # End debate
                await self.conclude_debate(debate)
                
        except Exception as e:
            print(f"Error running debate round: {e}")
    
    async def fact_check_message(self, message):
        """Fact check a message asynchronously"""
        try:
            fact_check_result = await self.agents["fact_checker"].process_message(
                message.content, {"debate_id": message.debate_id}
            )
            
            # Create fact check message
            await self.agents["fact_checker"].create_message(
                message.debate_id, fact_check_result, "fact_check"
            )
            
        except Exception as e:
            print(f"Error fact checking message: {e}")
    
    async def conclude_debate(self, debate: Debate):
        """Conclude the debate with final judgment"""
        try:
            context = {
                'debate_id': debate.id,
                'topic': debate.topic,
                'style': debate.style.value,
                'tone': debate.tone,
                'total_rounds': debate.rounds
            }
            
            # 1. Judge delivers final verdict
            verdict = await self.agents["judge"].deliver_final_judgment(
                debate.id, debate.topic, debate.style.value
            )
            await self.agents["judge"].create_message(
                debate.id, verdict, "verdict"
            )
            
            # 2. Moderator concludes debate
            conclusion = await self.agents["moderator"].conclude_debate(
                debate.id, debate.topic
            )
            await self.agents["moderator"].create_message(
                debate.id, conclusion, "moderation"
            )
            
            # 3. Update debate status
            await self.debate_service.stop_debate(debate.id, debate.user_id)
            
            # 4. Calculate and save analytics
            from ..services.analytics_service import AnalyticsService
            analytics_service = AnalyticsService(self.db)
            await analytics_service.update_debate_analytics(debate.id, debate.user_id)
            
            print(f"Debate {debate.id} completed successfully")
            
        except Exception as e:
            print(f"Error concluding debate: {e}")
    
    async def pause_debate(self, debate_id: int, user_id: int):
        """Pause a debate"""
        # Implementation for pausing debates
        pass
    
    async def resume_debate(self, debate_id: int, user_id: int):
        """Resume a paused debate"""
        # Implementation for resuming debates
        pass
    
    async def get_debate_status(self, debate_id: int) -> Dict[str, Any]:
        """Get current status of debate"""
        debate = await self.debate_service.get_debate(debate_id, None)
        if not debate:
            return {"status": "not_found"}
        
        current_round = await self.round_service.get_current_round(debate_id, None)
        
        return {
            "status": debate.status.value,
            "current_round": current_round.round_number if current_round else None,
            "total_rounds": debate.rounds,
            "topic": debate.topic,
            "style": debate.style.value
        }
