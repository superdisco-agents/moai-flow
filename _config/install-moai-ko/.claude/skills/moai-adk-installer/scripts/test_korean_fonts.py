#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11,<3.15"
# dependencies = [
#     "click>=8.1.0",
# ]
# ///

"""
MoAI-ADK Korean Font Testing

Tests Korean character rendering and font configuration:
1. Test Korean character rendering
2. Verify D2Coding font installation
3. Check Ghostty configuration
4. Test CJK character display
5. Validate UTF-8 encoding

Usage:
    uv run test_korean_fonts.py
    uv run test_korean_fonts.py --verbose
    uv run test_korean_fonts.py --json
"""

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import click


class KoreanFontTester:
    """Korean font rendering and configuration tester."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: Dict[str, dict] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.is_macos = platform.system() == "Darwin"

    def _run_command(self, cmd: List[str]) -> Tuple[bool, str, str]:
        """Execute command and return success status, stdout, stderr."""
        try:
            if self.verbose:
                print(f"Running: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
            )

            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()

        except Exception as e:
            return False, "", str(e)

    def test_korean_rendering(self) -> dict:
        """Test 1: Korean character rendering."""
        result = {
            "test": 1,
            "name": "Korean Character Rendering",
            "status": "pending",
            "details": {},
        }

        try:
            # Test strings with various Korean characters
            test_cases = {
                "basic_greeting": {
                    "text": "안녕하세요",
                    "description": "Hello (basic hangul)",
                },
                "mixed_content": {
                    "text": "MoAI-ADK 한글 테스트",
                    "description": "Mixed Korean-English",
                },
                "numbers": {
                    "text": "테스트 123 번호",
                    "description": "Korean with numbers",
                },
                "special_chars": {
                    "text": "특수문자!@#$%^&*()",
                    "description": "Special characters",
                },
                "long_text": {
                    "text": "인공지능 개발 도구키트",
                    "description": "AI Development Toolkit (longer text)",
                },
            }

            passed_tests = []
            failed_tests = []

            for test_name, test_data in test_cases.items():
                text = test_data["text"]
                description = test_data["description"]

                try:
                    # Test UTF-8 encoding/decoding
                    encoded = text.encode("utf-8")
                    decoded = encoded.decode("utf-8")

                    if decoded == text:
                        passed_tests.append({
                            "name": test_name,
                            "text": text,
                            "description": description,
                            "status": "passed",
                        })

                        if self.verbose:
                            print(f"✓ {description}: {text}")
                    else:
                        failed_tests.append({
                            "name": test_name,
                            "text": text,
                            "description": description,
                            "status": "failed",
                            "error": "Encoding mismatch",
                        })

                        if self.verbose:
                            print(f"✗ {description}: Encoding failed")

                except UnicodeEncodeError as e:
                    failed_tests.append({
                        "name": test_name,
                        "text": text,
                        "description": description,
                        "status": "failed",
                        "error": str(e),
                    })

                    if self.verbose:
                        print(f"✗ {description}: {e}")

            result["details"]["passed"] = passed_tests
            result["details"]["failed"] = failed_tests
            result["details"]["total_tests"] = len(test_cases)
            result["details"]["passed_count"] = len(passed_tests)
            result["details"]["failed_count"] = len(failed_tests)

            if len(passed_tests) == len(test_cases):
                result["status"] = "passed"
            elif len(passed_tests) > 0:
                result["status"] = "partial"
                self.warnings.append(
                    f"Some Korean character tests failed: {len(failed_tests)}/{len(test_cases)}"
                )
            else:
                result["status"] = "failed"
                self.errors.append("All Korean character tests failed")

        except Exception as e:
            result["status"] = "failed"
            result["details"]["error"] = str(e)
            self.errors.append(f"Korean rendering test failed: {e}")

        self.results["rendering"] = result
        return result

    def verify_d2coding_font(self) -> dict:
        """Test 2: Verify D2Coding font installation."""
        result = {
            "test": 2,
            "name": "D2Coding Font Installation",
            "status": "pending",
            "details": {},
        }

        try:
            if not self.is_macos:
                result["status"] = "skipped"
                result["details"]["reason"] = "Only supported on macOS"
                result["details"]["recommendation"] = (
                    "On Linux, check manually: fc-list | grep D2Coding"
                )
                self.results["d2coding"] = result
                return result

            # Check via Homebrew
            success, stdout, stderr = self._run_command(
                ["brew", "list", "--cask", "font-d2coding"]
            )

            if success:
                result["status"] = "passed"
                result["details"]["installed"] = True
                result["details"]["installation_method"] = "Homebrew Cask"

                if self.verbose:
                    print("✓ D2Coding font is installed via Homebrew")
            else:
                # Check via system fonts (alternative method)
                success_fc, stdout_fc, _ = self._run_command(
                    ["fc-list", ":", "family"]
                )

                if success_fc and "D2Coding" in stdout_fc:
                    result["status"] = "passed"
                    result["details"]["installed"] = True
                    result["details"]["installation_method"] = "System fonts"

                    if self.verbose:
                        print("✓ D2Coding font found in system fonts")
                else:
                    result["status"] = "failed"
                    result["details"]["installed"] = False
                    result["details"]["error"] = "D2Coding font not found"
                    self.errors.append(
                        "D2Coding font not installed. Run: brew install --cask font-d2coding"
                    )

        except Exception as e:
            result["status"] = "failed"
            result["details"]["error"] = str(e)
            self.errors.append(f"D2Coding font verification failed: {e}")

        self.results["d2coding"] = result
        return result

    def check_ghostty_config(self) -> dict:
        """Test 3: Check Ghostty terminal configuration."""
        result = {
            "test": 3,
            "name": "Ghostty Configuration",
            "status": "pending",
            "details": {},
        }

        try:
            # Check if Ghostty is installed
            ghostty_path = shutil.which("ghostty")
            result["details"]["ghostty_installed"] = ghostty_path is not None

            if ghostty_path:
                result["details"]["ghostty_path"] = ghostty_path

            # Check configuration file
            config_file = Path.home() / ".config" / "ghostty" / "config"
            result["details"]["config_exists"] = config_file.exists()

            if not config_file.exists():
                result["status"] = "warning"
                result["details"]["warning"] = "Ghostty config file not found"
                self.warnings.append(
                    "Ghostty configuration file not found. Run: uv run configure_korean.py"
                )
                self.results["ghostty_config"] = result
                return result

            # Read and analyze configuration
            with open(config_file, "r", encoding="utf-8") as f:
                config_content = f.read()

            # Check for Korean-specific settings
            checks = {
                "d2coding_font": "D2Coding" in config_content,
                "utf8_locale": "UTF-8" in config_content,
                "korean_comment": "Korean" in config_content,
            }

            result["details"]["configuration_checks"] = checks
            result["details"]["all_checks_passed"] = all(checks.values())

            if all(checks.values()):
                result["status"] = "passed"

                if self.verbose:
                    print("✓ Ghostty is properly configured for Korean")
            elif any(checks.values()):
                result["status"] = "partial"
                result["details"]["warning"] = "Partial Korean configuration"
                self.warnings.append(
                    "Ghostty is partially configured. Run: uv run configure_korean.py"
                )
            else:
                result["status"] = "failed"
                result["details"]["error"] = "Ghostty not configured for Korean"
                self.errors.append(
                    "Ghostty is not configured for Korean. Run: uv run configure_korean.py"
                )

        except Exception as e:
            result["status"] = "failed"
            result["details"]["error"] = str(e)
            self.errors.append(f"Ghostty configuration check failed: {e}")

        self.results["ghostty_config"] = result
        return result

    def test_cjk_characters(self) -> dict:
        """Test 4: Test CJK (Chinese, Japanese, Korean) character display."""
        result = {
            "test": 4,
            "name": "CJK Character Display",
            "status": "pending",
            "details": {},
        }

        try:
            # Test CJK character ranges
            cjk_tests = {
                "korean": {
                    "chars": "한글 韓國語",
                    "description": "Korean (Hangul and Hanja)",
                },
                "japanese": {
                    "chars": "日本語 ひらがな カタカナ",
                    "description": "Japanese (Kanji, Hiragana, Katakana)",
                },
                "chinese_simplified": {
                    "chars": "简体中文",
                    "description": "Simplified Chinese",
                },
                "chinese_traditional": {
                    "chars": "繁體中文",
                    "description": "Traditional Chinese",
                },
            }

            passed = []
            failed = []

            for lang, data in cjk_tests.items():
                chars = data["chars"]
                description = data["description"]

                try:
                    encoded = chars.encode("utf-8")
                    decoded = encoded.decode("utf-8")

                    if decoded == chars:
                        passed.append({
                            "language": lang,
                            "characters": chars,
                            "description": description,
                            "status": "passed",
                        })

                        if self.verbose:
                            print(f"✓ {description}: {chars}")
                    else:
                        failed.append({
                            "language": lang,
                            "characters": chars,
                            "description": description,
                            "status": "failed",
                        })

                except UnicodeEncodeError as e:
                    failed.append({
                        "language": lang,
                        "characters": chars,
                        "description": description,
                        "status": "failed",
                        "error": str(e),
                    })

            result["details"]["passed"] = passed
            result["details"]["failed"] = failed
            result["details"]["passed_count"] = len(passed)
            result["details"]["failed_count"] = len(failed)

            if len(passed) == len(cjk_tests):
                result["status"] = "passed"
            elif len(passed) > 0:
                result["status"] = "partial"
                self.warnings.append(f"Some CJK tests failed: {len(failed)}/{len(cjk_tests)}")
            else:
                result["status"] = "failed"
                self.errors.append("All CJK character tests failed")

        except Exception as e:
            result["status"] = "failed"
            result["details"]["error"] = str(e)
            self.errors.append(f"CJK character test failed: {e}")

        self.results["cjk"] = result
        return result

    def validate_utf8_encoding(self) -> dict:
        """Test 5: Validate UTF-8 encoding support."""
        result = {
            "test": 5,
            "name": "UTF-8 Encoding Support",
            "status": "pending",
            "details": {},
        }

        try:
            # Check system locale
            success, locale_output, _ = self._run_command(["locale"])

            result["details"]["locale_output"] = locale_output

            # Check for UTF-8 in locale
            has_utf8 = "UTF-8" in locale_output or "utf8" in locale_output
            result["details"]["utf8_in_locale"] = has_utf8

            # Check default encoding
            default_encoding = sys.getdefaultencoding()
            result["details"]["default_encoding"] = default_encoding
            result["details"]["is_utf8"] = default_encoding.lower() == "utf-8"

            # Check filesystem encoding
            fs_encoding = sys.getfilesystemencoding()
            result["details"]["filesystem_encoding"] = fs_encoding
            result["details"]["fs_is_utf8"] = fs_encoding.lower() == "utf-8"

            # Test encoding/decoding
            test_string = "테스트 한글 UTF-8"
            try:
                encoded = test_string.encode("utf-8")
                decoded = encoded.decode("utf-8")
                encoding_works = decoded == test_string
                result["details"]["encoding_test"] = "passed" if encoding_works else "failed"
            except Exception as e:
                result["details"]["encoding_test"] = f"failed: {e}"
                encoding_works = False

            # Overall status
            all_checks_passed = (
                has_utf8 and
                default_encoding.lower() == "utf-8" and
                encoding_works
            )

            if all_checks_passed:
                result["status"] = "passed"

                if self.verbose:
                    print("✓ UTF-8 encoding is properly supported")
            else:
                result["status"] = "warning"
                result["details"]["warning"] = "UTF-8 support is partial or incomplete"
                self.warnings.append(
                    "UTF-8 encoding may not be fully supported. "
                    "Set LANG=en_US.UTF-8 in shell profile."
                )

        except Exception as e:
            result["status"] = "failed"
            result["details"]["error"] = str(e)
            self.errors.append(f"UTF-8 encoding validation failed: {e}")

        self.results["utf8"] = result
        return result

    def run_all_tests(self) -> dict:
        """Run all Korean font tests."""
        if self.verbose:
            print("🔍 Testing Korean font support...\n")

        self.test_korean_rendering()
        self.verify_d2coding_font()
        self.check_ghostty_config()
        self.test_cjk_characters()
        self.validate_utf8_encoding()

        # Calculate overall status
        passed_count = len([r for r in self.results.values() if r.get("status") == "passed"])
        total_count = len(self.results)

        percentage = (passed_count / total_count) * 100 if total_count > 0 else 0

        if percentage >= 90:
            overall_status = "EXCELLENT"
        elif percentage >= 70:
            overall_status = "GOOD"
        elif percentage >= 50:
            overall_status = "FAIR"
        else:
            overall_status = "POOR"

        summary = {
            "overall_status": overall_status,
            "tests_passed": passed_count,
            "tests_total": total_count,
            "percentage": round(percentage, 1),
            "errors": self.errors,
            "warnings": self.warnings,
            "results": self.results,
        }

        return summary


def print_human_readable(summary: dict, verbose: bool = False):
    """Print human-readable test summary."""
    print("\n" + "=" * 70)
    print("Korean Font Testing Results")
    print("=" * 70 + "\n")

    # Print test results
    for key, result in summary["results"].items():
        status = result.get("status", "unknown")
        status_emoji = {
            "passed": "✓",
            "partial": "◐",
            "skipped": "⊙",
            "warning": "⚠",
            "failed": "✗",
        }.get(status, "?")

        test_num = result.get("test", "?")
        name = result.get("name", key)

        print(f"{status_emoji} Test {test_num}: {name} - {status.upper()}")

        if verbose and "details" in result:
            print(f"  Details: {json.dumps(result['details'], indent=4, ensure_ascii=False)}")
        print()

    # Print summary
    print("=" * 70)
    print(f"Overall Status: {summary['overall_status']}")
    print(f"Tests Passed: {summary['tests_passed']}/{summary['tests_total']} ({summary['percentage']}%)")
    print("=" * 70 + "\n")

    # Print errors
    if summary["errors"]:
        print("❌ ERRORS:")
        for error in summary["errors"]:
            print(f"  • {error}")
        print()

    # Print warnings
    if summary["warnings"]:
        print("⚠️  WARNINGS:")
        for warning in summary["warnings"]:
            print(f"  • {warning}")
        print()

    # Print visual test
    print("\n" + "=" * 70)
    print("Visual Korean Font Test")
    print("=" * 70)
    print("\nIf you can read these Korean characters clearly, fonts are working:\n")
    print("  안녕하세요 (Hello)")
    print("  MoAI-ADK 한글 지원 (MoAI-ADK Korean Support)")
    print("  인공지능 개발 도구 (AI Development Tools)")
    print("\n" + "=" * 70 + "\n")


@click.command()
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output with detailed information",
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output results in JSON format",
)
@click.option(
    "--help",
    "-h",
    "show_help",
    is_flag=True,
    help="Show this help message and exit",
)
def main(verbose: bool, output_json: bool, show_help: bool):
    """
    Test Korean font rendering and configuration.

    Tests:
    1. Korean character rendering
    2. D2Coding font installation
    3. Ghostty terminal configuration
    4. CJK character display
    5. UTF-8 encoding support

    Examples:
        uv run test_korean_fonts.py
        uv run test_korean_fonts.py --verbose
        uv run test_korean_fonts.py --json
    """
    if show_help:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        return

    tester = KoreanFontTester(verbose=verbose)
    summary = tester.run_all_tests()

    if output_json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print_human_readable(summary, verbose=verbose)

    # Exit with warning code if tests are not excellent
    if summary["percentage"] < 70:
        sys.exit(1)


if __name__ == "__main__":
    main()
