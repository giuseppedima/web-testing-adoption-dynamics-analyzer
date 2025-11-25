import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from retrieval.CommitAnalyzer.adoptionCommitAnalyzer import AdoptionCommitAnalyzer
from .issueFilterer import IssueFilterer
from datetime import timedelta, timezone
from core.constants import ADOPTION_KEYWORDS
from core.utils import run_in_parallel
from core.config import RESOURCES_DIR
import json

class AdoptionIssueFilterer:
    @staticmethod
    def analyze_adoption(repo, commit_date):

        commit_date = commit_date.replace(hour=23, minute=59, second=59, microsecond=59).replace(tzinfo=timezone.utc)

        issues = IssueFilterer.filter_issues(repo, commit_date-timedelta(days=10), commit_date, ADOPTION_KEYWORDS)

        results = {}

        # Add only if at least one of the two lists is not empty
        if issues and (issues["open"] or issues["closed"]):
            results[repo] = {
                'time_interval': {
                    'start': (commit_date - timedelta(days=10)).isoformat(),
                    'end': commit_date.isoformat()
                },
                'issues': {
                    'open': issues['open'] if issues else [],
                    'closed': issues['closed'] if issues else []
                },
            }

        return results
    
    @staticmethod
    def adoption_analysis():
        repos = AdoptionCommitAnalyzer.get_repos_with_adoption_commit()

        def process_repo(repo_data):
            repo, commit_date = repo_data
            return AdoptionIssueFilterer.analyze_adoption(repo, commit_date)

        all_analysis = run_in_parallel(process_repo, repos, max_workers=10)

        merged_analysis = {}
        for analysis in all_analysis:
            merged_analysis.update(analysis)

        output_path = RESOURCES_DIR / 'adoption_issues_filtered.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(merged_analysis, f, indent=4, ensure_ascii=False, sort_keys=True)

    @staticmethod
    def adoption_summary():
        input_path = RESOURCES_DIR / 'adoption_issues_filtered.json'
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        summary = {}

        for _, adoption in data.items():
            for issue in adoption['issues']['open'] + adoption['issues']['closed']:
                for keyword in issue['matches']:
                    keyword_lower = keyword.lower()
                    if keyword_lower not in summary:
                        summary[keyword_lower] = 0
                    summary[keyword_lower] += 1

        output_path = RESOURCES_DIR / 'adoption_issues_summary.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=4, ensure_ascii=False, sort_keys=True)
