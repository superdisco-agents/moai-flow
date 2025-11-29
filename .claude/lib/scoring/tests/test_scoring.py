#!/usr/bin/env python3
"""
Comprehensive test suite for directory scoring algorithm

Tests cover:
- Individual factor scoring functions
- Classification thresholds
- Protected paths and safety checks
- Project type detection
- Batch processing
- Export formats
- Edge cases and error handling
"""

import os
import sys
import json
import tempfile
import shutil
import subprocess
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scoring import (
    DirectoryScorer,
    DirectoryScore,
    ScoringConfig
)


class TestDirectoryScorer:
    """Test suite for DirectoryScorer class"""

    @staticmethod
    def setup_test_directory(base_path, structure):
        """
        Create a test directory structure

        Args:
            base_path: Base path for test directory
            structure: Dict describing directory structure
                      {filename: content or {subdirs}}
        """
        for name, content in structure.items():
            path = os.path.join(base_path, name)

            if isinstance(content, dict):
                os.makedirs(path, exist_ok=True)
                TestDirectoryScorer.setup_test_directory(path, content)
            else:
                with open(path, 'w') as f:
                    f.write(content or "")

    @staticmethod
    def test_time_decay_scoring():
        """Test time-based decay scoring"""
        print("Testing time decay scoring...")

        with tempfile.TemporaryDirectory() as tmpdir:
            scorer = DirectoryScorer()

            # Test recent modification (< 7 days)
            score = scorer._score_time_decay(tmpdir, time.time())
            assert score == 10, f"Expected 10 for recent directory, got {score}"

            # Test older modification (30 days)
            old_time = time.time() + (30 * 24 * 3600)
            score = scorer._score_time_decay(tmpdir, old_time)
            assert 0 < score < 10, f"Expected 0-10 for 30-day old directory, got {score}"

            # Test very old modification (200 days)
            very_old_time = time.time() + (200 * 24 * 3600)
            score = scorer._score_time_decay(tmpdir, very_old_time)
            assert score < 0, f"Expected negative score for very old directory, got {score}"

        print("✓ Time decay scoring tests passed")

    @staticmethod
    def test_git_activity_scoring():
        """Test git repository activity scoring"""
        print("Testing git activity scoring...")

        with tempfile.TemporaryDirectory() as tmpdir:
            scorer = DirectoryScorer()

            # Test non-git directory
            score = scorer._score_git_activity(tmpdir)
            assert score == 0, f"Expected 0 for non-git directory, got {score}"

            # Create git repository
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmpdir)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmpdir)

            # Test git directory with no commits
            score = scorer._score_git_activity(tmpdir)
            assert score >= 5, f"Expected ≥5 for git directory, got {score}"

            # Add a commit
            test_file = os.path.join(tmpdir, "test.txt")
            with open(test_file, 'w') as f:
                f.write("test")

            subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=tmpdir, capture_output=True)

            # Test with commits
            score = scorer._score_git_activity(tmpdir)
            assert score > 5, f"Expected >5 for git directory with commits, got {score}"

        print("✓ Git activity scoring tests passed")

    @staticmethod
    def test_dependency_scoring():
        """Test dependency file scoring"""
        print("Testing dependency scoring...")

        with tempfile.TemporaryDirectory() as tmpdir:
            scorer = DirectoryScorer()

            # Test empty directory
            score = scorer._score_dependencies(tmpdir, None)
            assert score == 0, f"Expected 0 for empty directory, got {score}"

            # Add package.json
            with open(os.path.join(tmpdir, "package.json"), 'w') as f:
                f.write('{"name": "test"}')

            score = scorer._score_dependencies(tmpdir, "node")
            assert score >= 10, f"Expected ≥10 with package.json, got {score}"

            # Add lock file
            with open(os.path.join(tmpdir, "package-lock.json"), 'w') as f:
                f.write('{}')

            score = scorer._score_dependencies(tmpdir, "node")
            assert score >= 15, f"Expected ≥15 with lock file, got {score}"

            # Add multiple dependency systems
            with open(os.path.join(tmpdir, "requirements.txt"), 'w') as f:
                f.write('flask==2.0.0')

            score = scorer._score_dependencies(tmpdir, "node")
            assert score >= 18, f"Expected ≥18 with multiple systems, got {score}"

        print("✓ Dependency scoring tests passed")

    @staticmethod
    def test_documentation_scoring():
        """Test documentation scoring"""
        print("Testing documentation scoring...")

        with tempfile.TemporaryDirectory() as tmpdir:
            scorer = DirectoryScorer()

            # Test empty directory
            score = scorer._score_documentation(tmpdir)
            assert score == 0, f"Expected 0 for empty directory, got {score}"

            # Add README
            with open(os.path.join(tmpdir, "README.md"), 'w') as f:
                f.write("# Test Project")

            score = scorer._score_documentation(tmpdir)
            assert score >= 8, f"Expected ≥8 with README, got {score}"

            # Add more documentation
            with open(os.path.join(tmpdir, "CONTRIBUTING.md"), 'w') as f:
                f.write("# Contributing")

            with open(os.path.join(tmpdir, "LICENSE"), 'w') as f:
                f.write("MIT License")

            score = scorer._score_documentation(tmpdir)
            assert score >= 12, f"Expected ≥12 with multiple docs, got {score}"

            # Add docs directory
            os.makedirs(os.path.join(tmpdir, "docs"))

            score = scorer._score_documentation(tmpdir)
            assert score >= 17, f"Expected ≥17 with docs directory, got {score}"

        print("✓ Documentation scoring tests passed")

    @staticmethod
    def test_file_activity_scoring():
        """Test file activity scoring"""
        print("Testing file activity scoring...")

        with tempfile.TemporaryDirectory() as tmpdir:
            scorer = DirectoryScorer()

            # Test empty directory
            score = scorer._score_file_activity(tmpdir)
            assert score == 0, f"Expected 0 for empty directory, got {score}"

            # Add some files
            for i in range(15):
                with open(os.path.join(tmpdir, f"file{i}.txt"), 'w') as f:
                    f.write(f"content {i}")

            score = scorer._score_file_activity(tmpdir)
            assert score >= 5, f"Expected ≥5 with many files, got {score}"

            # Add source code files
            with open(os.path.join(tmpdir, "main.py"), 'w') as f:
                f.write("print('hello')")

            with open(os.path.join(tmpdir, "app.js"), 'w') as f:
                f.write("console.log('hello')")

            score = scorer._score_file_activity(tmpdir)
            assert score >= 10, f"Expected ≥10 with source files, got {score}"

        print("✓ File activity scoring tests passed")

    @staticmethod
    def test_project_structure_scoring():
        """Test project structure scoring"""
        print("Testing project structure scoring...")

        with tempfile.TemporaryDirectory() as tmpdir:
            scorer = DirectoryScorer()

            # Test empty directory
            score = scorer._score_project_structure(tmpdir, None)
            assert score == 0, f"Expected 0 for empty directory, got {score}"

            # Add standard directories
            for dirname in ["src", "test", "docs"]:
                os.makedirs(os.path.join(tmpdir, dirname))

            score = scorer._score_project_structure(tmpdir, None)
            assert score >= 6, f"Expected ≥6 with standard directories, got {score}"

            # Add CI/CD configuration
            os.makedirs(os.path.join(tmpdir, ".github"))

            score = scorer._score_project_structure(tmpdir, None)
            assert score >= 11, f"Expected ≥11 with CI/CD, got {score}"

        print("✓ Project structure scoring tests passed")

    @staticmethod
    def test_project_type_detection():
        """Test project type detection"""
        print("Testing project type detection...")

        with tempfile.TemporaryDirectory() as tmpdir:
            scorer = DirectoryScorer()

            # Test unknown type
            project_type = scorer._detect_project_type(tmpdir)
            assert project_type is None, f"Expected None for empty directory, got {project_type}"

            # Test Node.js project
            with open(os.path.join(tmpdir, "package.json"), 'w') as f:
                f.write('{}')

            project_type = scorer._detect_project_type(tmpdir)
            assert project_type == "node", f"Expected 'node', got {project_type}"

            # Remove package.json and test Python project
            os.remove(os.path.join(tmpdir, "package.json"))
            with open(os.path.join(tmpdir, "requirements.txt"), 'w') as f:
                f.write('')

            project_type = scorer._detect_project_type(tmpdir)
            assert project_type == "python", f"Expected 'python', got {project_type}"

        print("✓ Project type detection tests passed")

    @staticmethod
    def test_protected_paths():
        """Test protected path detection"""
        print("Testing protected path detection...")

        scorer = DirectoryScorer()

        # Test protected paths
        assert scorer._is_protected("/path/to/.git"), ".git should be protected"
        assert scorer._is_protected("/path/to/node_modules"), "node_modules should be protected"
        assert scorer._is_protected("/path/to/.venv"), ".venv should be protected"

        # Test non-protected paths
        assert not scorer._is_protected("/path/to/project"), "Regular path should not be protected"
        assert not scorer._is_protected("/path/to/src"), "src should not be protected"

        print("✓ Protected path tests passed")

    @staticmethod
    def test_classification_thresholds():
        """Test classification threshold logic"""
        print("Testing classification thresholds...")

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a highly active project
            TestDirectoryScorer.setup_test_directory(tmpdir, {
                "README.md": "# Active Project",
                "package.json": "{}",
                "package-lock.json": "{}",
                "src": {
                    "main.js": "console.log('hello');",
                    "utils.js": "export const util = () => {};"
                },
                "test": {
                    "main.test.js": "test('main', () => {});"
                },
                "docs": {
                    "api.md": "# API"
                }
            })

            scorer = DirectoryScorer()
            score = scorer.score_directory(tmpdir)

            assert score.classification == "Active", f"Expected Active, got {score.classification}"
            assert score.total_score >= 20, f"Expected score ≥20, got {score.total_score}"

        # Test borderline directory
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create minimal structure
            TestDirectoryScorer.setup_test_directory(tmpdir, {
                "README.md": "# Borderline Project"
            })

            score = scorer.score_directory(tmpdir)
            assert score.classification in ["Borderline", "Active"], \
                f"Expected Borderline or Active, got {score.classification}"

        print("✓ Classification threshold tests passed")

    @staticmethod
    def test_batch_processing():
        """Test batch directory scoring"""
        print("Testing batch processing...")

        with tempfile.TemporaryDirectory() as tmpbase:
            # Create multiple test directories
            dirs = []
            for i in range(3):
                dirname = os.path.join(tmpbase, f"project{i}")
                os.makedirs(dirname)

                TestDirectoryScorer.setup_test_directory(dirname, {
                    "README.md": f"# Project {i}",
                    "package.json": "{}"
                })

                dirs.append(dirname)

            scorer = DirectoryScorer()
            scores = scorer.score_batch(dirs)

            assert len(scores) == 3, f"Expected 3 scores, got {len(scores)}"

            for score in scores:
                assert isinstance(score, DirectoryScore), "Expected DirectoryScore objects"
                assert score.total_score >= 0, "Expected non-negative scores"

        print("✓ Batch processing tests passed")

    @staticmethod
    def test_export_formats():
        """Test export format functions"""
        print("Testing export formats...")

        with tempfile.TemporaryDirectory() as tmpdir:
            TestDirectoryScorer.setup_test_directory(tmpdir, {
                "README.md": "# Test",
                "package.json": "{}"
            })

            scorer = DirectoryScorer()
            score = scorer.score_directory(tmpdir)

            # Test JSON export
            json_output = scorer.export_results([score], "json")
            json_data = json.loads(json_output)
            assert len(json_data) == 1, "Expected 1 score in JSON"
            assert "total_score" in json_data[0], "Missing total_score in JSON"

            # Test CSV export
            csv_output = scorer.export_results([score], "csv")
            lines = csv_output.strip().split("\n")
            assert len(lines) == 2, f"Expected 2 lines in CSV (header + data), got {len(lines)}"
            assert "Path" in lines[0], "Missing header in CSV"

            # Test Markdown export
            md_output = scorer.export_results([score], "markdown")
            assert "# Directory Activity Scores" in md_output, "Missing markdown header"
            assert "|" in md_output, "Missing table formatting"

        print("✓ Export format tests passed")

    @staticmethod
    def test_error_handling():
        """Test error handling for edge cases"""
        print("Testing error handling...")

        scorer = DirectoryScorer()

        # Test non-existent directory
        try:
            scorer.score_directory("/nonexistent/path")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "not a directory" in str(e).lower()

        # Test file instead of directory
        with tempfile.NamedTemporaryFile() as tmpfile:
            try:
                scorer.score_directory(tmpfile.name)
                assert False, "Should have raised ValueError"
            except ValueError as e:
                assert "not a directory" in str(e).lower()

        print("✓ Error handling tests passed")

    @staticmethod
    def test_complete_workflow():
        """Test complete scoring workflow"""
        print("Testing complete workflow...")

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a realistic project structure
            TestDirectoryScorer.setup_test_directory(tmpdir, {
                "README.md": "# Test Project\n\nA test project for scoring.",
                "LICENSE": "MIT License",
                "package.json": '{"name": "test", "version": "1.0.0"}',
                "package-lock.json": "{}",
                "src": {
                    "index.js": "const app = require('./app');\napp.start();",
                    "app.js": "module.exports = { start: () => {} };",
                    "utils.js": "module.exports = { helper: () => {} };"
                },
                "test": {
                    "app.test.js": "test('app', () => {});"
                },
                "docs": {
                    "api.md": "# API Documentation",
                    "guide.md": "# User Guide"
                },
                ".github": {
                    "workflows": {
                        "ci.yml": "name: CI"
                    }
                }
            })

            # Initialize git repository
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmpdir)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmpdir)
            subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Initial"], cwd=tmpdir, capture_output=True)

            scorer = DirectoryScorer()
            score = scorer.score_directory(tmpdir)

            # Validate comprehensive scoring
            assert score.classification == "Active", \
                f"Well-structured project should be Active, got {score.classification}"
            assert score.project_type == "node", \
                f"Should detect node project, got {score.project_type}"
            assert score.total_score >= 40, \
                f"Expected high score for complete project, got {score.total_score}"

            # Check all factors were evaluated
            expected_factors = [
                "time_decay", "git_activity", "dependencies",
                "documentation", "file_activity", "project_structure"
            ]

            for factor in expected_factors:
                assert factor in score.factors, f"Missing factor: {factor}"
                # Some factors may be 0 in specific cases (e.g., no hidden files in test setup)
                assert score.factors[factor] >= 0, f"Factor {factor} should have non-negative score"

        print("✓ Complete workflow test passed")


def run_all_tests():
    """Run all test cases"""
    print("="*70)
    print("Running Directory Scoring Test Suite")
    print("="*70)
    print()

    tests = [
        TestDirectoryScorer.test_time_decay_scoring,
        TestDirectoryScorer.test_git_activity_scoring,
        TestDirectoryScorer.test_dependency_scoring,
        TestDirectoryScorer.test_documentation_scoring,
        TestDirectoryScorer.test_file_activity_scoring,
        TestDirectoryScorer.test_project_structure_scoring,
        TestDirectoryScorer.test_project_type_detection,
        TestDirectoryScorer.test_protected_paths,
        TestDirectoryScorer.test_classification_thresholds,
        TestDirectoryScorer.test_batch_processing,
        TestDirectoryScorer.test_export_formats,
        TestDirectoryScorer.test_error_handling,
        TestDirectoryScorer.test_complete_workflow
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"✗ {test.__name__} FAILED: {e}")
            import traceback
            traceback.print_exc()

    print()
    print("="*70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*70)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
