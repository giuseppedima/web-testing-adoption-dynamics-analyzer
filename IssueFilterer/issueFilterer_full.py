from datetime import timedelta
from pathlib import Path
import json
from CommitAnalyzer.commitAnalyzer import CommitAnalyzer
from CommitFilterer.commitFilterer import CommitFilterer
from datetime import datetime, timezone
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
                        matched_keywords = [
                            keyword for keyword in keywords
                            if re.search(rf'\b{re.escape(keyword.lower())}\b', body_msg) or
                               re.search(rf'\b{re.escape(keyword.lower())}\b', title_msg)
                        ]
                        if append and matched_keywords:
                            filtered_issues[status].append({
                                "number": issue['number'],
                                "title": issue['title'],
                                "body": issue['body'],
                                "created_at": issue['created_at'],
                                "updated_at": issue['updated_at'],
                                "closed_at": issue['closed_at'],
                                "matches": matched_keywords
                            })
                    except Exception as e:
                        print(f"Error processing issue {issue['number']} in repository {repository} issue number {issue['number']}: {e}")
        except FileNotFoundError:
            print(f"No issues file found for repository {repository}. Skipping filtering.")
        
        return filtered_issues

    @staticmethod
    def adoption_analysis():
        repos = CommitAnalyzer.get_repos_with_adoption_commit()

        tasks = []
        for repo, commit_date in repos:
            commit_date = commit_date.replace(hour=23, minute=59, second=59, microsecond=59).replace(tzinfo=timezone.utc)
            tasks.append((IssueFilterer.filter_issues, (repo, commit_date-timedelta(days=10), commit_date, CommitFilterer.keywords['adoption'])))

        all_issues = CommitAnalyzer.execute_in_parallel(
            tasks=tasks,
            workers=100
        )

        results = []
        for idx, issues in enumerate(all_issues):
            # Aggiungi solo se almeno una delle due liste non è vuota
            if issues and (issues["open"] or issues["closed"]):
                repo_name, _ = repos[idx]
                results.append({repo_name: issues})
            else:
                print(f"No issues found for repository {repos[idx][0]} around adoption date {repos[idx][1]} matching keywords.")
        output_path = Path(__file__).resolve().parent.parent / 'resources' / 'adoption_issues_filtered.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)

    @staticmethod
    def migration_analysis():
        repos = CommitAnalyzer.get_repos_with_migration_commit()

        tasks = []
        migration_info = []
        repo_keys = []
        frameworks_list = []

        # Prepara le informazioni per ogni task
        for repo in repos:
            for key, values in repo.items():
                for value in values:
                    commit_date = value["timestamp"].replace(hour=23, minute=59, second=59, microsecond=59).replace(tzinfo=timezone.utc)
                    tasks.append((IssueFilterer.filter_issues, (key, commit_date-timedelta(days=10), commit_date, CommitFilterer.keywords['migration'])))
                    repo_keys.append(key)
                    frameworks_list.append(value['frameworks'])
                    migration_info.append({
                        "repo": key,
                        "timestamp": value["timestamp"],
                        "frameworks": value["frameworks"]
                    })

        all_issues = CommitAnalyzer.execute_in_parallel(
            tasks=tasks,
            workers=100
        )

        # Costruisci la struttura richiesta
        results = {}
        for idx, issues in enumerate(all_issues):
            repo_name = repo_keys[idx]
            frameworks = frameworks_list[idx]
            if not issues:
                print(f"No issues found for repository {repo_name}.")
                continue

            migration_entry = {
                'frameworks': frameworks,
                'issues': {
                    'open': issues['open'] if issues else [],
                    'closed': issues['closed'] if issues else []
                },
            }

            if repo_name not in results:
                results[repo_name] = []
            results[repo_name].append(migration_entry)

        # Salva i risultati in un file JSON
        output_path = Path(__file__).resolve().parent.parent / 'resources' / 'migration_issues_filtered.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)


    @staticmethod
    def adoption_summary():
        input_path = Path(__file__).resolve().parent.parent / 'resources' / 'adoption_issues_filtered.json'
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        summary = {}
        for repo_data in data:
            for _, issues in repo_data.items():
                for issue in issues['open'] + issues['closed']:
                    for keyword in issue['matches']:
                        keyword_lower = keyword.lower()
                        if keyword_lower not in summary:
                            summary[keyword_lower] = 0
                        summary[keyword_lower] += 1

        output_path = Path(__file__).resolve().parent.parent / 'resources' / 'adoption_issues_summary.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=4, ensure_ascii=False)
    
    @staticmethod
    def migration_summary():
        input_path = Path(__file__).resolve().parent.parent / 'resources' / 'migration_issues_filtered.json'
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
        output_path = Path(__file__).resolve().parent.parent / 'resources' / 'migration_issues_summary.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=4, ensure_ascii=False)



if __name__ == "__main__":
    # IssueFilterer.adoption_analysis()
    # IssueFilterer.migration_analysis()
    IssueFilterer.adoption_summary()
    IssueFilterer.migration_summary()