import concurrent.futures
from pathlib import Path
import pandas as pd
from pydriller import Repository
from datetime import datetime
from RepositoryAnalyzer.RepositoryCloner import Cloner
import json


class CommitAnalyzer:
    
    @staticmethod
    def get_repos_with_adoption_commit():
        input_file = Path(__file__).resolve().parent.parent / 'resources' / 'creation-adoption-gui.xlsx'
        df = pd.read_excel(input_file, header=None)
        found_repos = []
        for row in df.iloc[1:].itertuples(index=False): # first row is header
            repo_name, commit_date = row[2], row[1]
            if pd.notna(repo_name) and pd.notna(commit_date):
                commit_date = pd.to_datetime(commit_date)
                found_repos.append([repo_name, commit_date])
        return found_repos

    @staticmethod
    def get_repos_with_migration_commit():
        input_file = Path(__file__).resolve().parent.parent / 'resources' / 'migration_analysis.xlsx'
        df = pd.read_excel(input_file, header=None)
        found_repos = []
        for row in df.itertuples(index=False):
            key = row[0].replace('_', '/',1)  # Replace first underscore with slash
            values = []
            for col in row[2:]:
                if pd.notna(col):
                    try:
                        timestamp_part, frameworks_part = col.split('] : ')
                        timestamp_str = timestamp_part.strip('[')
                        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                        frameworks = [fw for fw in frameworks_part.strip(';').split(';') if fw]
                        values.append({'timestamp': timestamp, 'frameworks': frameworks})
                    except Exception as e:
                        print(f"Error parsing value '{col}': {e}")
                else:
                    break
            if values:
                found_repos.append({key: values})
        return found_repos

    @staticmethod
    def execute_in_parallel(tasks, workers=10):

        futures = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            for task, params in tasks:
                futures.append(executor.submit(task, *params))

        results = []
        for future in concurrent.futures.as_completed(futures):
            result = future.result()  # Retrieve the result of the process
            results.append(result)

        return results

    @staticmethod
    def get_previous_n_commits_starting_from_date(repository, start_date, n):
        
        cloner = Cloner()
        try:
            print(f"Cloning repository: {repository}")
            path = cloner.clone_repository(repository)
            print(f"Repository {repository} cloned successfully.")

            repo = Repository(path, order='reverse', to=start_date)

            commits = []

            for commit in repo.traverse_commits():
                if n > 0:
                    commits.append(commit)
                    n -= 1
                else:
                    break

            if not commits:
                raise ValueError(f"No commits found for repository {repository} at date {start_date}.")

            return commits

        except Exception as e:
            print(f"Error getting commits from repository {repository}: {e}")

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
                    print(f"Processing repository: {key} with commit date: {value['timestamp']}, frameworks: {value['frameworks']}")
                    tasks.append((CommitAnalyzer.get_previous_n_commits_starting_from_date, (key, value["timestamp"], 11)))
                    repo_keys.append(key)
                    frameworks_list.append(value['frameworks'])
                    migration_info.append({
                        "repo": key,
                        "timestamp": value["timestamp"],
                        "frameworks": value["frameworks"]
                    })

        all_commits = CommitAnalyzer.execute_in_parallel(
            tasks=tasks,
            workers=100
        )

        # Costruisci la struttura richiesta
        results = {}
        for idx, commits in enumerate(all_commits):
            repo_name = repo_keys[idx]
            frameworks = frameworks_list[idx]
            migration_commit = commits[0] if commits else None
            previous_commits = commits[1:] if commits else []

            migration_entry = {
                "migration": {
                    "frameworks": frameworks,
                    "hash": migration_commit.hash if migration_commit else None,
                    "date": str(migration_commit.committer_date) if migration_commit else None,
                    "message": migration_commit.msg if migration_commit else None
                },
                "previous": [
                    {
                        "hash": c.hash,
                        "date": str(c.committer_date),
                        "message": c.msg
                    } for c in previous_commits
                ]
            }

            if repo_name not in results:
                results[repo_name] = []
            results[repo_name].append(migration_entry)

        # Salva i risultati in un file JSON
        output_path = Path(__file__).resolve().parent.parent / 'resources' / 'migration.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)

        #TODO: cleanup clone directories

    @staticmethod
    def adoption_analysis():

        repos = CommitAnalyzer.get_repos_with_adoption_commit()

        tasks=[]
        for repo, commit_date in repos:
            print(f"Processing repository: {repo} with first GUI testing commit date: {commit_date}")
            tasks.append((CommitAnalyzer.get_previous_n_commits_starting_from_date, (repo, commit_date, 11)))

        all_commits = CommitAnalyzer.execute_in_parallel(
            tasks=tasks,
            workers=100
        )

        results = []
        for idx, commits in enumerate(all_commits):
            if commits:
                repo_name, adoption_date = repos[idx]
                adoption_commit = commits[0]
                previous_commits = commits[1:]
                results.append({
                    "repo": repo_name,
                    "adoption": {
                        "hash": adoption_commit.hash,
                        "date": str(adoption_commit.committer_date),
                        "message": adoption_commit.msg
                    },
                    "previous": [
                        {
                            "hash": c.hash,
                            "date": str(c.committer_date),
                            "message": c.msg
                        } for c in previous_commits
                    ]
                })
            else:
                print("No commits found for this repository.")

        # Salva i risultati in un file JSON
        output_path = Path(__file__).resolve().parent.parent / 'resources' / 'adoption.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)

        #TODO: cleanup clone directories


if __name__ == "__main__":
    Cloner.enable_git_long_paths()
    CommitAnalyzer.adoption_analysis()
    CommitAnalyzer.migration_analysis()
