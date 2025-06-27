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

        input_path = Path(__file__).resolve().parent.parent / 'resources' / 'adoption.json'
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        filtered_data = {}
        for entry in data:
            repo = entry['repo']
            matched_commits = []

            # Controllo case-insensitive
            adoption_msg = entry['adoption']['message'].lower()
            matched_keywords = [
                keyword for keyword in CommitFilterer.keywords['adoption']
                if re.search(rf'\b{re.escape(keyword.lower())}\b', adoption_msg)
            ]
            if matched_keywords:
                entry['adoption']['matches'] = matched_keywords
                matched_commits.append(entry['adoption'])

            for commit in entry['previous']:
                commit_msg = commit['message'].lower()
                matched_keywords = [
                    keyword for keyword in CommitFilterer.keywords['adoption']
                    if re.search(rf'\b{re.escape(keyword.lower())}\b', commit_msg)
                ]
                if matched_keywords:
                    commit['matches'] = matched_keywords
                    matched_commits.append(commit)

            if matched_commits:  # Solo se ci sono match aggiungi il repo
                filtered_data[repo] = matched_commits

        # Salva i dati filtrati su un nuovo file JSON
        output_path = Path(__file__).resolve().parent.parent / 'resources' / 'adoption_filtered.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(filtered_data, f, indent=4, ensure_ascii=False)

    @staticmethod
    def migration_filter():

        input_path = Path(__file__).resolve().parent.parent / 'resources' / 'migration.json'
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        filtered_data = {}
        for repo, migrations in data.items():
            matched_commits = []

            for migration in migrations:

                migration_msg = migration['migration']['message'].lower()
                matched_keywords = [
                    keyword for keyword in CommitFilterer.keywords['migration']
                    if re.search(rf'\b{re.escape(keyword.lower())}\b', migration_msg)
                ]
                if matched_keywords:
                    migration['migration']['matches'] = matched_keywords
                    matched_commits.append(migration['migration'])

                for commit in migration['previous']:
                    commit_msg = commit['message'].lower()
                    matched_keywords = [
                        keyword for keyword in CommitFilterer.keywords['migration']
                        if re.search(rf'\b{re.escape(keyword.lower())}\b', commit_msg)
                    ]
                    if matched_keywords:
                        commit['matches'] = matched_keywords
                        commit['frameworks'] = migration['migration']['frameworks']
                        matched_commits.append(commit)

            if matched_commits:  # Solo se ci sono match aggiungi il repo
                filtered_data[repo] = matched_commits

        # Salva i dati filtrati su un nuovo file JSON
        output_path = Path(__file__).resolve().parent.parent / 'resources' / 'migration_filtered.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(filtered_data, f, indent=4, ensure_ascii=False)

    
    @staticmethod
    def adoption_summary():
        input_path = Path(__file__).resolve().parent.parent / 'resources' / 'adoption_filtered.json'
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
            summary[keyword] = count
        output_path = Path(__file__).resolve().parent.parent / 'resources' / 'adoption_summary.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=4, ensure_ascii=False)
    
    @staticmethod
    def migration_summary():
        input_path = Path(__file__).resolve().parent.parent / 'resources' / 'migration_filtered.json'
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
            summary[keyword] = count
        output_path = Path(__file__).resolve().parent.parent / 'resources' / 'migration_summary.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    # CommitFilterer.adoption_filter()
    # CommitFilterer.migration_filter()
    CommitFilterer.adoption_summary()
    CommitFilterer.migration_summary()