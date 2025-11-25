import json
import pandas as pd
import re
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.config import RESOURCES_DIR

class Converter:
    @staticmethod
    def commits_adoption():
        rows = []

        # Load the JSON file
        input_file = RESOURCES_DIR / 'adoption_commits_filtered.json'
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Loop through each repo and commit
        for repo_name, commits in data.items():
            for commit in commits:
                rows.append({
                    'repo': repo_name,
                    'hash': commit['hash'],
                    'date': commit['date'],
                    'message': Converter.clean_excel_string(commit['message']),
                    'matches': ', '.join(commit.get('matches', [])),
                })
        
        # Convert to DataFrame and export to Excel
        df = pd.DataFrame(rows)
        output_file = RESOURCES_DIR / 'adoption_commits_filtered.xlsx'
        df.to_excel(output_file, index=False)

    @staticmethod
    def commits_migration():
        rows = []

        # Load the JSON file
        input_file = RESOURCES_DIR / 'migration_commits_filtered.json'
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Loop through each repo and migration
        for repo_name, migrations in data.items():
            for migration in migrations:
                frames_involved = ",".join(migration.get('frameworks_involved', []))
                rows.append({
                    'repo': repo_name,
                    'date': migration['date'],
                    'hash': migration['hash'],
                    'matches': ', '.join(migration.get('matches', [])),
                    'message': Converter.clean_excel_string(migration['message']),
                    'frameworks_involved': frames_involved,
                })
        
        # Convert to DataFrame and export to Excel
        df = pd.DataFrame(rows)
        output_file = RESOURCES_DIR / 'migration_commits_filtered.xlsx'
        df.to_excel(output_file, index=False)

    @staticmethod
    def issues_adoption():
        rows = []

        # Load the JSON file
        input_file = RESOURCES_DIR / 'adoption_issues_filtered.json'
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Loop through each repo and issue
        for repo_name, adoption in data.items():
            for is_closed, issues in [(False, adoption['issues']['open']), (True, adoption['issues']['closed'])]:
                for issue in issues:
                    rows.append({
                        'time_interval_start': adoption['time_interval']['start'],
                        'time_interval_end': adoption['time_interval']['end'],
                        'repo': repo_name,
                        'number': issue['number'],
                        'title': Converter.clean_excel_string(issue['title']),
                        'body': Converter.clean_excel_string(issue['body']),
                        'created_at': issue['created_at'],
                        'updated_at': issue['updated_at'],
                        'closed_at': issue['closed_at'],
                        'is_closed': is_closed,
                        'matches': ', '.join(issue['matches']),
                    })
        
        # Convert to DataFrame and export to Excel
        df = pd.DataFrame(rows)
        output_file = RESOURCES_DIR / 'adoption_issues_filtered.xlsx'
        df.to_excel(output_file, index=False)

    @staticmethod
    def issues_migration():
        rows = []

        # Load the JSON file
        input_file = RESOURCES_DIR / 'migration_issues_filtered.json'
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Loop through each repo and issue
        for repo_name, migrations in data.items():
            for migration in migrations:
                frames_involved = ",".join(migration['frameworks_involved'])
                for is_closed, issues in [(False, migration['issues']['open']), (True, migration['issues']['closed'])]:
                    for issue in issues:
                        rows.append({
                            'frameworks_involved': frames_involved,
                            'time_interval_start': migration['time_interval']['start'],
                            'time_interval_end': migration['time_interval']['end'],
                            'repo': repo_name,
                            'number': issue['number'],
                            'title': Converter.clean_excel_string(issue['title']),
                            'body': Converter.clean_excel_string(issue['body']),
                            'created_at': issue['created_at'],
                            'updated_at': issue['updated_at'],
                            'closed_at': issue['closed_at'],
                            'is_closed': is_closed,
                            'matches': ', '.join(issue['matches']),
                        })
        
        # Convert to DataFrame and export to Excel
        df = pd.DataFrame(rows)
        output_file = RESOURCES_DIR / 'migration_issues_filtered.xlsx'
        df.to_excel(output_file, index=False)

    @staticmethod
    def issues_missed_in_filter():
        rows = []  # This will store the rows for the Excel file

        # Load the JSON file
        input_file = RESOURCES_DIR / 'issues_missed_in_filter.json'
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Loop through each repo and issue
        for repo_name, res in data.items():

            for is_closed, issues in [(False, res['issues']['open']), (True, res['issues']['closed'])]:
                for issue in issues:
                    rows.append({
                        'repo': repo_name,
                        'number': issue['number'],
                        'title': Converter.clean_excel_string(issue['title']),
                        'body': Converter.clean_excel_string(issue['body']),
                        'created_at': issue['created_at'],
                        'updated_at': issue['updated_at'],
                        'closed_at': issue['closed_at'],
                        'is_closed': is_closed,
                    })
        # Convert the list of dicts to a DataFrame and export to Excel
        df = pd.DataFrame(rows)
        output_file = RESOURCES_DIR / 'issues_missed_in_filter.xlsx'
        df.to_excel(output_file, index=False)


    @staticmethod
    def clean_excel_string(s):
        if not isinstance(s, str):
            s = str(s)
        # Remove invalid characters for Excel, but keep \n and \r
        s = re.sub(r'[\x00-\x09\x0B\x0C\x0E-\x1F\x7F]', '', s)
        # Remove non-BMP Unicode characters (Excel doesn't support them)
        s = re.sub(r'[^\u0000-\uFFFF]', '', s)
        # If the string starts with "=", add a space in front to avoid formulas
        if s.startswith("="):
            s = " " + s
        return s

