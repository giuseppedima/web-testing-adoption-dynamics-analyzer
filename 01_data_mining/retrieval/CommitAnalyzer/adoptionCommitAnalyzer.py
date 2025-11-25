from pathlib import Path
import pandas as pd
import json
from .commitAnalyzer import CommitAnalyzer
from core.config import RESOURCES_DIR
from core.utils import run_in_parallel

class AdoptionCommitAnalyzer:

    @staticmethod
    def get_repos_with_adoption_commit():
        input_file = RESOURCES_DIR / 'creation-adoption-gui.xlsx'
        df = pd.read_excel(input_file, header=None)
        found_repos = []
        for row in df.iloc[1:].itertuples(index=False): # first row is header
            repo_name, commit_date = row[2], row[1]
            if pd.notna(repo_name) and pd.notna(commit_date):
                commit_date = pd.to_datetime(commit_date)
                found_repos.append([repo_name, commit_date])
        return found_repos
   
    @staticmethod
    def analyze_adoption(repo, commit_date):
        commits = CommitAnalyzer.get_previous_n_commits_starting_from_date(repo, commit_date, 11)
        results = {}
        if commits:
            adoption_commit = commits[0]
            previous_commits = commits[1:]
            
            results[repo] = {
                "adoption_commit": {
                    "hash": adoption_commit.hash,
                    "date": str(adoption_commit.committer_date),
                    "message": adoption_commit.msg
                },
                "previous_commits": [
                    {
                        "hash": c.hash,
                        "date": str(c.committer_date),
                        "message": c.msg
                    } for c in previous_commits
                ]
            }

        return results

    @staticmethod
    def adoption_analysis():

        repos = AdoptionCommitAnalyzer.get_repos_with_adoption_commit()
        
        def process_repo(repo_data):
            repo, commit_date = repo_data
            return AdoptionCommitAnalyzer.analyze_adoption(repo, commit_date)

        all_analysis = run_in_parallel(process_repo, repos, max_workers=10)

        # Merge all dictionaries into one
        merged_analysis = {}
        for analysis in all_analysis:
            merged_analysis.update(analysis)

        # Save results to a JSON file
        output_path = RESOURCES_DIR / 'adoption_commits.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(merged_analysis, f, indent=4, ensure_ascii=False, sort_keys=True)