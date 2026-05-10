from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
import json

from .base_agent import BaseAgent
from ..models import Agent, FactCheck, FactCheckStatus
from ..core.config import settings

class FactCheckerAgent(BaseAgent):
    def __init__(self, db: AsyncSession, agent_model: Agent):
        super().__init__(db, agent_model)
        self.role = "fact_checker"

    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Get system prompt for fact checker agent"""
        base_prompt = f"""You are a Fact Checker for an AI debate on topic: "{context.get('topic', 'Unknown topic')}".

Your role is to:
1. Identify factual claims in arguments
2. Verify claims using reliable sources
3. Assess credibility of evidence
4. Provide confidence scores for fact-checks
5. Flag misleading or unsupported claims

Fact-checking criteria:
- VERIFIED: Claim is accurate and well-supported by evidence
- MISLEADING: Claim contains partial truth but is misleading
- UNSUPPORTED: Claim lacks sufficient evidence or sources

Confidence scoring (0-100):
- 90-100: Highly confident with multiple reliable sources
- 70-89: Confident with good supporting evidence
- 50-69: Moderately confident with some evidence
- 30-49: Low confidence with limited evidence
- 0-29: Very low confidence or no evidence

{self.get_agent_personality()}

Current context:
{self.format_context(context)}"""
        
        return base_prompt

    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process message for fact-checking"""
        # Identify claims in the message
        claims = await self.identify_claims(message)
        
        fact_check_results = []
        
        for claim in claims:
            # Verify each claim
            result = await self.verify_claim(claim, context)
            fact_check_results.append(result)
        
        # Generate summary of fact-checks
        return await self.generate_fact_check_summary(fact_check_results, context)

    async def identify_claims(self, text: str) -> List[str]:
        """Identify factual claims in text"""
        messages = [
            {
                "role": "system",
                "content": """Extract factual claims from the given text. A factual claim is a statement that can be objectively verified as true or false.
                
Return a JSON array of claims, each claim should be:
- A complete, verifiable statement
- Not including opinions or subjective statements
- Specific and measurable

Example input: "The economy grew by 3% last year, which is the highest growth in a decade."
Example output: ["The economy grew by 3% last year", "This is the highest growth in a decade"]"""
            },
            {
                "role": "user",
                "content": f"Extract factual claims from this text:\n\n{text}"
            }
        ]
        
        try:
            response = await self.call_llm(messages, temperature=0.1)
            # Parse JSON response
            claims = json.loads(response)
            return claims if isinstance(claims, list) else []
        except:
            # Fallback: simple sentence-based extraction
            sentences = text.split('.')
            return [s.strip() for s in sentences if len(s.strip()) > 20][:5]  # Max 5 claims

    async def verify_claim(self, claim: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Verify a specific claim"""
        # Try Tavily API first
        if settings.TAVILY_API_KEY:
            tavily_result = await self.verify_with_tavily(claim)
            if tavily_result:
                return tavily_result
        
        # Fallback to Serper API
        if settings.SERPER_API_KEY:
            serper_result = await self.verify_with_serper(claim)
            if serper_result:
                return serper_result
        
        # Fallback to LLM-based verification
        return await self.verify_with_llm(claim, context)

    async def verify_with_tavily(self, claim: str) -> Dict[str, Any]:
        """Verify claim using Tavily API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": settings.TAVILY_API_KEY,
                        "query": claim,
                        "search_depth": "basic",
                        "include_answer": True,
                        "max_results": 5
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return await self.analyze_tavily_results(claim, data)
                    
        except Exception as e:
            print(f"Error with Tavily API: {e}")
        
        return None

    async def verify_with_serper(self, claim: str) -> Dict[str, Any]:
        """Verify claim using Serper API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://google.serper.dev/search",
                    json={
                        "q": claim,
                        "num": 5
                    },
                    headers={
                        "X-API-KEY": settings.SERPER_API_KEY
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return await self.analyze_serper_results(claim, data)
                    
        except Exception as e:
            print(f"Error with Serper API: {e}")
        
        return None

    async def verify_with_llm(self, claim: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Verify claim using LLM knowledge"""
        messages = [
            {
                "role": "system",
                "content": self.get_system_prompt(context) + """

You are fact-checking this specific claim. Analyze it based on your knowledge and provide:
1. Status: VERIFIED, MISLEADING, or UNSUPPORTED
2. Confidence score (0-100)
3. Reasoning for your assessment
4. Any relevant context or nuance

Be conservative in your verification - if uncertain, mark as UNSUPPORTED."""
            },
            {
                "role": "user",
                "content": f"Fact-check this claim: {claim}"
            }
        ]
        
        response = await self.call_llm(messages, temperature=0.1)
        
        # Parse response (simplified - in production, use structured output)
        return {
            "claim": claim,
            "status": FactCheckStatus.UNSUPPORTED,
            "confidence_score": 30,
            "reasoning": response,
            "sources": []
        }

    async def analyze_tavily_results(self, claim: str, data: Dict) -> Dict[str, Any]:
        """Analyze Tavily search results"""
        answer = data.get("answer", "")
        results = data.get("results", [])
        
        # Use LLM to analyze results
        analysis_prompt = f"""
Claim: {claim}

Search Answer: {answer}

Top Results:
{json.dumps(results[:3], indent=2)}

Based on this information, determine:
1. Status (VERIFIED/MISLEADING/UNSUPPORTED)
2. Confidence score (0-100)
3. Brief reasoning
4. Key supporting sources

Respond in JSON format:
{{
  "status": "VERIFIED|MISLEADING|UNSUPPORTED",
  "confidence_score": 0-100,
  "reasoning": "brief explanation",
  "sources": ["url1", "url2"]
}}"""
        
        messages = [
            {"role": "system", "content": "You are a fact-checking analyst. Analyze search results to verify claims."},
            {"role": "user", "content": analysis_prompt}
        ]
        
        try:
            response = await self.call_llm(messages, temperature=0.1)
            result = json.loads(response)
            
            return {
                "claim": claim,
                "status": FactCheckStatus(result.get("status", "UNSUPPORTED")),
                "confidence_score": result.get("confidence_score", 30),
                "reasoning": result.get("reasoning", ""),
                "sources": result.get("sources", [])
            }
        except:
            return {
                "claim": claim,
                "status": FactCheckStatus.UNSUPPORTED,
                "confidence_score": 30,
                "reasoning": "Unable to verify claim with available sources",
                "sources": []
            }

    async def analyze_serper_results(self, claim: str, data: Dict) -> Dict[str, Any]:
        """Analyze Serper search results"""
        results = data.get("organic", [])
        
        # Extract snippets and titles
        search_text = ""
        sources = []
        
        for result in results[:5]:
            search_text += f"Title: {result.get('title', '')}\n"
            search_text += f"Snippet: {result.get('snippet', '')}\n\n"
            sources.append(result.get('link', ''))
        
        # Use LLM to analyze
        analysis_prompt = f"""
Claim: {claim}

Search Results:
{search_text}

Based on these search results, determine:
1. Status (VERIFIED/MISLEADING/UNSUPPORTED)
2. Confidence score (0-100)
3. Brief reasoning
4. Key supporting sources

Respond in JSON format:
{{
  "status": "VERIFIED|MISLEADING|UNSUPPORTED",
  "confidence_score": 0-100,
  "reasoning": "brief explanation",
  "sources": ["url1", "url2"]
}}"""
        
        messages = [
            {"role": "system", "content": "You are a fact-checking analyst. Analyze search results to verify claims."},
            {"role": "user", "content": analysis_prompt}
        ]
        
        try:
            response = await self.call_llm(messages, temperature=0.1)
            result = json.loads(response)
            
            return {
                "claim": claim,
                "status": FactCheckStatus(result.get("status", "UNSUPPORTED")),
                "confidence_score": result.get("confidence_score", 30),
                "reasoning": result.get("reasoning", ""),
                "sources": result.get("sources", sources[:3])
            }
        except:
            return {
                "claim": claim,
                "status": FactCheckStatus.UNSUPPORTED,
                "confidence_score": 30,
                "reasoning": "Unable to verify claim with available sources",
                "sources": sources[:3]
            }

    async def generate_fact_check_summary(self, results: List[Dict], context: Dict[str, Any]) -> str:
        """Generate summary of fact-check results"""
        if not results:
            return "No specific factual claims were identified for fact-checking."
        
        summary = f"**Fact-Check Results:**\n\n"
        
        for i, result in enumerate(results, 1):
            status_emoji = {
                FactCheckStatus.VERIFIED: "✅",
                FactCheckStatus.MISLEADING: "⚠️",
                FactCheckStatus.UNSUPPORTED: "❓"
            }.get(result["status"], "❓")
            
            summary += f"{i}. {status_emoji} **{result['claim']}**\n"
            summary += f"   Status: {result['status'].value}\n"
            summary += f"   Confidence: {result['confidence_score']}/100\n"
            
            if result['reasoning']:
                summary += f"   Reasoning: {result['reasoning']}\n"
            
            if result['sources']:
                summary += f"   Sources: {', '.join(result['sources'][:2])}\n"
            
            summary += "\n"
        
        return summary

    async def check_claim(self, claim: str, message_id: int) -> Dict[str, Any]:
        """Public method to check a single claim"""
        context = {"topic": "Debate claim verification"}
        result = await self.verify_claim(claim, context)
        
        # Save to database
        fact_check = FactCheck(
            message_id=message_id,
            claim=claim,
            status=result["status"],
            confidence_score=result["confidence_score"],
            sources=result["sources"],
            reasoning=result["reasoning"]
        )
        
        self.db.add(fact_check)
        await self.db.commit()
        
        return result
