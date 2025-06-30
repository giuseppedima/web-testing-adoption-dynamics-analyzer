import json
from pathlib import Path
import re

class CommitFilterer:
    keywords = {
        'migration': [
            "migrate",
            "migrated",
            "migration",
            "replace",
            "replaced",
            "replacing",
            "switch",
            "switched",
            "transition",
            "transitioned",
            "move",
            "moved",
            "drop",
            "dropped",
            "deprecate",
            "deprecated",
            "rewrite",
            "rewrote",
            "reimplement",
            "refactor",
            "refactored",
            "modernize",
            "adopt",
            "selenium",
            "cypress",
            "puppeteer",
            "playwright",
            "convert",
            "unify tests",
            "restructure",
            "unstable",
            "brittle",
            "slow",
            "performance",
            "speed",
            "browser compatibility",
            "modern",
            "outdated",
            "maintenance",
            "complex",
            "simplify",
            "cleanup",
            "consolidate",
            "consistency",
            "cross-browser",
            "headless",
            "debug",
            "troubleshoot",
            "reliability",
            "robust",
            "coverage",
            "visibility",
            "observability"
        ],
        'adoption': [
            "add test",
            "added test",
            "introduce test",
            "create test",
            "initial test",
            "test setup",
            "first test",
            "add e2e",
            "added e2e",
            "new test suite",
            "added regression test",
            "adoption",
            "selenium",
            "cypress",
            "puppeteer",
            "playwright",
            "browser",
            "UI",
            "GUI",
            "user interface",
            "frontend",
            "bug",
            "prevent",
            "verify",
            "test new feature"
        ]
    }


    @staticmethod
    def adoption_filter():

        input_path = Path(__file__).resolve().parent.parent / 'resources' / 'adoption_commits.json'
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        filtered_data = {}
        lowered_keywords = [k.lower() for k in CommitFilterer.keywords['adoption']]
        for repo, entry in data.items():
            matched_commits = []

            # Controllo case-insensitive
            adoption_msg = entry['adoption_commit']['message'].lower()
            matched_keywords = [
                keyword for keyword in lowered_keywords
                if re.search(rf'\b{re.escape(keyword.lower())}\b', adoption_msg)
            ]
            if matched_keywords:
                entry['adoption_commit']['matches'] = matched_keywords
                matched_commits.append(entry['adoption_commit'])

            for commit in entry['previous_commits']:
                commit_msg = commit['message'].lower()
                matched_keywords = [
                    keyword for keyword in lowered_keywords
                    if re.search(rf'\b{re.escape(keyword.lower())}\b', commit_msg)
                ]
                if matched_keywords:
                    commit['matches'] = matched_keywords
                    matched_commits.append(commit)

            if matched_commits:  # Solo se ci sono match aggiungi il repo
                filtered_data[repo] = matched_commits

        # Salva i dati filtrati su un nuovo file JSON
        output_path = Path(__file__).resolve().parent.parent / 'resources' / 'adoption_commits_filtered.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(filtered_data, f, indent=4, ensure_ascii=False, sort_keys=True)

    @staticmethod
    def migration_filter():

        input_path = Path(__file__).resolve().parent.parent / 'resources' / 'migration_commits.json'
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        filtered_data = {}
        lowered_keywords = [k.lower() for k in CommitFilterer.keywords['migration']]
        for repo, migrations in data.items():

            matched_commits = []

            for migration in migrations:

                migration_msg = migration['migration_commit']['message'].lower()
                matched_keywords = [
                    keyword for keyword in lowered_keywords
                    if re.search(rf'\b{re.escape(keyword.lower())}\b', migration_msg)
                ]
                if matched_keywords:
                    migration['migration_commit']['matches'] = matched_keywords
                    matched_commits.append(migration['migration_commit'])

                for commit in migration['previous_commits']:
                    commit_msg = commit['message'].lower()
                    matched_keywords = [
                        keyword for keyword in lowered_keywords
                        if re.search(rf'\b{re.escape(keyword.lower())}\b', commit_msg)
                    ]
                    if matched_keywords:
                        commit['matches'] = matched_keywords
                        commit['frameworks_involved'] = migration['migration_commit']['frameworks_involved']
                        matched_commits.append(commit)

            if matched_commits:  # Solo se ci sono match aggiungi il repo
                filtered_data[repo] = matched_commits

        # Salva i dati filtrati su un nuovo file JSON
        output_path = Path(__file__).resolve().parent.parent / 'resources' / 'migration_commits_filtered.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(filtered_data, f, indent=4, ensure_ascii=False, sort_keys=True)

    
    @staticmethod
    def adoption_summary():
        input_path = Path(__file__).resolve().parent.parent / 'resources' / 'adoption_commits_filtered.json'
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        summary = {}
        for keyword in CommitFilterer.keywords['adoption']:
            keyword_lower = keyword.lower()
            count = 0
            for repo, commits in data.items():
                for commit in commits:
                    if keyword_lower in [k.lower() for k in commit['matches']]:
                        count += 1
                        print(f"Found match in repo '{repo}' for keyword '{keyword}': {commit['message']}")
            summary[keyword_lower] = count
        output_path = Path(__file__).resolve().parent.parent / 'resources' / 'adoption_commits_summary.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=4, ensure_ascii=False, sort_keys=True)
    
    @staticmethod
    def migration_summary():
        input_path = Path(__file__).resolve().parent.parent / 'resources' / 'migration_commits_filtered.json'
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        summary = {}
        for keyword in CommitFilterer.keywords['migration']:
            keyword_lower = keyword.lower()
            count = 0
            for repo, commits in data.items():
                for commit in commits:
                    if keyword_lower in [k.lower() for k in commit['matches']]:
                        count += 1
                        print(f"Found match in repo '{repo}' for keyword '{keyword}': {commit['message']}")
            summary[keyword_lower] = count
        output_path = Path(__file__).resolve().parent.parent / 'resources' / 'migration_commits_summary.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=4, ensure_ascii=False, sort_keys=True)


if __name__ == "__main__":
    # CommitFilterer.adoption_filter()
    # CommitFilterer.migration_filter()
    CommitFilterer.adoption_summary()
    CommitFilterer.migration_summary()