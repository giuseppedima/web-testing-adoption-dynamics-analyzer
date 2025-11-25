from pathlib import Path
import pandas as pd
from datetime import datetime
from .commitAnalyzer import CommitAnalyzer
from core.config import RESOURCES_DIR
from core.utils import run_in_parallel
import json

class MigrationCommitAnalyzer:
    @staticmethod
    def get_repos_with_migration_commit():
        input_file = RESOURCES_DIR / 'migration_analysis.xlsx'
        df = pd.read_excel(input_file, header=None)
        found_repos = []
        for row in df.itertuples(index=False):
            key = row[0].replace('_', '/',1)  # Replace first underscore with slash
            values = []
            for col in row[2:]:
                if pd.notna(col):
                    try:
                        timestamp_part, frameworks_part = col.split('] : ')
                        timestamp_str = timestamp_part.strip('[')
                        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                        frameworks = [fw for fw in frameworks_part.strip(';').split(';') if fw]
                        values.append({'timestamp': timestamp, 'frameworks': frameworks})
                    except Exception as e:
                        print(f"Error parsing value '{col}': {e}")
                else:
                    break
            if values:
                found_repos.append({key: values})
        return found_repos

    @staticmethod
    def analyze_migration(repo):
        repo_name, migrations_info = next(iter(repo.items()))

        results = {}

        for migration in migrations_info:
            commits = CommitAnalyzer.get_previous_n_commits_starting_from_date(repo_name, migration['timestamp'], 11)

            if not commits:
                continue

            migration_commit = commits[0] if commits else None
            previous_commits = commits[1:] if commits else []

            migration_entry = {
                "migration_commit": {
                    "frameworks_involved": migration['frameworks'],
                    "hash": migration_commit.hash if migration_commit else None,
                    "date": str(migration_commit.committer_date) if migration_commit else None,
                    "message": migration_commit.msg if migration_commit else None
                },
                "previous_commits": [
                    {
                        "hash": c.hash,
                        "date": str(c.committer_date),
                        "message": c.msg
                    } for c in previous_commits
                ]
            }

            if repo_name not in results:
                results[repo_name] = []
            results[repo_name].append(migration_entry)

        return results

    @staticmethod
    def migration_analysis():
   
        repos = MigrationCommitAnalyzer.get_repos_with_migration_commit()

        all_analysis = run_in_parallel(MigrationCommitAnalyzer.analyze_migration, repos, max_workers=10)

        # Merge all dictionaries into one
        merged_analysis = {}
        for analysis in all_analysis:
            merged_analysis.update(analysis)

        # Save results to a JSON file
        output_path = RESOURCES_DIR / 'migration_commits.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(merged_analysis, f, indent=4, ensure_ascii=False, sort_keys=True)