import json
from pathlib import Path
import re
from core.constants import ADOPTION_KEYWORDS, MIGRATION_KEYWORDS
from core.config import RESOURCES_DIR

class CommitFilterer:

    @staticmethod
    def adoption_filter():

        input_path = RESOURCES_DIR / 'adoption_commits.json'
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        filtered_data = {}
        lowered_keywords = [k.lower() for k in ADOPTION_KEYWORDS]
        for repo, entry in data.items():
            matched_commits = []

            # Case-insensitive check
            adoption_msg = entry['adoption_commit']['message'].lower()
            matched_keywords = [
                keyword for keyword in lowered_keywords
                if re.search(rf'\b{re.escape(keyword)}\b', adoption_msg)
            ]
            if matched_keywords:
                entry['adoption_commit']['matches'] = matched_keywords
                matched_commits.append(entry['adoption_commit'])

            for commit in entry['previous_commits']:
                commit_msg = commit['message'].lower()
                matched_keywords = [
                    keyword for keyword in lowered_keywords
                    if re.search(rf'\b{re.escape(keyword)}\b', commit_msg)
                ]
                if matched_keywords:
                    commit['matches'] = matched_keywords
                    matched_commits.append(commit)

            if matched_commits:  # Add repo only if there are matches
                filtered_data[repo] = matched_commits

        # Save filtered data to a new JSON file
        output_path = RESOURCES_DIR / 'adoption_commits_filtered.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(filtered_data, f, indent=4, ensure_ascii=False, sort_keys=True)

    @staticmethod
    def migration_filter():

        input_path = RESOURCES_DIR / 'migration_commits.json'
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        filtered_data = {}
        lowered_keywords = [k.lower() for k in MIGRATION_KEYWORDS]
        for repo, migrations in data.items():

            matched_commits = []

            for migration in migrations:

                migration_msg = migration['migration_commit']['message'].lower()
                matched_keywords = [
                    keyword for keyword in lowered_keywords
                    if re.search(rf'\b{re.escape(keyword)}\b', migration_msg)
                ]
                if matched_keywords:
                    migration['migration_commit']['matches'] = matched_keywords
                    matched_commits.append(migration['migration_commit'])

                for commit in migration['previous_commits']:
                    commit_msg = commit['message'].lower()
                    matched_keywords = [
                        keyword for keyword in lowered_keywords
                        if re.search(rf'\b{re.escape(keyword)}\b', commit_msg)
                    ]
                    if matched_keywords:
                        commit['matches'] = matched_keywords
                        commit['frameworks_involved'] = migration['migration_commit']['frameworks_involved']
                        matched_commits.append(commit)

            if matched_commits:  # Add repo only if there are matches
                filtered_data[repo] = matched_commits

        # Save filtered data to a new JSON file
        output_path = RESOURCES_DIR / 'migration_commits_filtered.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(filtered_data, f, indent=4, ensure_ascii=False, sort_keys=True)

    
    @staticmethod
    def adoption_summary():
        input_path = RESOURCES_DIR / 'adoption_commits_filtered.json'
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        summary = {}
        for keyword in ADOPTION_KEYWORDS:
            keyword_lower = keyword.lower()
            count = 0
            for repo, commits in data.items():
                for commit in commits:
                    if keyword_lower in commit['matches']:
                        count += 1
                        print(f"Found match in repo '{repo}' for keyword '{keyword}': {commit['message']}")
            summary[keyword_lower] = count
        output_path = RESOURCES_DIR / 'adoption_commits_summary.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=4, ensure_ascii=False, sort_keys=True)
    
    @staticmethod
    def migration_summary():
        input_path = RESOURCES_DIR / 'migration_commits_filtered.json'
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        summary = {}
        for keyword in MIGRATION_KEYWORDS:
            keyword_lower = keyword.lower()
            count = 0
            for repo, commits in data.items():
                for commit in commits:
                    if keyword_lower in commit['matches']:
                        count += 1
                        print(f"Found match in repo '{repo}' for keyword '{keyword}': {commit['message']}")
            summary[keyword_lower] = count
        output_path = RESOURCES_DIR / 'migration_commits_summary.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=4, ensure_ascii=False, sort_keys=True)