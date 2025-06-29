from CommitAnalyzer.migrationCommitAnalyzer import MigrationCommitAnalyzer
from IssueFilterer.issueFilterer import IssueFilterer
from datetime import timedelta, timezone
from CommitFilterer.commitFilterer import CommitFilterer
from CommitAnalyzer.commitAnalyzer import CommitAnalyzer
import json
from pathlib import Path

class MigrationIssueFilterer:
    @staticmethod
    def analyze_migration(repo):
        results = {}

        for key, values in repo.items():
            for value in values:
                commit_date = value["timestamp"].replace(hour=23, minute=59, second=59, microsecond=59).replace(tzinfo=timezone.utc)
                issues = IssueFilterer.filter_issues(key, commit_date-timedelta(days=10), commit_date, CommitFilterer.keywords['migration'])

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

        tasks = []
   
        # Prepara le informazioni per ogni task
        for repo in repos:
          tasks.append((MigrationIssueFilterer.analyze_migration, (repo, )))

        all_analysis = CommitAnalyzer.execute_in_parallel(
            tasks=tasks,
            workers=10
        )

        # Merge di tutti i dizionari in uno solo
        merged_analysis = {}
        for analysis in all_analysis:
            merged_analysis.update(analysis)


        # Salva i risultati in un file JSON
        output_path = Path(__file__).resolve().parent.parent / 'resources' / 'migration_issues_filtered.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(merged_analysis, f, indent=4, ensure_ascii=False, sort_keys=True)


if __name__ == "__main__":
    MigrationIssueFilterer.migration_analysis()
