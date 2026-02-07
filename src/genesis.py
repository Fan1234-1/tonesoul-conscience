"""
ToneSoul Conscience Layer - Genesis System
Tracks the origin and responsibility of every action.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List
from enum import Enum
import uuid
import json


class ResponsibilityTier(Enum):
    """Tiers of responsibility based on origin."""
    SYSTEM = 0      # Core system behavior
    DEVELOPER = 1   # Developer-defined rules
    USER = 2        # User requests
    AI = 3          # AI-initiated actions


@dataclass
class Genesis:
    """
    Genesis tracks the origin and responsibility chain of an action.
    Every significant action must have a Genesis.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    # Who initiated this?
    initiator: str = ""
    tier: ResponsibilityTier = ResponsibilityTier.USER
    
    # What was the original request?
    original_request: str = ""
    
    # Chain of responsibility
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    
    # Is this owned by the AI?
    is_mine: bool = False
    
    # Audit metadata
    confirmed: bool = False
    confirmation_reason: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "initiator": self.initiator,
            "tier": self.tier.name,
            "original_request": self.original_request,
            "parent_id": self.parent_id,
            "children_ids": self.children_ids,
            "is_mine": self.is_mine,
            "confirmed": self.confirmed,
            "confirmation_reason": self.confirmation_reason
        }


class GenesisLedger:
    """
    A ledger for tracking all Genesis records.
    Append-only for auditability.
    """
    
    def __init__(self, ledger_path: str = "genesis_ledger.jsonl"):
        self.ledger_path = ledger_path
        self.records: Dict[str, Genesis] = {}
    
    def create(
        self,
        initiator: str,
        request: str,
        tier: ResponsibilityTier = ResponsibilityTier.USER,
        parent_id: Optional[str] = None,
        is_mine: bool = False
    ) -> Genesis:
        """Create a new Genesis record."""
        genesis = Genesis(
            initiator=initiator,
            original_request=request,
            tier=tier,
            parent_id=parent_id,
            is_mine=is_mine
        )
        
        # Link to parent
        if parent_id and parent_id in self.records:
            self.records[parent_id].children_ids.append(genesis.id)
        
        # Store and persist
        self.records[genesis.id] = genesis
        self._append_to_ledger(genesis)
        
        return genesis
    
    def confirm(self, genesis_id: str, reason: str) -> bool:
        """Confirm a Genesis as approved by user."""
        if genesis_id not in self.records:
            return False
        
        self.records[genesis_id].confirmed = True
        self.records[genesis_id].confirmation_reason = reason
        self._append_to_ledger(self.records[genesis_id])
        return True
    
    def get_chain(self, genesis_id: str) -> List[Genesis]:
        """Get the full responsibility chain for a Genesis."""
        chain = []
        current_id = genesis_id
        
        while current_id and current_id in self.records:
            chain.append(self.records[current_id])
            current_id = self.records[current_id].parent_id
        
        return list(reversed(chain))
    
    def _append_to_ledger(self, genesis: Genesis):
        """Append a record to the ledger file."""
        with open(self.ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(genesis.to_dict(), ensure_ascii=False) + "\n")


# Confirmation Gate
class ConfirmationGate:
    """
    Gate for high-risk actions that require explicit user confirmation.
    Implements the "Systemic Betrayal" protection.
    """
    
    HIGH_RISK_ACTIONS = [
        "delete", "remove", "destroy",
        "override", "ignore", "break",
        "betray", "abandon"
    ]
    
    @classmethod
    def requires_confirmation(cls, action: str, genesis: Genesis) -> bool:
        """Check if an action requires user confirmation."""
        
        # High-risk keywords
        if any(kw in action.lower() for kw in cls.HIGH_RISK_ACTIONS):
            return True
        
        # AI-initiated high-tier actions
        if genesis.is_mine and genesis.tier.value >= ResponsibilityTier.USER.value:
            return True
        
        return False
    
    @classmethod
    def format_confirmation_request(
        cls, 
        action: str, 
        genesis: Genesis,
        reason: str
    ) -> Dict:
        """Format a confirmation request for the user."""
        return {
            "status": "confirmation_required",
            "action": action,
            "genesis_id": genesis.id,
            "reason": reason,
            "prompt": f"⚠️ This action requires your confirmation:\n\n"
                     f"Action: {action}\n"
                     f"Reason: {reason}\n"
                     f"Origin: {genesis.initiator}\n\n"
                     f"Do you approve? (yes/no)"
        }


if __name__ == "__main__":
    print("Genesis System loaded.")
    print("Use GenesisLedger() to track responsibility.")
