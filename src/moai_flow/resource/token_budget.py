"""
TokenBudget: Per-Swarm Token Allocation Manager

Manages token budgets across multiple swarms to prevent context window overflow.
Integrates with MoAI-ADK's JIT Context Loader for unified token management.

Features:
- Per-swarm token allocation with configurable limits
- Real-time consumption tracking
- Warning thresholds (150K, 180K)
- Budget reallocation and reset mechanisms
- Integration with .moai/config/config.json
"""

import json
import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class SwarmAllocation:
    """Token allocation for a specific swarm"""

    swarm_id: str
    allocated: int
    consumed: int = 0
    reserved: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    warnings_issued: List[str] = field(default_factory=list)

    @property
    def available(self) -> int:
        """Calculate available tokens (allocated - consumed - reserved)"""
        return max(0, self.allocated - self.consumed - self.reserved)

    @property
    def usage_percent(self) -> float:
        """Calculate usage percentage"""
        if self.allocated == 0:
            return 0.0
        return (self.consumed / self.allocated) * 100

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "swarm_id": self.swarm_id,
            "allocated": self.allocated,
            "consumed": self.consumed,
            "reserved": self.reserved,
            "available": self.available,
            "usage_percent": self.usage_percent,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "warnings_issued": self.warnings_issued,
        }


@dataclass
class BudgetConfig:
    """Configuration for token budget management"""

    total_budget: int = 200000  # Global 200K budget from CLAUDE.md
    warning_threshold_1: int = 150000  # First warning at 150K
    warning_threshold_2: int = 180000  # Critical warning at 180K
    default_swarm_limit: int = 50000  # Default per-swarm allocation
    enable_auto_rebalance: bool = True
    enable_warnings: bool = True
    reserve_buffer: int = 10000  # Reserve 10K for critical operations

    @classmethod
    def from_config(cls, config_path: str = ".moai/config/config.json") -> "BudgetConfig":
        """Load budget configuration from MoAI config file"""
        config_file = Path(config_path)

        # Default configuration
        config = cls()

        if not config_file.exists():
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return config

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Extract token budget settings if they exist
            if "token_budget" in data:
                budget_data = data["token_budget"]
                config.total_budget = budget_data.get("total_budget", 200000)
                config.warning_threshold_1 = budget_data.get("warning_threshold_1", 150000)
                config.warning_threshold_2 = budget_data.get("warning_threshold_2", 180000)
                config.default_swarm_limit = budget_data.get("default_swarm_limit", 50000)
                config.enable_auto_rebalance = budget_data.get("enable_auto_rebalance", True)
                config.enable_warnings = budget_data.get("enable_warnings", True)
                config.reserve_buffer = budget_data.get("reserve_buffer", 10000)

            logger.info(f"Loaded token budget config: total={config.total_budget}")

        except Exception as e:
            logger.error(f"Error loading config from {config_path}: {e}")

        return config


class TokenBudget:
    """
    Per-Swarm Token Allocation Manager

    Manages token budgets across multiple swarms with:
    - Dynamic allocation per swarm
    - Real-time consumption tracking
    - Warning threshold monitoring (150K, 180K)
    - Budget rebalancing
    - Integration with MoAI config
    """

    def __init__(self, config_path: str = ".moai/config/config.json"):
        """
        Initialize TokenBudget manager

        Args:
            config_path: Path to MoAI configuration file
        """
        self.config = BudgetConfig.from_config(config_path)
        self.allocations: Dict[str, SwarmAllocation] = {}
        self.total_consumed: int = 0
        self.lock = threading.RLock()  # Thread-safe operations

        # Statistics tracking
        self.allocation_history: List[Dict] = []
        self.warning_log: List[Dict] = []

        logger.info(
            f"TokenBudget initialized: total={self.config.total_budget}, "
            f"default_swarm={self.config.default_swarm_limit}"
        )

    def allocate_swarm(self, swarm_id: str, token_limit: Optional[int] = None) -> bool:
        """
        Allocate tokens to a specific swarm

        Args:
            swarm_id: Unique identifier for the swarm
            token_limit: Custom token limit (uses default if None)

        Returns:
            True if allocation successful, False otherwise
        """
        with self.lock:
            # Check if swarm already exists
            if swarm_id in self.allocations:
                logger.warning(f"Swarm {swarm_id} already allocated, skipping")
                return False

            # Determine allocation amount
            allocation_amount = token_limit or self.config.default_swarm_limit

            # Check if allocation exceeds available budget
            available_budget = self._calculate_available_budget()
            if allocation_amount > available_budget:
                logger.error(
                    f"Cannot allocate {allocation_amount} tokens to {swarm_id}: "
                    f"only {available_budget} tokens available"
                )
                return False

            # Create allocation
            allocation = SwarmAllocation(swarm_id=swarm_id, allocated=allocation_amount)

            self.allocations[swarm_id] = allocation
            self.allocation_history.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "swarm_id": swarm_id,
                    "allocated": allocation_amount,
                    "action": "allocate",
                }
            )

            logger.info(f"Allocated {allocation_amount} tokens to swarm {swarm_id}")
            return True

    def consume(self, swarm_id: str, tokens: int) -> bool:
        """
        Track token consumption for a swarm

        Args:
            swarm_id: Swarm identifier
            tokens: Number of tokens to consume

        Returns:
            True if consumption allowed, False if exceeds budget
        """
        with self.lock:
            # Check if swarm exists
            if swarm_id not in self.allocations:
                logger.error(f"Swarm {swarm_id} not allocated")
                return False

            allocation = self.allocations[swarm_id]

            # Validate consumption doesn't exceed available
            if tokens > allocation.available:
                logger.error(
                    f"Cannot consume {tokens} tokens for {swarm_id}: "
                    f"only {allocation.available} available (allocated={allocation.allocated}, "
                    f"consumed={allocation.consumed}, reserved={allocation.reserved})"
                )
                return False

            # Update consumption
            allocation.consumed += tokens
            allocation.last_updated = datetime.now()
            self.total_consumed += tokens

            # Check for warnings
            if self.config.enable_warnings:
                self._check_warnings(swarm_id, allocation)

            logger.debug(
                f"Consumed {tokens} tokens for {swarm_id}: "
                f"{allocation.consumed}/{allocation.allocated} "
                f"({allocation.usage_percent:.1f}%)"
            )

            return True

    def reserve(self, swarm_id: str, tokens: int) -> bool:
        """
        Reserve tokens for planned operations

        Args:
            swarm_id: Swarm identifier
            tokens: Number of tokens to reserve

        Returns:
            True if reservation successful, False otherwise
        """
        with self.lock:
            if swarm_id not in self.allocations:
                logger.error(f"Swarm {swarm_id} not allocated")
                return False

            allocation = self.allocations[swarm_id]

            # Check if reservation possible
            if tokens > allocation.available:
                logger.error(
                    f"Cannot reserve {tokens} tokens for {swarm_id}: " f"only {allocation.available} available"
                )
                return False

            allocation.reserved += tokens
            allocation.last_updated = datetime.now()

            logger.debug(f"Reserved {tokens} tokens for {swarm_id}")
            return True

    def release_reservation(self, swarm_id: str, tokens: int) -> bool:
        """
        Release previously reserved tokens

        Args:
            swarm_id: Swarm identifier
            tokens: Number of tokens to release

        Returns:
            True if release successful, False otherwise
        """
        with self.lock:
            if swarm_id not in self.allocations:
                logger.error(f"Swarm {swarm_id} not allocated")
                return False

            allocation = self.allocations[swarm_id]

            if tokens > allocation.reserved:
                logger.warning(
                    f"Attempting to release {tokens} tokens but only " f"{allocation.reserved} reserved for {swarm_id}"
                )
                tokens = allocation.reserved

            allocation.reserved -= tokens
            allocation.last_updated = datetime.now()

            logger.debug(f"Released {tokens} reserved tokens for {swarm_id}")
            return True

    def get_balance(self, swarm_id: str) -> int:
        """
        Get remaining token balance for a swarm

        Args:
            swarm_id: Swarm identifier

        Returns:
            Available tokens, or -1 if swarm not found
        """
        with self.lock:
            if swarm_id not in self.allocations:
                logger.warning(f"Swarm {swarm_id} not found")
                return -1

            return self.allocations[swarm_id].available

    def get_usage_percent(self, swarm_id: str) -> float:
        """
        Calculate usage percentage for a swarm

        Args:
            swarm_id: Swarm identifier

        Returns:
            Usage percentage (0-100), or -1 if swarm not found
        """
        with self.lock:
            if swarm_id not in self.allocations:
                logger.warning(f"Swarm {swarm_id} not found")
                return -1.0

            return self.allocations[swarm_id].usage_percent

    def should_warn(self, swarm_id: str) -> Tuple[bool, Optional[str]]:
        """
        Check if swarm has exceeded warning thresholds

        Args:
            swarm_id: Swarm identifier

        Returns:
            Tuple of (should_warn, warning_message)
        """
        with self.lock:
            if swarm_id not in self.allocations:
                return False, None

            allocation = self.allocations[swarm_id]
            usage_percent = allocation.usage_percent

            if usage_percent >= 90:
                return True, f"CRITICAL: Swarm {swarm_id} at {usage_percent:.1f}% token usage"
            elif usage_percent >= 75:
                return True, f"WARNING: Swarm {swarm_id} at {usage_percent:.1f}% token usage"
            else:
                return False, None

    def reset(self, swarm_id: str) -> bool:
        """
        Reset swarm budget (e.g., after /clear command)

        Args:
            swarm_id: Swarm identifier

        Returns:
            True if reset successful, False otherwise
        """
        with self.lock:
            if swarm_id not in self.allocations:
                logger.warning(f"Swarm {swarm_id} not found for reset")
                return False

            allocation = self.allocations[swarm_id]
            old_consumed = allocation.consumed

            # Reset consumption but keep allocation
            allocation.consumed = 0
            allocation.reserved = 0
            allocation.warnings_issued.clear()
            allocation.last_updated = datetime.now()

            self.total_consumed -= old_consumed

            self.allocation_history.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "swarm_id": swarm_id,
                    "action": "reset",
                    "previous_consumed": old_consumed,
                }
            )

            logger.info(f"Reset swarm {swarm_id}: cleared {old_consumed} consumed tokens")
            return True

    def deallocate_swarm(self, swarm_id: str) -> bool:
        """
        Remove swarm allocation completely

        Args:
            swarm_id: Swarm identifier

        Returns:
            True if deallocation successful, False otherwise
        """
        with self.lock:
            if swarm_id not in self.allocations:
                logger.warning(f"Swarm {swarm_id} not found for deallocation")
                return False

            allocation = self.allocations.pop(swarm_id)
            self.total_consumed -= allocation.consumed

            self.allocation_history.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "swarm_id": swarm_id,
                    "action": "deallocate",
                    "consumed": allocation.consumed,
                    "allocated": allocation.allocated,
                }
            )

            logger.info(f"Deallocated swarm {swarm_id}")
            return True

    def rebalance(self) -> Dict[str, int]:
        """
        Rebalance token allocations across swarms

        Returns:
            Dictionary of swarm_id -> new_allocation
        """
        with self.lock:
            if not self.config.enable_auto_rebalance:
                logger.info("Auto-rebalance disabled")
                return {}

            if not self.allocations:
                return {}

            # Calculate available budget
            available_budget = self._calculate_available_budget()

            # Distribute evenly among swarms
            num_swarms = len(self.allocations)
            base_allocation = (self.config.total_budget - self.config.reserve_buffer) // num_swarms

            rebalance_plan = {}
            for swarm_id, allocation in self.allocations.items():
                # Don't reduce below consumed amount
                new_allocation = max(base_allocation, allocation.consumed + 1000)
                rebalance_plan[swarm_id] = new_allocation
                allocation.allocated = new_allocation
                allocation.last_updated = datetime.now()

            logger.info(f"Rebalanced {num_swarms} swarms: base={base_allocation}")
            return rebalance_plan

    def get_global_status(self) -> Dict:
        """
        Get global token budget status

        Returns:
            Dictionary with comprehensive status information
        """
        with self.lock:
            total_allocated = sum(a.allocated for a in self.allocations.values())
            total_available = sum(a.available for a in self.allocations.values())

            # Check global thresholds
            global_usage_percent = (self.total_consumed / self.config.total_budget) * 100
            warn_level = "normal"

            if self.total_consumed >= self.config.warning_threshold_2:
                warn_level = "critical"
            elif self.total_consumed >= self.config.warning_threshold_1:
                warn_level = "warning"

            return {
                "total_budget": self.config.total_budget,
                "total_consumed": self.total_consumed,
                "total_allocated": total_allocated,
                "total_available": total_available,
                "global_usage_percent": global_usage_percent,
                "warn_level": warn_level,
                "active_swarms": len(self.allocations),
                "swarms": {swarm_id: alloc.to_dict() for swarm_id, alloc in self.allocations.items()},
                "thresholds": {
                    "warning_1": self.config.warning_threshold_1,
                    "warning_2": self.config.warning_threshold_2,
                },
            }

    def _calculate_available_budget(self) -> int:
        """Calculate available budget for new allocations"""
        total_allocated = sum(a.allocated for a in self.allocations.values())
        return max(0, self.config.total_budget - total_allocated - self.config.reserve_buffer)

    def _check_warnings(self, swarm_id: str, allocation: SwarmAllocation):
        """Check and issue warnings for threshold violations"""
        should_warn, message = self.should_warn(swarm_id)

        if should_warn and message not in allocation.warnings_issued:
            allocation.warnings_issued.append(message)
            self.warning_log.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "swarm_id": swarm_id,
                    "message": message,
                    "usage_percent": allocation.usage_percent,
                }
            )
            logger.warning(message)

        # Global threshold check
        if self.total_consumed >= self.config.warning_threshold_2:
            global_warning = (
                f"CRITICAL: Global token usage at {self.total_consumed}/{self.config.total_budget} "
                f"({(self.total_consumed/self.config.total_budget)*100:.1f}%) - Execute /clear recommended"
            )
            if global_warning not in [w["message"] for w in self.warning_log[-5:]]:
                self.warning_log.append(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "swarm_id": "GLOBAL",
                        "message": global_warning,
                        "usage_percent": (self.total_consumed / self.config.total_budget) * 100,
                    }
                )
                logger.critical(global_warning)

        elif self.total_consumed >= self.config.warning_threshold_1:
            global_warning = (
                f"WARNING: Global token usage at {self.total_consumed}/{self.config.total_budget} "
                f"({(self.total_consumed/self.config.total_budget)*100:.1f}%)"
            )
            if global_warning not in [w["message"] for w in self.warning_log[-5:]]:
                self.warning_log.append(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "swarm_id": "GLOBAL",
                        "message": global_warning,
                        "usage_percent": (self.total_consumed / self.config.total_budget) * 100,
                    }
                )
                logger.warning(global_warning)


# Global instance for easy import
token_budget = TokenBudget()


# Convenience functions
def allocate_swarm(swarm_id: str, token_limit: Optional[int] = None) -> bool:
    """Allocate tokens to a swarm using global instance"""
    return token_budget.allocate_swarm(swarm_id, token_limit)


def consume_tokens(swarm_id: str, tokens: int) -> bool:
    """Consume tokens for a swarm using global instance"""
    return token_budget.consume(swarm_id, tokens)


def get_swarm_balance(swarm_id: str) -> int:
    """Get swarm token balance using global instance"""
    return token_budget.get_balance(swarm_id)


def reset_swarm(swarm_id: str) -> bool:
    """Reset swarm budget using global instance"""
    return token_budget.reset(swarm_id)


def get_budget_status() -> Dict:
    """Get global budget status using global instance"""
    return token_budget.get_global_status()
