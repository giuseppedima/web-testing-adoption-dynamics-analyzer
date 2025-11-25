import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from retrieval.CommitAnalyzer.migrationCommitAnalyzer import MigrationCommitAnalyzer
from .issueFilterer import IssueFilterer
from datetime import timedelta, timezone
from core.constants import MIGRATION_KEYWORDS
from core.utils import run_in_parallel
from core.config import RESOURCES_DIR
import json

class MigrationIssueFilterer:
    @staticmethod
    def analyze_migration(repo):
        results = {}

        for key, values in repo.items():
            for value in values:
                commit_date = value["timestamp"].replace(hour=23, minute=59, second=59, microsecond=59).replace(tzinfo=timezone.utc)
                issues = IssueFilterer.filter_issues(key, commit_date-timedelta(days=10), commit_date, MIGRATION_KEYWORDS)

                if issues and (issues["open"] or issues["closed"]):
                    migration_entry = {
                        'frameworks_involved': value['frameworks'],
                        'time_interval': {
                            'start': (commit_date - timedelta(days=10)).isoformat(),
                            'end': commit_date.isoformat()
                        },
                        'issues': {
                            'open': issues['open'] if issues else [],
                            'closed': issues['closed'] if issues else []
                        },
                    }
                    if key not in results:
                        results[key] = []
                    results[key].append(migration_entry)
        return results
    
    @staticmethod
    def migration_analysis():
        repos = MigrationCommitAnalyzer.get_repos_with_migration_commit()

        all_analysis = run_in_parallel(MigrationIssueFilterer.analyze_migration, repos, max_workers=10)

        # Merge all dictionaries into one
        merged_analysis = {}
        for analysis in all_analysis:
            merged_analysis.update(analysis)


        # Save results to a JSON file
        output_path = RESOURCES_DIR / 'migration_issues_filtered.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(merged_analysis, f, indent=4, ensure_ascii=False, sort_keys=True)
    
    @staticmethod
    def migration_summary():
        input_path = RESOURCES_DIR / 'migration_issues_filtered.json'
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        summary = {}
        for _, migrations in data.items():
            for migration in migrations:
                for issue in migration['issues']['open'] + migration['issues']['closed']:
                    for keyword in issue['matches']:
                        keyword_lower = keyword.lower()
                        if keyword_lower not in summary:
                            summary[keyword_lower] = 0
                        summary[keyword_lower] += 1
        output_path = RESOURCES_DIR / 'migration_issues_summary.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=4, ensure_ascii=False, sort_keys=True)
