"""
Weighted Consensus Algorithm

Expert-weighted voting for domain-specific decision-making.
Assigns higher voting weights to expert agents in their respective domains.

Use Cases:
- Architecture decisions: Higher weight for expert-backend, expert-database
- Security decisions: Higher weight for expert-security
- UI decisions: Higher weight for expert-frontend, expert-uiux
- Quality decisions: Higher weight for manager-quality, manager-tdd
"""

from typing import Any, Dict, List, Optional
from .base import ConsensusAlgorithm, ConsensusResult


# Expert agent weight presets (default: all agents = 1.0)
EXPERT_WEIGHT_PRESET = {
    # Expert agents (2.0x weight)
    "expert-backend": 2.0,
    "expert-frontend": 2.0,
    "expert-database": 2.0,
    "expert-devops": 2.0,
    "expert-security": 2.0,
    "expert-uiux": 2.0,
    "expert-debug": 2.0,

    # Manager agents (1.5x weight for quality/workflow)
    "manager-tdd": 1.5,
    "manager-quality": 1.5,
    "manager-strategy": 1.5,

    # Regular agents (1.0x weight - default)
    # All other agents automatically get 1.0
}


def create_domain_weights(domain: str, agents: List[str]) -> Dict[str, float]:
    """
    Create domain-specific weight configuration.

    Assigns higher weights to domain experts for domain-specific proposals.

    Args:
        domain: Domain identifier (e.g., "backend", "frontend", "security")
        agents: List of agent IDs participating in consensus

    Returns:
        Dict mapping agent_id to weight (1.0 for non-experts)

    Example:
        >>> weights = create_domain_weights("security", ["expert-security", "expert-backend", "manager-tdd"])
        >>> print(weights)
        {"expert-security": 3.0, "expert-backend": 1.5, "manager-tdd": 1.0}
    """
    domain_experts = {
        "backend": ["expert-backend", "expert-database"],
        "frontend": ["expert-frontend", "expert-uiux"],
        "security": ["expert-security"],
        "database": ["expert-database"],
        "devops": ["expert-devops"],
        "quality": ["manager-quality", "manager-tdd"],
    }

    weights = {}
    domain_key = domain.lower()
    experts = domain_experts.get(domain_key, [])

    for agent_id in agents:
        if agent_id in experts:
            # Primary domain expert gets 3.0x weight
            weights[agent_id] = 3.0
        elif agent_id.startswith("expert-"):
            # Other experts get 1.5x weight
            weights[agent_id] = 1.5
        else:
            # Regular agents get 1.0 weight
            weights[agent_id] = 1.0

    return weights


class WeightedConsensus(ConsensusAlgorithm):
    """
    Weighted voting consensus algorithm.

    Implements expert-weighted voting where different agents have different
    voting weights based on their expertise. Expert agents receive higher
    weights in their domain, allowing domain knowledge to influence decisions.

    Decision Logic:
        weighted_for = sum(weight for agent, vote in votes if vote == "approve")
        weighted_against = sum(weight for agent, vote in votes if vote == "reject")
        total_weight = weighted_for + weighted_against
        approval_percentage = weighted_for / total_weight
        decision = "approved" if approval_percentage >= 0.5 else "rejected"

    Edge Cases:
        - All agents abstain -> "rejected" (conservative default)
        - Agent not in weight map -> default weight (1.0)
        - Equal weighted votes -> "rejected" (conservative default)
        - Timeout -> "timeout"

    Example:
        >>> coordinator = SwarmCoordinator()
        >>> weights = {"expert-backend": 2.0, "expert-frontend": 2.0, "manager-tdd": 1.5}
        >>> consensus = WeightedConsensus(coordinator, agent_weights=weights)
        >>> result = consensus.propose({"action": "deploy", "env": "production"})
        >>> print(result.decision)  # "approved" or "rejected"
    """

    def __init__(
        self,
        coordinator: Any,  # ICoordinator - using Any to avoid circular import
        agent_weights: Optional[Dict[str, float]] = None
    ):
        """
        Initialize weighted consensus algorithm.

        Args:
            coordinator: Coordinator reference for agent communication
            agent_weights: Dict mapping agent_id to weight (default: all agents weight=1.0)
        """
        self._coordinator = coordinator
        self._agent_weights = agent_weights or {}
        self._default_weight = 1.0
        self._last_proposal = None
        self._last_result = None

    def set_agent_weight(self, agent_id: str, weight: float) -> None:
        """
        Set voting weight for specific agent.

        Expert agents should receive higher weights (e.g., 2.0 or 3.0).
        Regular agents typically have weight 1.0.

        Args:
            agent_id: Unique agent identifier
            weight: Voting weight (must be > 0)

        Raises:
            ValueError: If weight is not positive

        Example:
            >>> consensus.set_agent_weight("expert-backend", 2.0)
            >>> consensus.set_agent_weight("manager-quality", 1.5)
        """
        if weight <= 0:
            raise ValueError(f"Weight must be positive, got {weight}")
        self._agent_weights[agent_id] = weight

    def get_agent_weight(self, agent_id: str) -> float:
        """
        Get agent's voting weight.

        Returns default weight (1.0) if agent not in weight map.

        Args:
            agent_id: Unique agent identifier

        Returns:
            Agent's voting weight (default: 1.0)
        """
        return self._agent_weights.get(agent_id, self._default_weight)

    def propose(
        self,
        proposal: Dict[str, Any],
        timeout_ms: int = 30000
    ) -> ConsensusResult:
        """
        Propose and collect weighted votes.

        Collects votes from all registered agents and calculates weighted
        consensus based on agent expertise weights.

        Args:
            proposal: Proposal data (must be JSON-serializable)
            timeout_ms: Timeout in milliseconds (not implemented yet)

        Returns:
            ConsensusResult with weighted decision

        Vote Types:
            - "approve": Vote in favor
            - "reject": Vote against
            - "abstain": No vote (excluded from calculation)

        Example:
            >>> proposal = {"action": "implement_feature", "spec": "SPEC-001"}
            >>> result = consensus.propose(proposal, timeout_ms=30000)
            >>> if result.decision == "approved":
            ...     print(f"Approved with {result.votes_for} weighted votes")
        """
        self._last_proposal = proposal

        # Get all registered agents from coordinator
        topology_info = self._coordinator.get_topology_info()
        agent_count = topology_info.get("agent_count", 0)

        if agent_count == 0:
            # No agents available
            return ConsensusResult(
                decision="rejected",
                votes_for=0,
                votes_against=0,
                abstain=0,
                threshold=0.5,
                participants=[],
                vote_details={},
                metadata={"reason": "no_agents_available"}
            )

        # Collect votes from all agents
        votes = self._collect_votes(proposal)

        # Calculate weighted scores
        weighted_for = 0.0
        weighted_against = 0.0
        abstain_count = 0
        vote_details = {}

        for agent_id, vote in votes.items():
            weight = self.get_agent_weight(agent_id)
            vote_details[agent_id] = vote

            if vote == "approve":
                weighted_for += weight
            elif vote == "reject":
                weighted_against += weight
            elif vote == "abstain":
                abstain_count += 1

        # Total weighted votes (excluding abstentions)
        total_weight = weighted_for + weighted_against

        # Determine decision
        if total_weight == 0:
            # All agents abstained -> conservative rejection
            decision = "rejected"
            approval_percentage = 0.0
        else:
            approval_percentage = weighted_for / total_weight
            decision = "approved" if approval_percentage >= 0.5 else "rejected"

        result = ConsensusResult(
            decision=decision,
            votes_for=int(weighted_for),
            votes_against=int(weighted_against),
            abstain=abstain_count,
            threshold=0.5,
            participants=list(votes.keys()),
            vote_details=vote_details,
            metadata={
                "weighted_for": weighted_for,
                "weighted_against": weighted_against,
                "approval_percentage": approval_percentage,
                "total_weight": total_weight,
                "agent_weights": {k: self.get_agent_weight(k) for k in votes.keys()}
            }
        )

        self._last_result = result
        return result

    def _collect_votes(self, proposal: Dict[str, Any]) -> Dict[str, str]:
        """
        Collect votes from all agents.

        This is a placeholder implementation. In production, this would:
        1. Broadcast proposal to all agents via coordinator
        2. Wait for votes (with timeout)
        3. Collect and validate responses

        Args:
            proposal: Proposal to vote on

        Returns:
            Dict mapping agent_id to vote ("approve", "reject", "abstain")
        """
        # TODO: Implement actual vote collection via coordinator
        # For now, return empty dict (to be implemented with agent communication)
        return {}

    def get_state(self) -> Dict[str, Any]:
        """
        Get current algorithm state.

        Returns:
            Dict with algorithm state including weights and last result
        """
        return {
            "algorithm": "weighted_consensus",
            "default_weight": self._default_weight,
            "agent_weights": dict(self._agent_weights),
            "last_proposal": self._last_proposal,
            "last_result": {
                "decision": self._last_result.decision,
                "votes_for": self._last_result.votes_for,
                "votes_against": self._last_result.votes_against,
                "metadata": self._last_result.metadata
            } if self._last_result else None
        }

    def reset(self) -> bool:
        """
        Reset algorithm to initial state.

        Clears last proposal and result, but preserves weight configuration.

        Returns:
            True (always succeeds)
        """
        self._last_proposal = None
        self._last_result = None
        return True
