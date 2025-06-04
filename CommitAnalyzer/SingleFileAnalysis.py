import gc

from CommitAnalyzer.commitAnalyzer import  CommitAnalyzer
from pydriller import Repository, ModificationType

from RepositoryAnalyzer.RepositoryCloner import Cloner


class SingleFileAnalysis:

    @staticmethod
    def filter_false_envolved_commit(sorted_commits,filename):
        real_envolved_commit = []
        current_filename = filename
        for i in range(len(sorted_commits)):
            commit = sorted_commits[i]
            found = False
            print(f"-----COMMIT {i} ({commit.committer_date})---------")
            for modification in commit.modified_files:
                type = modification.change_type
                path = modification.new_path
                old_name = modification.old_path
                if type == ModificationType.ADD:
                    if path == current_filename:
                        found = True
                        break
                elif type == ModificationType.DELETE:
                    if old_name == current_filename:
                        found = True
                        break
                elif type == ModificationType.MODIFY:
                    if path == current_filename:
                        found = True
                        break
                elif type == ModificationType.RENAME:
                    if  path == current_filename:
                        found = True
                        current_filename = old_name
                        break
            if found:
                real_envolved_commit.append(commit)
        return real_envolved_commit

    @staticmethod
    def analyze_single_file(repo_path,filename):
        repo = Repository(repo_path, filepath=file)
        file_commit_involved = list(repo.traverse_commits())
        non_merge_commits_involved = [commit for commit in file_commit_involved if not commit.merge]
        print(f" [before] {file} envoles {len(non_merge_commits_involved)} commit!")
        sorted_commits = sorted(non_merge_commits_involved, key=lambda c: c.committer_date, reverse=True)
        real_envolved_commit = SingleFileAnalysis.filter_false_envolved_commit(sorted_commits,filename)
        print(f" [after] {file} envoles {len(real_envolved_commit)} commit!")



#repos = CommitAnalyzer.get_e2e_repo_with_n_more_test(30)
#web_repo, e2e_repo = repos[8]
repo_name = 'keycloak/keycloak'
original_name = repo_name.replace('/', '\\')
new_name = repo_name.replace('/', '_')
file_analysis_name = new_name + ".csv"
path_folder_clone = f"../clone"
#cloner = Cloner(path_folder_clone)
#cloner.clone_repository(repo_name)
cloned_repository = path_folder_clone + "/" + new_name
files_name = CommitAnalyzer.get_tests_path_main(file_analysis_name,repo_name,False)
print(f"The repo {repo_name} has {len(files_name)} number of e2e test files.")
sel_commits = []
for file in files_name:
    try:
        repo = Repository(cloned_repository, filepath=file)
        file_commit_involved = list(repo.traverse_commits())
        non_merge_commits = [commit for commit in file_commit_involved if not commit.merge]
        discendent_non_merge_commits = sorted(non_merge_commits, key=lambda c: c.committer_date, reverse=True)
        to_replace = '/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/clone/' + repo_name.replace(
            '/', '_')
        filename = file.replace(to_replace + "/", '')
        real_envolved_commit = CommitAnalyzer.filter_false_envolved_commit(discendent_non_merge_commits, filename)
        print(f"{file} envoles {len(real_envolved_commit)} commit!")
        sel_commits.extend(real_envolved_commit)
    finally:
        if repo:
            del repo
        gc.collect()
sorted_commits = sorted(sel_commits, key=lambda commit: commit.committer_date)
# print(f"Number of commits that envolve webguitests are: {len(sel_commits)}")
print(f"First commit about a webguitest: {sorted_commits[0].committer_date}")
