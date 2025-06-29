from pathlib import Path
import json
from datetime import datetime
import re

class IssueFilterer:

    @staticmethod
    def filter_issues(repository, start_date, end_date, keywords):
        filtered_issues = {"open": [], "closed": []}
        try:
            issue_file = Path(__file__).resolve().parent.parent / 'resources' / 'all_issues' / f'{repository.replace("/", "_", 1)}_all_issues.json'
            with open(issue_file, 'r', encoding='utf-8') as f:
                issues = json.load(f)
            
            for status, issue_list in [('open', issues['open']), ('closed', issues['closed'])]:
                for issue in issue_list:
                    try:
                        append = False

                        created_at = datetime.fromisoformat(issue['created_at'].replace('Z', '+00:00'))
                        if start_date <= created_at <= end_date:
                            append = True
                        updated_at = datetime.fromisoformat(issue['updated_at'].replace('Z', '+00:00')) if issue['updated_at'] else None
                        if start_date <= updated_at <= end_date:
                            append = True
                        if issue['closed_at']:
                            closed_at = datetime.fromisoformat(issue['closed_at'].replace('Z', '+00:00'))
                            if closed_at and start_date <= closed_at <= end_date:
                                append = True

                        title_msg = issue['title'].lower() if issue['title'] else ''
                        body_msg = issue['body'].lower() if issue['body'] else ''
                        if append and any(
                            re.search(rf'\b{re.escape(keyword.lower())}\b', body_msg) or
                            re.search(rf'\b{re.escape(keyword.lower())}\b', title_msg)
                            for keyword in keywords
                        ):
                            filtered_issues[status].append({
                                "number": issue['number'],
                                "title": issue['title'],
                                "body": issue['body'],
                                "created_at": issue['created_at'],
                                "updated_at": issue['updated_at'],
                                "closed_at": issue['closed_at']
                            })
                    except Exception as e:
                        print(f"Error processing issue {issue['number']} in repository {repository} issue number {issue['number']}: {e}")
        except FileNotFoundError:
            print(f"No issues file found for repository {repository}. Skipping filtering.")
        
        return filtered_issues

