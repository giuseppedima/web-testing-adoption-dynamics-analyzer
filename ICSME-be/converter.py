import json
import pandas as pd
import re

class Converter:
    @staticmethod
    def adoption():
        rows = []  # This will store the rows for the Excel file

        # Load the JSON file
        with open('adoption_issues_filtered.json', 'r', encoding='utf-8') as f:
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
        # Convert the list of dicts to a DataFrame and export to Excel
        df = pd.DataFrame(rows)
        df.to_excel('adoption_issues_filtered.xlsx', index=False)


    @staticmethod
    def migration():
        rows = []  # This will store the rows for the Excel file

        # Load the JSON file
        with open('migration_issues_filtered.json', 'r', encoding='utf-8') as f:
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

        # Convert the list of dicts to a DataFrame and export to Excel
        df = pd.DataFrame(rows)
        df.to_excel('migration_issues_filtered.xlsx', index=False)

    @staticmethod
    def issues_missed_in_filter():
        rows = []  # This will store the rows for the Excel file

        # Load the JSON file
        with open('issues_missed_in_filter.json', 'r', encoding='utf-8') as f:
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
        df.to_excel('issues_missed_in_filter.xlsx', index=False)


    @staticmethod
    def clean_excel_string(s):
        if not isinstance(s, str):
            s = str(s)
        # Rimuove caratteri non validi per Excel, ma mantiene \n e \r
        s = re.sub(r'[\x00-\x09\x0B\x0C\x0E-\x1F\x7F]', '', s)
        # Rimuove caratteri Unicode non BMP (Excel non li supporta)
        s = re.sub(r'[^\u0000-\uFFFF]', '', s)
        # Se la stringa inizia con "=", aggiungi uno spazio davanti per evitare formule
        if s.startswith("="):
            s = " " + s
        return s

if __name__ == "__main__":
    # Converter.adoption()
    # Converter.migration()
    Converter.issues_missed_in_filter()