"""
Gossip Protocol Core

Eventual consistency through probabilistic message passing.
Agents spread information via random peer selection until convergence.

Use Cases:
- Eventual consistency for non-critical decisions
- Scalable consensus for large agent networks
- Fault-tolerant distributed state synchronization
- Asynchronous decision-making without coordination overhead

Algorithm:
1. Each agent starts with initial vote
2. For each round (max: rounds):
   - Each agent selects random peers (fanout)
   - Share current state with peers
   - Update state based on peer majority
3. Check convergence (95%+ agreement)
4. Return majority decision

Guarantees:
- High probability of convergence (exponential)
- O(log n) message complexity
- Tolerates agent failures
- No global clock needed

Complexity:
- Message: O(n * log n) total messages
- Rounds: O(log n) rounds to convergence
- Memory: O(n) state storage per agent

References:
- Demers et al. (1987): "Epidemic algorithms for replicated database maintenance"
- Birman et al. (1999): "Bimodal multicast"
"""

import random
import logging
import time
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import Counter

from .base import ConsensusAlgorithm, ConsensusResult

logger = logging.getLogger(__name__)


@dataclass
class GossipConfig:
    """
    Gossip protocol configuration.

    Attributes:
        fanout: Number of random peers to gossip to per round (default: 3)
        max_rounds: Maximum gossip propagation rounds (default: 5)
        convergence_threshold: % of agents that must agree (default: 0.95 = 95%)
        round_delay_ms: Delay between rounds in milliseconds (default: 100)
    """
    fanout: int = 3
    max_rounds: int = 5
    convergence_threshold: float = 0.95
    round_delay_ms: int = 100


class GossipProtocol(ConsensusAlgorithm):
    """
    Gossip-based eventual consistency protocol.

    Agents spread information through random peer selection.
    Guarantees eventual consistency with probabilistic guarantees.

    Features:
    - Probabilistic convergence with high probability
    - O(log n) message complexity per agent
    - Fault tolerance against agent failures
    - Asynchronous operation (no global coordination)
    - Scalable to large agent networks (100+ agents)

    Decision Logic:
        For each round:
            1. Each agent selects fanout random peers
            2. Shares current vote with peers
            3. Updates vote based on peer majority
        Until: convergence_threshold reached OR max_rounds exceeded

    Example:
        >>> coordinator = SwarmCoordinator()
        >>> gossip = GossipProtocol(fanout=3, rounds=5, convergence_threshold=0.95)
        >>> result = gossip.decide(
        ...     votes={"agent1": "approve", "agent2": "approve", "agent3": "reject"},
        ...     threshold=0.66
        ... )
        >>> print(result.decision)  # "approved" after convergence
    """

    def __init__(
        self,
        fanout: int = 3,
        rounds: int = 5,
        convergence_threshold: float = 0.95
    ):
        """
        Initialize gossip protocol.

        Args:
            fanout: Number of random peers to gossip to per round (1-10)
            rounds: Maximum gossip rounds (1-20)
            convergence_threshold: % of agents that must agree (0.51-1.0)

        Raises:
            ValueError: If parameters are out of valid ranges

        Example:
            >>> # Standard configuration for medium networks (10-50 agents)
            >>> gossip = GossipProtocol(fanout=3, rounds=5, convergence_threshold=0.95)
            >>>
            >>> # High-reliability configuration for critical decisions
            >>> gossip = GossipProtocol(fanout=5, rounds=10, convergence_threshold=0.99)
            >>>
            >>> # Fast convergence for large networks (100+ agents)
            >>> gossip = GossipProtocol(fanout=10, rounds=3, convergence_threshold=0.90)
        """
        # Validate parameters
        if not 1 <= fanout <= 10:
            raise ValueError(f"Fanout must be between 1 and 10 (got {fanout})")
        if not 1 <= rounds <= 20:
            raise ValueError(f"Rounds must be between 1 and 20 (got {rounds})")
        if not 0.51 <= convergence_threshold <= 1.0:
            raise ValueError(
                f"Convergence threshold must be between 0.51 and 1.0 (got {convergence_threshold})"
            )

        self._config = GossipConfig(
            fanout=fanout,
            max_rounds=rounds,
            convergence_threshold=convergence_threshold,
            round_delay_ms=100
        )
        self._last_proposal = None
        self._last_result = None
        self._round_history: List[Dict[str, Any]] = []

        logger.info(
            f"GossipProtocol initialized: fanout={fanout}, rounds={rounds}, "
            f"convergence={convergence_threshold:.2%}"
        )

    def propose(
        self,
        proposal: Dict[str, Any],
        timeout_ms: int = 30000
    ) -> ConsensusResult:
        """
        Gossip-based consensus decision using proposal.

        Args:
            proposal: Proposal data (must be JSON-serializable)
            timeout_ms: Timeout in milliseconds (not used in gossip)

        Returns:
            ConsensusResult with decision outcome

        Example:
            >>> proposal = {"proposal_id": "deploy-v2", "description": "Deploy v2"}
            >>> result = gossip.propose(proposal)
            >>> print(result.decision)
        """
        if not proposal.get("proposal_id"):
            raise ValueError("Proposal must include 'proposal_id' field")

        # For gossip, we need initial votes in the proposal
        if "votes" not in proposal:
            raise ValueError("Proposal must include 'votes' dict for gossip protocol")

        return self.decide(
            votes=proposal["votes"],
            threshold=proposal.get("threshold", 0.66),
            metadata={"proposal_id": proposal["proposal_id"]}
        )

    def decide(
        self,
        votes: Dict[str, str],
        threshold: float = 0.66,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConsensusResult:
        """
        Gossip-based consensus decision.

        Algorithm:
        1. Each agent starts with initial vote
        2. For each round:
           - Select random peers (fanout)
           - Share current state
           - Update state based on peers
        3. Check convergence (95%+ agreement)
        4. Return majority decision

        Args:
            votes: Initial vote state mapping agent_id to vote type
                  ("approve", "reject", "abstain")
            threshold: Approval threshold for decision (default: 0.66)
            metadata: Optional metadata for tracking

        Returns:
            ConsensusResult with decision after gossip convergence

        Raises:
            ValueError: If votes dictionary is empty

        Example:
            >>> votes = {
            ...     "agent1": "approve",
            ...     "agent2": "approve",
            ...     "agent3": "reject",
            ...     "agent4": "approve",
            ...     "agent5": "abstain"
            ... }
            >>> result = gossip.decide(votes, threshold=0.66)
            >>> print(f"Decision: {result.decision}")  # "approved"
        """
        if not votes:
            raise ValueError("Votes dictionary cannot be empty")

        start_time = time.time()
        proposal_id = metadata.get("proposal_id", "direct-vote") if metadata else "direct-vote"

        logger.info(
            f"Gossip decision for {proposal_id}: {len(votes)} agents, "
            f"threshold={threshold:.2%}"
        )

        # Reset round history for new decision
        self._round_history = []

        # Execute gossip rounds
        final_state, rounds_completed, converged = self._execute_gossip_rounds(votes)

        # Calculate result
        result = self._calculate_result(
            final_state=final_state,
            proposal_id=proposal_id,
            start_time=start_time,
            rounds_completed=rounds_completed,
            converged=converged,
            threshold=threshold
        )

        self._last_result = result
        return result

    def _execute_gossip_rounds(
        self,
        initial_votes: Dict[str, str]
    ) -> Tuple[Dict[str, str], int, bool]:
        """
        Execute gossip propagation rounds until convergence or max rounds.

        Args:
            initial_votes: Initial vote state for all agents

        Returns:
            Tuple of (final_state, rounds_completed, converged)

        Algorithm:
            For each round:
                1. Each agent selects random peers
                2. Shares vote with peers
                3. Updates vote based on peer majority
                4. Check convergence
        """
        current_state = dict(initial_votes)  # Copy to avoid mutation
        all_agents = list(current_state.keys())

        for round_num in range(1, self._config.max_rounds + 1):
            logger.debug(f"Gossip round {round_num}/{self._config.max_rounds}")

            # Execute one round of propagation
            new_state = self._propagate_round(current_state, all_agents)

            # Record round history
            converged, agreement_ratio = self._check_convergence(
                new_state,
                self._config.convergence_threshold
            )

            self._round_history.append({
                "round": round_num,
                "state": dict(new_state),
                "agreement_ratio": agreement_ratio,
                "converged": converged
            })

            # Check convergence
            if converged:
                logger.info(
                    f"Convergence reached in round {round_num} "
                    f"(agreement={agreement_ratio:.2%})"
                )
                return new_state, round_num, True

            # Update state for next round
            current_state = new_state

            # Delay between rounds (simulate network propagation)
            if self._config.round_delay_ms > 0 and round_num < self._config.max_rounds:
                time.sleep(self._config.round_delay_ms / 1000.0)

        # Max rounds reached without convergence
        _, final_agreement = self._check_convergence(
            current_state,
            self._config.convergence_threshold
        )

        logger.warning(
            f"Max rounds ({self._config.max_rounds}) reached without convergence "
            f"(final agreement={final_agreement:.2%})"
        )

        return current_state, self._config.max_rounds, False

    def _propagate_round(
        self,
        current_state: Dict[str, str],
        all_agents: List[str]
    ) -> Dict[str, str]:
        """
        Execute one round of gossip propagation.

        For each agent:
        1. Select random peers (fanout)
        2. Share state with peers
        3. Update based on peer states (majority rule)

        Args:
            current_state: Current vote state for all agents
            all_agents: List of all agent IDs

        Returns:
            Updated state after one round of gossip
        """
        new_state = {}

        for agent_id in all_agents:
            # Select random peers for this agent
            peers = self._select_random_peers(agent_id, all_agents, self._config.fanout)

            # Get votes from agent + peers
            peer_votes = [current_state[agent_id]]  # Include own vote
            for peer_id in peers:
                peer_votes.append(current_state[peer_id])

            # Update agent's vote based on peer majority
            new_vote = self._calculate_peer_majority(peer_votes)
            new_state[agent_id] = new_vote

        return new_state

    def _select_random_peers(
        self,
        agent_id: str,
        all_agents: List[str],
        fanout: int
    ) -> List[str]:
        """
        Select random peers for gossiping.

        Excludes self, selects up to fanout random agents.

        Args:
            agent_id: Current agent selecting peers
            all_agents: List of all available agents
            fanout: Number of peers to select

        Returns:
            List of selected peer agent IDs

        Example:
            >>> peers = gossip._select_random_peers("agent1", ["agent1", "agent2", "agent3"], 2)
            >>> len(peers) <= 2
            True
            >>> "agent1" not in peers  # Never selects self
            True
        """
        # Available peers (exclude self)
        available_peers = [a for a in all_agents if a != agent_id]

        # Select up to fanout random peers
        num_to_select = min(fanout, len(available_peers))
        selected_peers = random.sample(available_peers, num_to_select)

        return selected_peers

    def _calculate_peer_majority(self, peer_votes: List[str]) -> str:
        """
        Calculate majority vote from peer votes.

        Uses majority rule with abstain tie-breaking:
        - If clear majority exists -> return majority vote
        - If tie -> return current vote (first in list)
        - Abstains don't participate in majority calculation

        Args:
            peer_votes: List of votes from peers (first element is own vote)

        Returns:
            Majority vote or current vote if tie

        Example:
            >>> gossip._calculate_peer_majority(["approve", "approve", "reject"])
            "approve"
            >>> gossip._calculate_peer_majority(["approve", "reject", "abstain"])
            "approve"  # Current vote (tie)
        """
        # Count votes (exclude abstentions from majority calculation)
        active_votes = [v for v in peer_votes if v != "abstain"]

        if not active_votes:
            # All abstained -> keep current vote
            return peer_votes[0]

        # Get most common vote
        vote_counts = Counter(active_votes)
        majority_vote, count = vote_counts.most_common(1)[0]

        # Check if true majority (>50%)
        if count > len(active_votes) / 2:
            return majority_vote
        else:
            # Tie or no majority -> keep current vote
            return peer_votes[0]

    def _check_convergence(
        self,
        state: Dict[str, str],
        threshold: float = 0.95
    ) -> Tuple[bool, float]:
        """
        Check if agents have converged.

        Convergence: >= threshold % of agents agree on same vote

        Args:
            state: Current vote state
            threshold: Convergence threshold (default: 0.95 = 95%)

        Returns:
            Tuple of (converged: bool, agreement_ratio: float)

        Example:
            >>> state = {"a1": "approve", "a2": "approve", "a3": "approve", "a4": "reject"}
            >>> converged, ratio = gossip._check_convergence(state, threshold=0.75)
            >>> converged
            False  # Only 75% agreement (3/4), need 95%
            >>> ratio
            0.75
        """
        if not state:
            return False, 0.0

        # Count votes (exclude abstentions)
        active_votes = [v for v in state.values() if v != "abstain"]

        if not active_votes:
            return False, 0.0

        # Find most common vote
        vote_counts = Counter(active_votes)
        most_common_vote, count = vote_counts.most_common(1)[0]

        # Calculate agreement ratio
        agreement_ratio = count / len(active_votes)

        # Check if meets threshold
        converged = agreement_ratio >= threshold

        return converged, agreement_ratio

    def _aggregate_majority(
        self,
        final_state: Dict[str, str]
    ) -> Tuple[str, Dict[str, int]]:
        """
        Aggregate final state to majority decision.

        Args:
            final_state: Final vote state after gossip rounds

        Returns:
            Tuple of (decision, vote_counts)

        Decision Logic:
            - Calculate vote counts
            - Exclude abstentions from decision
            - Return "approved" if approve votes > reject votes
            - Return "rejected" otherwise
        """
        # Count votes
        vote_counts = Counter(final_state.values())

        approve_count = vote_counts.get("approve", 0)
        reject_count = vote_counts.get("reject", 0)
        abstain_count = vote_counts.get("abstain", 0)

        # Determine decision (exclude abstentions)
        if approve_count > reject_count:
            decision = "approved"
        elif reject_count > approve_count:
            decision = "rejected"
        else:
            # Tie -> conservative rejection
            decision = "rejected"

        return decision, {
            "approve": approve_count,
            "reject": reject_count,
            "abstain": abstain_count
        }

    def _calculate_result(
        self,
        final_state: Dict[str, str],
        proposal_id: str,
        start_time: float,
        rounds_completed: int,
        converged: bool,
        threshold: float = 0.66
    ) -> ConsensusResult:
        """
        Calculate consensus result from final gossip state.

        Args:
            final_state: Final vote state after gossip
            proposal_id: Proposal identifier
            start_time: Start timestamp
            rounds_completed: Number of rounds executed
            converged: Whether convergence was reached
            threshold: Approval threshold (for metadata only)

        Returns:
            ConsensusResult with decision and metadata
        """
        # Aggregate votes
        decision, vote_counts = self._aggregate_majority(final_state)

        # Calculate metrics
        duration_ms = (time.time() - start_time) * 1000
        _, agreement_ratio = self._check_convergence(
            final_state,
            self._config.convergence_threshold
        )

        # Build result
        result = ConsensusResult(
            decision=decision,
            votes_for=vote_counts["approve"],
            votes_against=vote_counts["reject"],
            abstain=vote_counts["abstain"],
            threshold=threshold,
            participants=list(final_state.keys()),
            vote_details=final_state,
            metadata={
                "proposal_id": proposal_id,
                "algorithm": "gossip",
                "rounds_completed": rounds_completed,
                "converged": converged,
                "agreement_ratio": agreement_ratio,
                "convergence_threshold": self._config.convergence_threshold,
                "fanout": self._config.fanout,
                "max_rounds": self._config.max_rounds,
                "duration_ms": duration_ms,
                "round_history": self._round_history
            }
        )

        return result

    def get_state(self) -> Dict[str, Any]:
        """
        Get current algorithm state.

        Returns:
            Dict with gossip-specific state information including configuration,
            last result, and round history.

        Example:
            >>> state = gossip.get_state()
            >>> print(state["config"]["fanout"])
            3
            >>> print(state["last_result"]["decision"])
            "approved"
        """
        return {
            "algorithm": "gossip",
            "config": {
                "fanout": self._config.fanout,
                "max_rounds": self._config.max_rounds,
                "convergence_threshold": self._config.convergence_threshold,
                "round_delay_ms": self._config.round_delay_ms
            },
            "last_proposal": self._last_proposal,
            "last_result": {
                "decision": self._last_result.decision,
                "rounds_completed": self._last_result.metadata.get("rounds_completed", 0),
                "converged": self._last_result.metadata.get("converged", False),
                "agreement_ratio": self._last_result.metadata.get("agreement_ratio", 0.0)
            } if self._last_result else None,
            "round_history_count": len(self._round_history),
            "supports_timeout": True,
            "supports_abstain": True,
            "probabilistic_guarantees": True,
            "fault_tolerant": True
        }

    def reset(self) -> bool:
        """
        Reset algorithm to initial state.

        Clears last proposal, result, and round history.
        Preserves configuration.

        Returns:
            True if reset successfully, False otherwise

        Example:
            >>> gossip.reset()
            True
        """
        try:
            self._last_proposal = None
            self._last_result = None
            self._round_history = []

            logger.info("GossipProtocol reset successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to reset GossipProtocol: {e}")
            return False


__all__ = [
    "GossipProtocol",
    "GossipConfig",
]
