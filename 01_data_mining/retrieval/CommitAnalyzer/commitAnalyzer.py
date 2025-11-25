from pydriller import Repository
from ..RepositoryAnalyzer.RepositoryCloner import Cloner

class CommitAnalyzer:

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
