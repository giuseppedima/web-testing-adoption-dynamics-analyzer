"""
Command Line Interface for Statistical Analysis module.
Provides easy access to plot generation and statistics.
"""
import argparse
import sys
from pathlib import Path

# Add current directory to path for imports
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

from statisticsGenerator import StatisticsGenerator
from commitStatisticsGenerator import CommitStatisticsGenerator
from issueStatisticsGenerator import IssueStatisticsGenerator


def generate_all_plots():
    """Generate all statistical plots."""
    stats = StatisticsGenerator()
    
    plots = [
        ('Adoption by Framework', stats.adoption_counts_by_framework),
        ('Migration Directed Graph', stats.migration_directed_graph),
        ('Migration Sankey Diagram', stats.migration_sankey_diagram),
        ('Motivation Category Distribution', stats.motivation_category_distribution),
        ('Grouped Bar Chart Motivation', stats.grouped_bar_chart_motivation_category),
        ('Playwright Migration Sources', stats.playwright_migration_sources),
        ('Adoption vs Migration Distribution', stats.generate_side_by_side_pie_charts),
        ('Target Framework by Language', stats.target_framework_by_language),
        ('Transitions Timeline', stats.transitions_timeline_scatter),
        ('Commit Statistics', CommitStatisticsGenerator.generate_side_by_side_pie_charts),
        ('Issue Statistics', IssueStatisticsGenerator.generate_bar_chart_issues),
        ('Filtering Funnel', IssueStatisticsGenerator.create_filtering_funnel)
    ]
    
    print("Generating all plots...\n")
    for desc, func in plots:
        try:
            print(f"  - {desc}...")
            func()
        except Exception as e:
            print(f"    ✗ Error: {e}")
    
    print("\n✓ All plots generated successfully")


def show_counts():
    """Display count statistics."""
    print("\n=== Repository Counts ===")
    total_repos = StatisticsGenerator.get_all_repositories_count()
    print(f"Total repositories: {total_repos}")
    
    print("\n=== Commit Counts ===")
    prev_adoption, adoption, prev_migration, migration = CommitStatisticsGenerator.get_all_commits_count()
    print(f"Adoption commits: {adoption}")
    print(f"Additional adoption commits: {prev_adoption}")
    print(f"Migration commits: {migration}")
    print(f"Additional migration commits: {prev_migration}")
    
    adoption_filtered, migration_filtered = CommitStatisticsGenerator.get_commits_after_filtering_count()
    print(f"\nAfter filtering:")
    print(f"  Adoption: {adoption_filtered}")
    print(f"  Migration: {migration_filtered}")
    
    adoption_labeled, migration_labeled = CommitStatisticsGenerator.get_commits_after_labeling_count()
    print(f"\nAfter labeling:")
    print(f"  Adoption: {adoption_labeled}")
    print(f"  Migration: {migration_labeled}")
    
    print("\n=== Issue Counts ===")
    open_issues, closed_issues = IssueStatisticsGenerator.get_issues_count()
    print(f"Open issues: {open_issues}")
    print(f"Closed issues: {closed_issues}")
    print(f"Total issues: {open_issues + closed_issues}")
    
    adoption_filtered, migration_filtered = IssueStatisticsGenerator.get_issues_after_filtering_count()
    print(f"\nAfter filtering:")
    print(f"  Adoption: {adoption_filtered}")
    print(f"  Migration: {migration_filtered}")
    
    adoption_labeled, migration_labeled = IssueStatisticsGenerator.get_issues_after_labeling_count()
    print(f"\nAfter labeling:")
    print(f"  Adoption: {adoption_labeled}")
    print(f"  Migration: {migration_labeled}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Statistical Analysis CLI for E2E Testing Framework Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all plots
  python -m 04_statistical_analysis.cli
        """
    )
    
    args = parser.parse_args()
    
    try:
        generate_all_plots()
    
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
