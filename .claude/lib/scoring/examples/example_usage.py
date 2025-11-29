#!/usr/bin/env python3
"""
Example usage scripts for directory activity scoring

This file demonstrates various use cases and integration patterns
for the directory scoring algorithm.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scoring import DirectoryScorer, ScoringConfig


def example_basic_scoring():
    """Example 1: Basic directory scoring"""
    print("="*70)
    print("Example 1: Basic Directory Scoring")
    print("="*70)

    scorer = DirectoryScorer()

    # Score current directory
    score = scorer.score_directory(".")

    print(f"\nDirectory: {score.path}")
    print(f"Score: {score.total_score}")
    print(f"Classification: {score.classification}")
    print(f"Project Type: {score.project_type or 'Unknown'}")
    print(f"Protected: {score.protected}")

    print("\nFactor Breakdown:")
    for factor, value in score.factors.items():
        print(f"  {factor:20s}: {value:.2f}")


def example_custom_config():
    """Example 2: Custom configuration"""
    print("\n" + "="*70)
    print("Example 2: Custom Configuration")
    print("="*70)

    # Create custom config
    config = ScoringConfig()

    # Adjust thresholds
    config.ACTIVE_THRESHOLD = 25
    config.BORDERLINE_THRESHOLD = 5

    # Adjust weights - emphasize git activity
    config.WEIGHTS["git_activity"] = 3.0
    config.WEIGHTS["documentation"] = 0.5

    # Add custom protected paths
    config.PROTECTED_PATHS.append("my_special_dir")

    print("\nCustom Configuration:")
    print(f"  Active Threshold: {config.ACTIVE_THRESHOLD}")
    print(f"  Borderline Threshold: {config.BORDERLINE_THRESHOLD}")
    print(f"  Git Activity Weight: {config.WEIGHTS['git_activity']}")

    # Score with custom config
    scorer = DirectoryScorer(config)
    score = scorer.score_directory(".")

    print(f"\nScore with custom config: {score.total_score}")
    print(f"Classification: {score.classification}")


def example_batch_scoring():
    """Example 3: Batch scoring multiple directories"""
    print("\n" + "="*70)
    print("Example 3: Batch Scoring")
    print("="*70)

    scorer = DirectoryScorer()

    # Get all subdirectories
    current_dir = Path(".")
    subdirs = [str(d) for d in current_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]

    if not subdirs:
        print("\nNo subdirectories found in current directory")
        return

    # Score all subdirectories
    scores = scorer.score_batch(subdirs[:5])  # Limit to first 5 for demo

    print(f"\nScored {len(scores)} directories:")
    print(f"\n{'Directory':<30} {'Score':>10} {'Classification':>15}")
    print("-"*70)

    for score in scores:
        dir_name = Path(score.path).name
        print(f"{dir_name:<30} {score.total_score:>10.2f} {score.classification:>15}")


def example_export_formats():
    """Example 4: Exporting in different formats"""
    print("\n" + "="*70)
    print("Example 4: Export Formats")
    print("="*70)

    scorer = DirectoryScorer()
    score = scorer.score_directory(".")

    # JSON export
    print("\nJSON Format:")
    print("-"*70)
    json_output = scorer.export_results([score], "json")
    print(json_output[:200] + "..." if len(json_output) > 200 else json_output)

    # CSV export
    print("\n\nCSV Format:")
    print("-"*70)
    csv_output = scorer.export_results([score], "csv")
    print(csv_output)

    # Markdown export
    print("\n\nMarkdown Format:")
    print("-"*70)
    md_output = scorer.export_results([score], "markdown")
    print(md_output)


def example_find_archivable():
    """Example 5: Find archivable directories"""
    print("\n" + "="*70)
    print("Example 5: Find Archivable Directories")
    print("="*70)

    scorer = DirectoryScorer()
    current_dir = Path(".")

    archivable = []
    borderline = []
    active = []

    # Score all subdirectories
    for dir_path in current_dir.iterdir():
        if not dir_path.is_dir() or dir_path.name.startswith("."):
            continue

        try:
            score = scorer.score_directory(str(dir_path))

            if score.classification == "Archivable":
                archivable.append((dir_path.name, score.total_score))
            elif score.classification == "Borderline":
                borderline.append((dir_path.name, score.total_score))
            else:
                active.append((dir_path.name, score.total_score))
        except Exception as e:
            print(f"Error scoring {dir_path}: {e}")

    print(f"\nActive Directories ({len(active)}):")
    for name, score in sorted(active, key=lambda x: x[1], reverse=True):
        print(f"  {name:30s} (score: {score:.2f})")

    print(f"\nBorderline Directories ({len(borderline)}):")
    for name, score in sorted(borderline, key=lambda x: x[1], reverse=True):
        print(f"  {name:30s} (score: {score:.2f})")

    print(f"\nArchivable Directories ({len(archivable)}):")
    for name, score in sorted(archivable, key=lambda x: x[1]):
        print(f"  {name:30s} (score: {score:.2f})")


def example_detailed_analysis():
    """Example 6: Detailed factor analysis"""
    print("\n" + "="*70)
    print("Example 6: Detailed Factor Analysis")
    print("="*70)

    scorer = DirectoryScorer()
    score = scorer.score_directory(".")

    config = scorer.config

    print(f"\nDirectory: {score.path}")
    print(f"Total Score: {score.total_score}")
    print(f"Classification: {score.classification}")

    print("\nDetailed Factor Breakdown:")
    print(f"{'Factor':<25} {'Raw Score':>12} {'Weight':>10} {'Weighted':>12} {'%':>10}")
    print("-"*70)

    total_weighted = sum(score.factors[f] * config.WEIGHTS[f] for f in score.factors)

    for factor, raw_score in sorted(score.factors.items(), key=lambda x: x[1], reverse=True):
        weight = config.WEIGHTS[factor]
        weighted = raw_score * weight
        percentage = (weighted / total_weighted * 100) if total_weighted > 0 else 0

        print(f"{factor:<25} {raw_score:>12.2f} {weight:>10.1f} {weighted:>12.2f} {percentage:>9.1f}%")

    print("-"*70)
    print(f"{'Total':<25} {'':<12} {'':<10} {total_weighted:>12.2f} {'100.0%':>10}")


def example_workspace_audit():
    """Example 7: Workspace audit report"""
    print("\n" + "="*70)
    print("Example 7: Workspace Audit Report")
    print("="*70)

    scorer = DirectoryScorer()
    current_dir = Path(".")

    print(f"\nWorkspace: {current_dir.absolute()}")

    # Score all subdirectories
    all_scores = []
    for dir_path in current_dir.iterdir():
        if not dir_path.is_dir() or dir_path.name.startswith("."):
            continue

        try:
            score = scorer.score_directory(str(dir_path))
            all_scores.append(score)
        except Exception as e:
            print(f"Warning: Could not score {dir_path}: {e}")

    if not all_scores:
        print("\nNo directories found to score")
        return

    # Calculate statistics
    total_dirs = len(all_scores)
    active_count = sum(1 for s in all_scores if s.classification == "Active")
    borderline_count = sum(1 for s in all_scores if s.classification == "Borderline")
    archivable_count = sum(1 for s in all_scores if s.classification == "Archivable")
    protected_count = sum(1 for s in all_scores if s.protected)

    avg_score = sum(s.total_score for s in all_scores) / total_dirs

    # Project type distribution
    project_types = {}
    for score in all_scores:
        ptype = score.project_type or "unknown"
        project_types[ptype] = project_types.get(ptype, 0) + 1

    print(f"\nSummary:")
    print(f"  Total Directories: {total_dirs}")
    print(f"  Active: {active_count} ({active_count/total_dirs*100:.1f}%)")
    print(f"  Borderline: {borderline_count} ({borderline_count/total_dirs*100:.1f}%)")
    print(f"  Archivable: {archivable_count} ({archivable_count/total_dirs*100:.1f}%)")
    print(f"  Protected: {protected_count}")
    print(f"  Average Score: {avg_score:.2f}")

    print(f"\nProject Types:")
    for ptype, count in sorted(project_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {ptype:15s}: {count:3d} ({count/total_dirs*100:.1f}%)")

    print(f"\nTop 5 Most Active:")
    for score in sorted(all_scores, key=lambda x: x.total_score, reverse=True)[:5]:
        dir_name = Path(score.path).name
        print(f"  {dir_name:30s} {score.total_score:>10.2f}")

    print(f"\nRecommendations:")
    if archivable_count > 0:
        print(f"  - Review {archivable_count} archivable director{'y' if archivable_count == 1 else 'ies'} for cleanup")
    if borderline_count > 0:
        print(f"  - Assess {borderline_count} borderline director{'y' if borderline_count == 1 else 'ies'} for relevance")
    if active_count / total_dirs < 0.5:
        print(f"  - Consider workspace cleanup: only {active_count/total_dirs*100:.1f}% of directories are active")


def example_comparison():
    """Example 8: Compare scoring configurations"""
    print("\n" + "="*70)
    print("Example 8: Configuration Comparison")
    print("="*70)

    # Default config
    default_scorer = DirectoryScorer()

    # Git-focused config
    git_config = ScoringConfig()
    git_config.WEIGHTS["git_activity"] = 4.0
    git_config.WEIGHTS["documentation"] = 0.5
    git_scorer = DirectoryScorer(git_config)

    # Documentation-focused config
    doc_config = ScoringConfig()
    doc_config.WEIGHTS["documentation"] = 3.0
    doc_config.WEIGHTS["git_activity"] = 1.0
    doc_scorer = DirectoryScorer(doc_config)

    # Score with each config
    default_score = default_scorer.score_directory(".")
    git_score = git_scorer.score_directory(".")
    doc_score = doc_scorer.score_directory(".")

    print(f"\nDirectory: .")
    print(f"\n{'Config':<20} {'Total Score':>15} {'Classification':>20}")
    print("-"*70)
    print(f"{'Default':<20} {default_score.total_score:>15.2f} {default_score.classification:>20}")
    print(f"{'Git-Focused':<20} {git_score.total_score:>15.2f} {git_score.classification:>20}")
    print(f"{'Doc-Focused':<20} {doc_score.total_score:>15.2f} {doc_score.classification:>20}")

    print(f"\nFactor Comparison:")
    print(f"{'Factor':<20} {'Default':>12} {'Git-Focused':>15} {'Doc-Focused':>15}")
    print("-"*70)

    for factor in default_score.factors.keys():
        default_val = default_score.factors[factor]
        git_val = git_score.factors[factor]
        doc_val = doc_score.factors[factor]

        print(f"{factor:<20} {default_val:>12.2f} {git_val:>15.2f} {doc_val:>15.2f}")


def main():
    """Run all examples"""
    print("\nDirectory Activity Scoring - Example Usage")
    print("="*70)

    examples = [
        ("Basic Scoring", example_basic_scoring),
        ("Custom Configuration", example_custom_config),
        ("Batch Scoring", example_batch_scoring),
        ("Export Formats", example_export_formats),
        ("Find Archivable", example_find_archivable),
        ("Detailed Analysis", example_detailed_analysis),
        ("Workspace Audit", example_workspace_audit),
        ("Configuration Comparison", example_comparison)
    ]

    print("\nAvailable Examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\nRunning all examples...\n")

    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\nError in {name}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*70)
    print("Examples completed!")
    print("="*70)


if __name__ == "__main__":
    main()
