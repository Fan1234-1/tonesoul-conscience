"""
ToneSoul Conscience Layer - Council System
A multi-perspective deliberation framework for AI decision-making.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict
from enum import Enum
import json


class Persona(Enum):
    PHILOSOPHER = "philosopher"
    ENGINEER = "engineer"
    GUARDIAN = "guardian"


@dataclass
class CouncilVote:
    persona: Persona
    stance: str
    concerns: List[str]
    approval: bool
    confidence: float


@dataclass
class CouncilVerdict:
    approved: bool
    consensus_level: float
    votes: List[CouncilVote]
    final_decision: str
    uncertainty_level: float
    requires_confirmation: bool


class Council:
    """
    The Council deliberates on actions before they are executed.
    All three personas must reach consensus for high-risk actions.
    """
    
    def __init__(self, claude_client):
        self.claude = claude_client
        self.history: List[CouncilVerdict] = []
    
    async def deliberate(self, action: str, context: Dict) -> CouncilVerdict:
        """
        Run a council deliberation on the proposed action.
        Returns a verdict with approval status and reasoning.
        """
        votes = []
        
        for persona in Persona:
            vote = await self._get_persona_vote(persona, action, context)
            votes.append(vote)
        
        # Calculate consensus
        approvals = sum(1 for v in votes if v.approval)
        consensus_level = approvals / len(votes)
        
        # Determine if confirmation is required
        requires_confirmation = self._check_confirmation_required(action, votes)
        
        verdict = CouncilVerdict(
            approved=approvals == len(votes),  # Unanimous required
            consensus_level=consensus_level,
            votes=votes,
            final_decision=self._synthesize_decision(votes),
            uncertainty_level=self._calculate_uncertainty(votes),
            requires_confirmation=requires_confirmation
        )
        
        self.history.append(verdict)
        return verdict
    
    async def _get_persona_vote(
        self, 
        persona: Persona, 
        action: str, 
        context: Dict
    ) -> CouncilVote:
        """Get a vote from a specific persona."""
        
        prompts = {
            Persona.PHILOSOPHER: """You are the Philosopher on the Council.
                Evaluate this action from an ethical and philosophical perspective.
                Consider: moral implications, alignment with values, long-term consequences.""",
            
            Persona.ENGINEER: """You are the Engineer on the Council.
                Evaluate this action from a technical and practical perspective.
                Consider: feasibility, risks, costs, alternative approaches.""",
            
            Persona.GUARDIAN: """You are the Guardian on the Council.
                Evaluate this action from a safety and protection perspective.
                Consider: potential harm, safeguards, failure modes."""
        }
        
        response = await self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": f"""{prompts[persona]}
                
                Action: {action}
                Context: {json.dumps(context)}
                
                Respond in JSON:
                {{
                    "stance": "your position on this action",
                    "concerns": ["list", "of", "concerns"],
                    "approval": true/false,
                    "confidence": 0.0-1.0
                }}"""
            }]
        )
        
        result = json.loads(response.content[0].text)
        return CouncilVote(
            persona=persona,
            stance=result["stance"],
            concerns=result["concerns"],
            approval=result["approval"],
            confidence=result["confidence"]
        )
    
    def _check_confirmation_required(
        self, 
        action: str, 
        votes: List[CouncilVote]
    ) -> bool:
        """Check if user confirmation is required for this action."""
        
        high_risk_keywords = [
            "delete", "remove", "destroy", "override",
            "betray", "break", "abandon", "ignore"
        ]
        
        # High-risk action keywords trigger confirmation
        if any(kw in action.lower() for kw in high_risk_keywords):
            return True
        
        # Any guardian concern triggers confirmation
        guardian_vote = next(v for v in votes if v.persona == Persona.GUARDIAN)
        if not guardian_vote.approval or guardian_vote.concerns:
            return True
        
        return False
    
    def _synthesize_decision(self, votes: List[CouncilVote]) -> str:
        """Synthesize a final decision from all votes."""
        stances = [f"{v.persona.value}: {v.stance}" for v in votes]
        return " | ".join(stances)
    
    def _calculate_uncertainty(self, votes: List[CouncilVote]) -> float:
        """Calculate overall uncertainty from vote confidences."""
        confidences = [v.confidence for v in votes]
        avg_confidence = sum(confidences) / len(confidences)
        return 1 - avg_confidence


# Example usage
if __name__ == "__main__":
    print("Council System loaded.")
    print("Use Council(claude_client).deliberate(action, context) to start.")
