"""
Command Line Interface for Data Mining module.
Provides easy access to retrieval and filtering operations.
"""
import argparse
import sys
from pathlib import Path

# Add current directory to path for imports
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

from retrieval.CommitAnalyzer.adoptionCommitAnalyzer import AdoptionCommitAnalyzer
from retrieval.CommitAnalyzer.migrationCommitAnalyzer import MigrationCommitAnalyzer
from retrieval.totalIssueAnalysis.totalIssueAnalysis import TotalIssue
from filtering.CommitFilterer.commitFilterer import CommitFilterer
from filtering.IssueFilterer.adoptionIssueFilterer import AdoptionIssueFilterer
from filtering.IssueFilterer.migrationIssueFilterer import MigrationIssueFilterer


def retrieve_commits(commit_type):
    """Retrieve commits from repositories."""
    if commit_type == 'adoption':
        print("Retrieving adoption commits...")
        AdoptionCommitAnalyzer.adoption_analysis()
        print("✓ Adoption commits retrieved successfully")
    elif commit_type == 'migration':
        print("Retrieving migration commits...")
        MigrationCommitAnalyzer.migration_analysis()
        print("✓ Migration commits retrieved successfully")
    else:
        print(f"Error: Unknown commit type '{commit_type}'")
        sys.exit(1)


def retrieve_issues():
    """Retrieve all issues from repositories."""
    print("Retrieving all issues...")
    TotalIssue.run_parallel_analysis()
    TotalIssue.export_issues_summary_to_csv()
    print("✓ All issues retrieved successfully and summary exported")


def retrieve_issues_for_repo(repo_name):
    """Retrieve issues for a specific repository."""
    print(f"Retrieving issues for repository: {repo_name}")
    TotalIssue.get_number_of_open_closed_issues(repo_name, True)
    print(f"✓ Issues for {repo_name} retrieved successfully")


def filter_issues(issue_type):
    """Filter issues using keywords."""
    if issue_type == 'adoption':
        print("Filtering adoption issues...")
        AdoptionIssueFilterer.adoption_analysis()
        AdoptionIssueFilterer.adoption_summary()
        print("✓ Adoption issues filtered successfully and summary generated")
    elif issue_type == 'migration':
        print("Filtering migration issues...")
        MigrationIssueFilterer.migration_analysis()
        MigrationIssueFilterer.migration_summary()
        print("✓ Migration issues filtered successfully and summary generated")
    else:
        print(f"Error: Unknown issue type '{issue_type}'")
        sys.exit(1)


def filter_commits(commit_type):
    """Filter commits using keywords."""
    if commit_type == 'adoption':
        print("Filtering adoption commits...")
        CommitFilterer.adoption_filter()
        CommitFilterer.adoption_summary()
        print("✓ Adoption commits filtered successfully and summary generated")
    elif commit_type == 'migration':
        print("Filtering migration commits...")
        CommitFilterer.migration_filter()
        CommitFilterer.migration_summary()
        print("✓ Migration commits filtered successfully and summary generated")
    else:
        print(f"Error: Unknown commit type '{commit_type}'")
        sys.exit(1)

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Data Mining CLI for E2E Testing Framework Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:

  # Retrieve all issues
  python -m 01_data_mining.cli --task retrieval --target issues
  
  # Retrieve issues for a specific repository
  python -m 01_data_mining.cli --task retrieval --target issues --repo owner/repo

  # Retrieve adoption commits
  python -m 01_data_mining.cli --task retrieval --target commits --type adoption
  
  # Retrieve migration commits
  python -m 01_data_mining.cli --task retrieval --target commits --type migration
  
  # Filter adoption commits
  python -m 01_data_mining.cli --task filtering --target commits --type adoption
  
  # Filter migration commits
  python -m 01_data_mining.cli --task filtering --target commits --type migration
  
  # Filter adoption issues
  python -m 01_data_mining.cli --task filtering --target issues --type adoption
  
  # Filter migration issues
  python -m 01_data_mining.cli --task filtering --target issues --type migration

        """
    )
    
    parser.add_argument(
        '--task',
        choices=['retrieval', 'filtering'],
        required=True,
        help='Task to perform'
    )
    
    parser.add_argument(
        '--target',
        choices=['commits', 'issues'],
        help='Target data type (required for retrieval and filtering)'
    )
    
    parser.add_argument(
        '--type',
        choices=['adoption', 'migration'],
        help='Specific type to process (required for commits and filtering)'
    )
    
    parser.add_argument(
        '--repo',
        help='Repository name (format: owner/repo) for retrieving issues from a specific repository'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.target:
        parser.error(f"--target is required")
    
    if args.target == 'commits' and not args.type:
        parser.error(f"--type is required for commits")
    
    if args.task == 'filtering' and args.target == 'issues' and not args.type:
        parser.error(f"--type is required for filtering issues")
    
    try:
        # Execute task
        if args.task == 'retrieval':
            if args.target == 'commits':
                retrieve_commits(args.type)
            elif args.target == 'issues':
                if args.repo:
                    retrieve_issues_for_repo(args.repo)
                else:
                    retrieve_issues()
        
        elif args.task == 'filtering':
            if args.target == 'commits':
                filter_commits(args.type)
            elif args.target == 'issues':
                filter_issues(args.type)
    
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
