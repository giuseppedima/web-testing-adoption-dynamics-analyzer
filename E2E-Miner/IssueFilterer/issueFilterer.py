from pathlib import Path
import json
from datetime import datetime
import re

class IssueFilterer:

    @staticmethod
    def filter_issues(repository, start_date, end_date, keywords):
        filtered_issues = {"open": [], "closed": []}
        lowered_keywords = [k.lower() for k in keywords]
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
                        matched_keywords = [
                            keyword for keyword in lowered_keywords
                            if re.search(rf'\b{re.escape(keyword)}\b', body_msg) or
                               re.search(rf'\b{re.escape(keyword)}\b', title_msg)
                        ]
                        if append and matched_keywords:
                            filtered_issues[status].append({
                                "number": issue['number'],
                                "title": issue['title'],
                                "body": issue['body'],
                                "created_at": issue['created_at'],
                                "updated_at": issue['updated_at'],
                                "closed_at": issue['closed_at'],
                                "matches": matched_keywords,
                            })
                    except Exception as e:
                        print(f"Error processing issue {issue['number']} in repository {repository} issue number {issue['number']}: {e}")
        except FileNotFoundError:
            print(f"No issues file found for repository {repository}. Skipping filtering.")
        
        return filtered_issues

    @staticmethod
    def issues_missed_in_filter(repo, issues):
        filtered_issues = {"open": [], "closed": []}
        all_issues = Path(__file__).resolve().parent.parent / 'resources' / 'all_issues' / f'{repo.replace("/", "_", 1)}_all_issues.json'
        if not all_issues.exists():
            print(f"File {all_issues} does not exist. Skipping repository {repo}.")
            return filtered_issues
        
        with open(all_issues, 'r', encoding='utf-8') as f:
            issues_data = json.load(f)
            for status, issue_list in [('open', issues_data['open']), ('closed', issues_data['closed'])]:
                for issue in issue_list:
                    if issue['number'] in issues:
                        filtered_issues['open' if status == 'open' else 'closed'].append({
                            "number": issue['number'],
                            "title": issue['title'],
                            "body": issue['body'],
                        "created_at": issue['created_at'],
                        "updated_at": issue['updated_at'],
                        "closed_at": issue['closed_at']
                        
                    })
        return filtered_issues

if __name__ == "__main__":
    input_path = Path(__file__).resolve().parent.parent / 'resources' / 'issues_missed_in_filter.json'
    to_download = {
        "layer5io/meshery": [11557],
        "guardicore/monkey": [3685],
        "laion-ai/open-assistant": [86],
        "openrefine/openrefine": [733],
        "royal-navy/design-system": [3035, 3446]
    }
    result = {}
    for repo, issues in to_download.items():
        result[repo] = {}
        result[repo]["issues"] = IssueFilterer.issues_missed_in_filter(repo, issues)

    with open(input_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False, sort_keys=True)
