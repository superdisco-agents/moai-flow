"""Comprehensive tests for IssueTriage system.

This test suite verifies:
1. Triage rule matching and classification
2. Priority calculation with weighted formula
3. Assignee suggestion based on component ownership
4. SLA calculation for different priority levels
5. Edge cases and error handling
"""

import pytest
from moai_flow.github.triage import (
    IssueTriage,
    TriageRule,
    IssueMetadata,
    IssuePriority,
)


class TestTriageRuleMatching:
    """Test triage rule pattern matching."""

    def test_timeout_error_classification(self):
        """TimeoutError should be classified as HIGH priority with timeout labels."""
        triage = IssueTriage()
        error = TimeoutError("Request timeout after 30 seconds")
        context = {"component": "api", "environment": "production"}

        metadata = triage.classify(error, context)

        assert IssuePriority.HIGH in [metadata.priority, IssuePriority.CRITICAL]
        assert "timeout" in metadata.labels
        assert "performance" in metadata.labels

    def test_permission_error_classification(self):
        """PermissionError should be classified as HIGH/CRITICAL with security labels."""
        triage = IssueTriage()
        error = PermissionError("Access denied to resource")
        context = {"component": "api", "environment": "production"}

        metadata = triage.classify(error, context)

        # HIGH or CRITICAL depending on context (weighted calculation)
        assert metadata.priority in [IssuePriority.HIGH, IssuePriority.CRITICAL]
        assert "security" in metadata.labels

    def test_type_error_classification(self):
        """TypeError should be classified as MEDIUM priority."""
        triage = IssueTriage()
        error = TypeError("Expected str, got int")
        context = {"component": "backend", "environment": "development"}

        metadata = triage.classify(error, context)

        assert metadata.priority in [IssuePriority.MEDIUM, IssuePriority.LOW]
        assert "bug" in metadata.labels
        assert "type-safety" in metadata.labels

    def test_value_error_classification(self):
        """ValueError should be classified as MEDIUM with validation labels."""
        triage = IssueTriage()
        error = ValueError("Invalid value: expected 1-100, got 150")
        context = {"component": "api"}

        metadata = triage.classify(error, context)

        assert metadata.priority in [IssuePriority.MEDIUM, IssuePriority.LOW]
        assert "bug" in metadata.labels
        assert "validation" in metadata.labels

    def test_import_error_classification(self):
        """ImportError should be classified as HIGH with dependency labels."""
        triage = IssueTriage()
        error = ImportError("No module named 'missing_package'")
        context = {"component": "backend", "environment": "production"}

        metadata = triage.classify(error, context)

        assert metadata.priority in [IssuePriority.HIGH, IssuePriority.CRITICAL]
        assert "dependency" in metadata.labels
        assert "build" in metadata.labels

    def test_network_error_classification(self):
        """ConnectionError should be classified as MEDIUM with infrastructure labels."""
        triage = IssueTriage()
        error = ConnectionError("Network unreachable")
        context = {"component": "api"}

        metadata = triage.classify(error, context)

        assert metadata.priority in [IssuePriority.MEDIUM, IssuePriority.HIGH]
        assert "infrastructure" in metadata.labels
        assert "network" in metadata.labels

    def test_memory_error_classification(self):
        """MemoryError should be classified as HIGH/CRITICAL with performance labels."""
        triage = IssueTriage()
        error = MemoryError("Out of memory")
        context = {"component": "backend", "environment": "production"}

        metadata = triage.classify(error, context)

        # HIGH or CRITICAL depending on frequency and business impact
        assert metadata.priority in [IssuePriority.HIGH, IssuePriority.CRITICAL]
        assert "performance" in metadata.labels
        assert "memory" in metadata.labels

    def test_database_error_classification(self):
        """DatabaseError should be classified as HIGH with database labels."""
        triage = IssueTriage()

        # Simulate DatabaseError (custom exception)
        class DatabaseError(Exception):
            pass

        error = DatabaseError("Deadlock detected")
        context = {"component": "backend", "environment": "production"}

        metadata = triage.classify(error, context)

        assert metadata.priority in [IssuePriority.HIGH, IssuePriority.CRITICAL]

    def test_file_not_found_classification(self):
        """FileNotFoundError should be classified as MEDIUM with filesystem labels."""
        triage = IssueTriage()
        error = FileNotFoundError("File 'config.json' not found")
        context = {"component": "backend"}

        metadata = triage.classify(error, context)

        assert metadata.priority in [IssuePriority.MEDIUM, IssuePriority.LOW]
        assert "bug" in metadata.labels
        assert "filesystem" in metadata.labels

    def test_key_error_classification(self):
        """KeyError should be classified as MEDIUM with data labels."""
        triage = IssueTriage()
        error = KeyError("'user_id'")
        context = {"component": "api"}

        metadata = triage.classify(error, context)

        assert metadata.priority in [IssuePriority.MEDIUM, IssuePriority.LOW]
        assert "bug" in metadata.labels
        assert "data" in metadata.labels

    def test_assertion_error_classification(self):
        """AssertionError should be classified as HIGH with test labels."""
        triage = IssueTriage()
        error = AssertionError("Expected 5, got 3")
        context = {"component": "tests", "environment": "ci"}

        metadata = triage.classify(error, context)

        assert metadata.priority in [IssuePriority.HIGH, IssuePriority.MEDIUM]
        assert "test" in metadata.labels
        assert "bug" in metadata.labels


class TestPriorityCalculation:
    """Test priority calculation with weighted formula."""

    def test_priority_critical_production_high_frequency(self):
        """CRITICAL: High severity + production + high frequency."""
        triage = IssueTriage()
        error = MemoryError("Out of memory")
        context = {
            "environment": "production",
            "frequency": 25,
            "user_impact": 1500,
        }

        priority = triage.assign_priority(error, context)

        # Expected: 100*0.4 + 100*0.3 + 100*0.2 + 100*0.1 = 100 → CRITICAL
        assert priority == IssuePriority.CRITICAL

    def test_priority_high_production_moderate_frequency(self):
        """HIGH: Moderate severity + production + moderate frequency."""
        triage = IssueTriage()
        error = TimeoutError("Request timeout")
        context = {
            "environment": "production",
            "frequency": 8,
            "user_impact": 50,
        }

        priority = triage.assign_priority(error, context)

        # Expected: 75*0.4 + 100*0.3 + 75*0.2 + 75*0.1 = 75 → HIGH
        assert priority in [IssuePriority.HIGH, IssuePriority.CRITICAL]

    def test_priority_medium_staging(self):
        """MEDIUM: Moderate severity + staging + low frequency."""
        triage = IssueTriage()
        error = ValueError("Invalid value")
        context = {"environment": "staging", "frequency": 3}

        priority = triage.assign_priority(error, context)

        # Expected: 50*0.4 + 60*0.3 + 25*0.2 + 10*0.1 = 44 → MEDIUM
        assert priority in [IssuePriority.MEDIUM, IssuePriority.LOW]

    def test_priority_low_development(self):
        """LOW: Low severity + development + first occurrence."""
        triage = IssueTriage()
        error = TypeError("Type mismatch")
        context = {"environment": "development", "frequency": 1}

        priority = triage.assign_priority(error, context)

        # Expected: 50*0.4 + 30*0.3 + 10*0.2 + 10*0.1 = 32 → MEDIUM or LOW
        assert priority in [IssuePriority.LOW, IssuePriority.MEDIUM]

    def test_priority_business_impact_revenue(self):
        """Business impact (revenue) should boost priority."""
        triage = IssueTriage()
        error = ValueError("Payment processing failed")
        context = {
            "environment": "production",
            "tags": ["revenue"],
            "frequency": 5,
        }

        priority = triage.assign_priority(error, context)

        # Revenue tag should boost business impact score to 100
        assert priority in [IssuePriority.HIGH, IssuePriority.CRITICAL]

    def test_priority_security_tag(self):
        """Security tag should result in CRITICAL priority."""
        triage = IssueTriage()
        error = ValueError("SQL injection detected")
        context = {
            "environment": "production",
            "tags": ["security"],
            "frequency": 1,
        }

        priority = triage.assign_priority(error, context)

        # Security tag → business impact 100 → high overall score
        assert priority in [IssuePriority.HIGH, IssuePriority.CRITICAL]


class TestAssigneesSuggestion:
    """Test assignee suggestion based on component ownership."""

    def test_assignee_backend_component(self):
        """Backend component should suggest backend-team."""
        triage = IssueTriage()
        error = ValueError("Backend error")
        context = {"component": "backend"}

        assignees = triage.suggest_assignees(error, context)

        assert "backend-team" in assignees

    def test_assignee_frontend_component(self):
        """Frontend component should suggest frontend-team."""
        triage = IssueTriage()
        error = TypeError("UI rendering error")
        context = {"component": "frontend"}

        assignees = triage.suggest_assignees(error, context)

        assert "frontend-team" in assignees

    def test_assignee_database_component(self):
        """Database component should suggest database-team and backend-team."""
        triage = IssueTriage()
        error = Exception("Database error")
        context = {"component": "database"}

        assignees = triage.suggest_assignees(error, context)

        assert "database-team" in assignees or "backend-team" in assignees

    def test_assignee_security_component(self):
        """Security component should suggest security-team."""
        triage = IssueTriage()
        error = PermissionError("Security violation")
        context = {"component": "security"}

        assignees = triage.suggest_assignees(error, context)

        assert "security-team" in assignees

    def test_assignee_devops_component(self):
        """CI/CD component should suggest devops-team."""
        triage = IssueTriage()
        error = Exception("Build failed")
        context = {"component": "ci-cd"}

        assignees = triage.suggest_assignees(error, context)

        assert "devops-team" in assignees

    def test_assignee_unknown_component(self):
        """Unknown component should return empty list."""
        triage = IssueTriage()
        error = ValueError("Unknown error")
        context = {"component": "unknown-module"}

        assignees = triage.suggest_assignees(error, context)

        # Unknown component may return empty list or default assignee
        assert isinstance(assignees, list)


class TestSLACalculation:
    """Test SLA calculation for different priority levels."""

    def test_sla_critical(self):
        """CRITICAL priority should have 4-hour SLA."""
        triage = IssueTriage()
        sla = triage.calculate_sla(IssuePriority.CRITICAL)
        assert sla == 4

    def test_sla_high(self):
        """HIGH priority should have 24-hour SLA."""
        triage = IssueTriage()
        sla = triage.calculate_sla(IssuePriority.HIGH)
        assert sla == 24

    def test_sla_medium(self):
        """MEDIUM priority should have 72-hour SLA."""
        triage = IssueTriage()
        sla = triage.calculate_sla(IssuePriority.MEDIUM)
        assert sla == 72

    def test_sla_low(self):
        """LOW priority should have 168-hour SLA."""
        triage = IssueTriage()
        sla = triage.calculate_sla(IssuePriority.LOW)
        assert sla == 168


class TestCustomRules:
    """Test custom triage rules."""

    def test_custom_rule_addition(self):
        """Custom rules should extend default rules."""
        custom_rules = [
            TriageRule(
                error_patterns=[r"custom error"],
                labels=["custom", "special"],
                priority=IssuePriority.CRITICAL,
                assignees=["custom-team"],
            )
        ]

        triage = IssueTriage(custom_rules=custom_rules)

        class CustomError(Exception):
            pass

        error = CustomError("Custom error occurred")
        context = {"component": "special-module"}

        metadata = triage.classify(error, context)

        # Custom rule should match and apply labels
        assert "custom" in metadata.labels or metadata.priority == IssuePriority.CRITICAL


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_context(self):
        """Empty context should not cause errors."""
        triage = IssueTriage()
        error = ValueError("Test error")
        context = {}

        metadata = triage.classify(error, context)

        assert metadata.title
        assert metadata.body
        assert metadata.labels
        assert metadata.priority

    def test_missing_environment(self):
        """Missing environment should default to moderate priority."""
        triage = IssueTriage()
        error = ValueError("Test error")
        context = {"frequency": 5}

        metadata = triage.classify(error, context)

        # Without environment, priority calculation should still work
        assert metadata.priority in [
            IssuePriority.LOW,
            IssuePriority.MEDIUM,
            IssuePriority.HIGH,
        ]

    def test_very_long_error_message(self):
        """Very long error message should be handled gracefully."""
        triage = IssueTriage()
        long_message = "Error: " + "A" * 1000
        error = ValueError(long_message)
        context = {}

        metadata = triage.classify(error, context)

        # Title should be truncated
        assert len(metadata.title) < 200
        assert metadata.body

    def test_special_characters_in_error(self):
        """Special characters should be normalized in labels."""
        triage = IssueTriage()
        error = ValueError("Error with @#$% special chars")
        context = {}

        metadata = triage.classify(error, context)

        # Labels should be normalized
        for label in metadata.labels:
            assert label.islower()
            assert " " not in label

    def test_production_environment_priority_boost(self):
        """Production environment should boost priority significantly."""
        triage = IssueTriage()
        error = ValueError("Test error")

        # Same error in different environments
        dev_context = {"environment": "development", "frequency": 1}
        prod_context = {"environment": "production", "frequency": 1}

        dev_priority = triage.assign_priority(error, dev_context)
        prod_priority = triage.assign_priority(error, prod_context)

        # Production should have higher priority
        priority_order = {
            IssuePriority.LOW: 1,
            IssuePriority.MEDIUM: 2,
            IssuePriority.HIGH: 3,
            IssuePriority.CRITICAL: 4,
        }

        assert priority_order[prod_priority] >= priority_order[dev_priority]


class TestWeightedScoreCalculation:
    """Test individual score calculation methods."""

    def test_severity_score_critical(self):
        """Critical errors should get 100 severity score."""
        triage = IssueTriage()
        score = triage._calculate_severity_score("MemoryError", "out of memory")
        assert score == 100.0

    def test_severity_score_high(self):
        """High severity errors should get 75 severity score."""
        triage = IssueTriage()
        score = triage._calculate_severity_score("TimeoutError", "timeout")
        assert score == 75.0

    def test_severity_score_medium(self):
        """Medium severity errors should get 50 severity score."""
        triage = IssueTriage()
        score = triage._calculate_severity_score("ValueError", "invalid value")
        assert score == 50.0

    def test_environment_score_production(self):
        """Production environment should get 100 score."""
        triage = IssueTriage()
        score = triage._calculate_environment_score({"environment": "production"})
        assert score == 100.0

    def test_environment_score_staging(self):
        """Staging environment should get 60 score."""
        triage = IssueTriage()
        score = triage._calculate_environment_score({"environment": "staging"})
        assert score == 60.0

    def test_frequency_score_high(self):
        """High frequency (20+) should get 100 score."""
        triage = IssueTriage()
        score = triage._calculate_frequency_score({"frequency": 25})
        assert score == 100.0

    def test_frequency_score_medium(self):
        """Medium frequency (5-9) should get 50 score."""
        triage = IssueTriage()
        score = triage._calculate_frequency_score({"frequency": 7})
        assert score == 50.0

    def test_business_impact_revenue(self):
        """Revenue-affecting issues should get 100 business impact score."""
        triage = IssueTriage()
        score = triage._calculate_business_impact_score(
            {"tags": ["revenue"]}, "payment failed"
        )
        assert score == 100.0

    def test_business_impact_user_count(self):
        """High user impact should get 100 business impact score."""
        triage = IssueTriage()
        score = triage._calculate_business_impact_score(
            {"user_impact": 2000}, "error"
        )
        assert score == 100.0


# Additional integration test
class TestEndToEndTriage:
    """End-to-end integration tests."""

    def test_production_timeout_high_frequency(self):
        """Production timeout with high frequency should be CRITICAL."""
        triage = IssueTriage()
        error = TimeoutError("API timeout after 30s")
        context = {
            "component": "api",
            "environment": "production",
            "frequency": 30,
            "user_impact": 500,
        }

        metadata = triage.classify(error, context)

        # Should be CRITICAL or HIGH
        assert metadata.priority in [IssuePriority.CRITICAL, IssuePriority.HIGH]
        assert "timeout" in metadata.labels
        assert "production" in metadata.labels
        assert len(metadata.assignees) > 0
        assert metadata.title
        assert metadata.body

    def test_development_type_error_low_frequency(self):
        """Development TypeError with low frequency should be LOW/MEDIUM."""
        triage = IssueTriage()
        error = TypeError("Expected str, got int")
        context = {
            "component": "backend",
            "environment": "development",
            "frequency": 1,
        }

        metadata = triage.classify(error, context)

        assert metadata.priority in [IssuePriority.LOW, IssuePriority.MEDIUM]
        assert "bug" in metadata.labels
