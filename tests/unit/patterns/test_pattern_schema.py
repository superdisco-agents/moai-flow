"""
Tests for Pattern Schema Validation
====================================

Comprehensive tests for pattern schema definitions and validators.
"""

import pytest
from datetime import datetime

from moai_flow.patterns.schema import (
    PatternType,
    PatternSchema,
    TaskCompletionData,
    ErrorOccurrenceData,
    AgentUsageData,
    UserCorrectionData,
    PatternContext,
    Pattern
)


class TestTaskCompletionValidation:
    """Test task completion data validation."""

    def test_valid_task_completion(self):
        """Test valid task completion data."""
        data = {
            "task_type": "code_generation",
            "agent": "expert-backend",
            "duration_ms": 2500,
            "success": True
        }
        assert PatternSchema.validate_task_completion(data)

    def test_missing_required_field(self):
        """Test validation fails with missing required field."""
        data = {
            "task_type": "code_generation",
            "agent": "expert-backend",
            # Missing duration_ms and success
        }
        assert not PatternSchema.validate_task_completion(data)

    def test_invalid_type(self):
        """Test validation fails with invalid type."""
        data = {
            "task_type": "code_generation",
            "agent": "expert-backend",
            "duration_ms": "invalid",  # Should be int
            "success": True
        }
        assert not PatternSchema.validate_task_completion(data)

    def test_negative_duration(self):
        """Test validation fails with negative duration."""
        data = {
            "task_type": "code_generation",
            "agent": "expert-backend",
            "duration_ms": -100,
            "success": True
        }
        assert not PatternSchema.validate_task_completion(data)

    def test_invalid_coverage_percent(self):
        """Test validation fails with invalid coverage percentage."""
        data = {
            "task_type": "code_generation",
            "agent": "expert-backend",
            "duration_ms": 2500,
            "success": True,
            "coverage_percent": 150.0  # Should be 0-100
        }
        assert not PatternSchema.validate_task_completion(data)

    def test_valid_coverage_percent(self):
        """Test validation succeeds with valid coverage percentage."""
        data = {
            "task_type": "code_generation",
            "agent": "expert-backend",
            "duration_ms": 2500,
            "success": True,
            "coverage_percent": 85.5
        }
        assert PatternSchema.validate_task_completion(data)


class TestErrorOccurrenceValidation:
    """Test error occurrence data validation."""

    def test_valid_error_occurrence(self):
        """Test valid error occurrence data."""
        data = {
            "error_type": "TypeError",
            "error_message": "unsupported operand type"
        }
        assert PatternSchema.validate_error_occurrence(data)

    def test_missing_required_field(self):
        """Test validation fails with missing required field."""
        data = {
            "error_type": "TypeError"
            # Missing error_message
        }
        assert not PatternSchema.validate_error_occurrence(data)

    def test_invalid_line_number(self):
        """Test validation fails with invalid line number."""
        data = {
            "error_type": "TypeError",
            "error_message": "error",
            "line_number": -5  # Should be >= 0
        }
        assert not PatternSchema.validate_error_occurrence(data)

    def test_valid_line_number(self):
        """Test validation succeeds with valid line number."""
        data = {
            "error_type": "TypeError",
            "error_message": "error",
            "line_number": 42
        }
        assert PatternSchema.validate_error_occurrence(data)


class TestAgentUsageValidation:
    """Test agent usage data validation."""

    def test_valid_agent_usage(self):
        """Test valid agent usage data."""
        data = {
            "agent_type": "expert-backend",
            "task_type": "code_generation",
            "success": True,
            "duration_ms": 3000
        }
        assert PatternSchema.validate_agent_usage(data)

    def test_missing_required_field(self):
        """Test validation fails with missing required field."""
        data = {
            "agent_type": "expert-backend",
            "task_type": "code_generation"
            # Missing success and duration_ms
        }
        assert not PatternSchema.validate_agent_usage(data)

    def test_invalid_tools_list(self):
        """Test validation fails with invalid tools list."""
        data = {
            "agent_type": "expert-backend",
            "task_type": "code_generation",
            "success": True,
            "duration_ms": 3000,
            "tools_used": ["Read", 123, "Write"]  # Mixed types
        }
        assert not PatternSchema.validate_agent_usage(data)

    def test_valid_tools_list(self):
        """Test validation succeeds with valid tools list."""
        data = {
            "agent_type": "expert-backend",
            "task_type": "code_generation",
            "success": True,
            "duration_ms": 3000,
            "tools_used": ["Read", "Write", "Edit"]
        }
        assert PatternSchema.validate_agent_usage(data)


class TestUserCorrectionValidation:
    """Test user correction data validation."""

    def test_valid_user_correction(self):
        """Test valid user correction data."""
        data = {
            "original_output": "def foo(): pass",
            "corrected_output": "def foo() -> None: pass",
            "correction_type": "type_hints",
            "agent": "expert-backend"
        }
        assert PatternSchema.validate_user_correction(data)

    def test_missing_required_field(self):
        """Test validation fails with missing required field."""
        data = {
            "original_output": "def foo(): pass",
            "corrected_output": "def foo() -> None: pass"
            # Missing correction_type and agent
        }
        assert not PatternSchema.validate_user_correction(data)

    def test_invalid_severity(self):
        """Test validation fails with invalid severity."""
        data = {
            "original_output": "def foo(): pass",
            "corrected_output": "def foo() -> None: pass",
            "correction_type": "type_hints",
            "agent": "expert-backend",
            "severity": "ultra-critical"  # Not in valid set
        }
        assert not PatternSchema.validate_user_correction(data)

    def test_valid_severity(self):
        """Test validation succeeds with valid severity."""
        for severity in ["minor", "moderate", "critical"]:
            data = {
                "original_output": "def foo(): pass",
                "corrected_output": "def foo() -> None: pass",
                "correction_type": "type_hints",
                "agent": "expert-backend",
                "severity": severity
            }
            assert PatternSchema.validate_user_correction(data)


class TestPatternContextValidation:
    """Test pattern context validation."""

    def test_valid_context(self):
        """Test valid pattern context."""
        context = {
            "project_name": "moai-adk",
            "environment": "development",
            "timestamp": datetime.now().isoformat()
        }
        assert PatternSchema.validate_context(context)

    def test_invalid_environment(self):
        """Test validation fails with invalid environment."""
        context = {
            "environment": "super-production"  # Not in valid set
        }
        assert not PatternSchema.validate_context(context)

    def test_valid_environments(self):
        """Test validation succeeds with all valid environments."""
        for env in ["development", "staging", "production"]:
            context = {"environment": env}
            assert PatternSchema.validate_context(context)

    def test_invalid_tags(self):
        """Test validation fails with invalid tags."""
        context = {
            "tags": ["valid", 123, "another"]  # Mixed types
        }
        assert not PatternSchema.validate_context(context)

    def test_valid_tags(self):
        """Test validation succeeds with valid tags."""
        context = {
            "tags": ["backend", "authentication", "security"]
        }
        assert PatternSchema.validate_context(context)

    def test_invalid_timestamp(self):
        """Test validation fails with invalid timestamp."""
        context = {
            "timestamp": "not-a-valid-timestamp"
        }
        assert not PatternSchema.validate_context(context)

    def test_valid_timestamp(self):
        """Test validation succeeds with valid timestamp."""
        context = {
            "timestamp": datetime.now().isoformat()
        }
        assert PatternSchema.validate_context(context)


class TestCompletePatternValidation:
    """Test complete pattern structure validation."""

    def test_valid_complete_pattern(self):
        """Test valid complete pattern."""
        pattern: Pattern = {
            "pattern_id": "test-123",
            "pattern_type": PatternType.TASK_COMPLETION,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "task_type": "code_generation",
                "agent": "expert-backend",
                "duration_ms": 2500,
                "success": True
            },
            "context": {
                "project_name": "moai-adk",
                "environment": "development"
            },
            "version": "1.0"
        }
        assert PatternSchema.validate_pattern(pattern)

    def test_missing_root_field(self):
        """Test validation fails with missing root field."""
        pattern = {
            "pattern_id": "test-123",
            "pattern_type": PatternType.TASK_COMPLETION
            # Missing timestamp and data
        }
        assert not PatternSchema.validate_pattern(pattern)

    def test_invalid_pattern_type(self):
        """Test validation fails with invalid pattern type."""
        pattern = {
            "pattern_id": "test-123",
            "pattern_type": "invalid_type",
            "timestamp": datetime.now().isoformat(),
            "data": {}
        }
        assert not PatternSchema.validate_pattern(pattern)

    def test_invalid_timestamp(self):
        """Test validation fails with invalid timestamp."""
        pattern = {
            "pattern_id": "test-123",
            "pattern_type": PatternType.TASK_COMPLETION,
            "timestamp": "not-a-timestamp",
            "data": {
                "task_type": "code_generation",
                "agent": "expert-backend",
                "duration_ms": 2500,
                "success": True
            }
        }
        assert not PatternSchema.validate_pattern(pattern)

    def test_invalid_context(self):
        """Test validation fails with invalid context."""
        pattern = {
            "pattern_id": "test-123",
            "pattern_type": PatternType.TASK_COMPLETION,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "task_type": "code_generation",
                "agent": "expert-backend",
                "duration_ms": 2500,
                "success": True
            },
            "context": {
                "environment": "invalid-env"  # Invalid environment
            }
        }
        assert not PatternSchema.validate_pattern(pattern)

    def test_invalid_pattern_data(self):
        """Test validation fails with invalid pattern-specific data."""
        pattern = {
            "pattern_id": "test-123",
            "pattern_type": PatternType.TASK_COMPLETION,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "task_type": "code_generation"
                # Missing required fields
            }
        }
        assert not PatternSchema.validate_pattern(pattern)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
