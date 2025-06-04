import concurrent
import errno
import os
import shutil
import stat
import re
import subprocess
from pathlib import Path
import pandas as pd
from CommitAnalyzer.CommitMessageAnalyzer_perf import CommitMessageAnalyzerPerf
from RepositoryAnalyzer.RepositoryCloner import Cloner
from pydriller import Repository,ModificationType

class PBTRepositoryAnalyzer:

    repos = ['chomechome/granula','damicoedoardo/recval']

    @staticmethod
    def enable_git_long_paths():
        try:
            # Enable long paths in Git for the current user
            subprocess.run(['git', 'config', '--global', 'core.longpaths', 'true'], check=True)
            print("Enabled long paths in Git for the current user.")
        except subprocess.CalledProcessError as e:
            print(f"Error enabling long paths in Git: {e}")
            exit(1)

    @staticmethod
    def rename_dir(old_name, new_name):
        # Assicurati che il nuovo percorso non esista già
        if not os.path.exists("../clone/" + new_name):
            # Rinomina la directory
            os.rename( "../clone/"+ old_name,
                      "../clone/"+ new_name)
        else:
            print(f"Error: Directory already exists.")

    @staticmethod
    def handle_remove_readonly(func, path, exc):
        excvalue = exc[1]
        if func in (os.rmdir, os.remove, os.unlink) and excvalue.errno == errno.EACCES:
            os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
            func(path)
        else:
            raise

    @staticmethod
    def  clear_directory(directory_path):
        if not os.path.exists(directory_path):
            print(f"Directory {directory_path} does not exist, nothing to clear.")
            return

        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path, ignore_errors=False, onerror=PBTRepositoryAnalyzer.handle_remove_readonly)
                else:
                    os.remove(item_path)
            except Exception as e:
                print(f"Error removing {item_path}: {e}")
        print('Folder succesfully cleaned!')


    @staticmethod
    def empty_recycle_bin():
        try:
            # Chiama l'API di Windows per svuotare il cestino
            # ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 1)
            PBTRepositoryAnalyzer.clear_directory("/home/sergio/.local/share/Trash/files")
            print("Cestino svuotato con successo.")
        except Exception as e:
            print(f"Errore durante lo svuotamento del cestino: {e}")

    @staticmethod
    def check_pbt_file(file_path,source_code,is_source_code):
        if not is_source_code:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                    # Check if hypothesis is imported
                    has_hypothesis = bool(re.search(r"^\s*(import|from)\s+hypothesis", content, re.MULTILINE))

                    # Count occurrences of @given
                    given_count = len(re.findall(r"@\w*\.?given\(", content))

                    return has_hypothesis, given_count
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                return False, 0
        else:
            content = source_code
            #print(content)
            # Check if hypothesis is imported
            has_hypothesis = bool(re.search(r"^\s*(import|from)\s+hypothesis", content, re.MULTILINE))

            # Count occurrences of @given
            given_count = len(re.findall(r"@\w*\.?given\(", content))

            return has_hypothesis, given_count


    @staticmethod
    def analyze_test_history(data_res, cloned_repository,repo_name,repofile_path):
        repo = Repository(cloned_repository, filepath=repofile_path)
        file_commit_involved = list(repo.traverse_commits())
        non_merge_commits = [commit for commit in file_commit_involved if not commit.merge]
        discendent_non_merge_commits = sorted(non_merge_commits, key=lambda c: c.committer_date, reverse=True)
        print(f'sorted_commit :{len(discendent_non_merge_commits)}')
        filename = str(repofile_path).replace("\\", '/')
        filename = filename.replace(cloned_repository+"/", '')
        real_envolved_commit, mods = CommitMessageAnalyzerPerf.get_realcommit_envolved_and_modification(
            discendent_non_merge_commits, filename)

        combined = list(zip(real_envolved_commit, mods))

        # Sort using committer_date from real_envolved_commit
        sorted_combined = sorted(combined, key=lambda c: c[0].committer_date)

        # Unzip into separate lists
        real_envolved_commit_sorted, mods_sorted = zip(*sorted_combined)

        # Convert back to lists if needed
        real_envolved_commit_sorted = list(real_envolved_commit_sorted)
        mods_sorted = list(mods_sorted)

        print(f"{repofile_path} envoles {len(real_envolved_commit)} commit!")
        source_code_before=''
        commit_hash_before=''
        for index, commit in enumerate(real_envolved_commit_sorted):
            type =mods_sorted[index].change_type
            if index == 0 and type == ModificationType.ADD:
                if mods_sorted[index].source_code is not None:
                    has_hypothesis, given_count = PBTRepositoryAnalyzer.check_pbt_file(None, mods_sorted[index].source_code,True)
                    if has_hypothesis and given_count > 0:
                        data_res['repo'].append(repo_name)
                        data_res['test'].append(filename)
                        data_res['source_code_before'].append(source_code_before)
                        data_res['source_code_after'].append(mods_sorted[index].source_code)
                        data_res['commit_before'].append(commit_hash_before)
                        data_res['commit_after'].append(commit.hash)
                        data_res['commit_message_after'].append(commit.msg)
                        data_res['given_count'].append(given_count)
                        data_res['label'].append('')
                        data_res['manually_check_required'].append(False)
                        data_res['introduced_later'].append(False)
                        return
                    else:
                        commit_hash_before =commit.hash
                        source_code_before= mods_sorted[index].source_code
            elif index == 0 and type == ModificationType.RENAME:
                if mods_sorted[index].source_code is not None:
                    has_hypothesis, given_count = PBTRepositoryAnalyzer.check_pbt_file(None,mods_sorted[index].source_code,True)
                    if has_hypothesis and given_count > 0:
                        data_res['repo'].append(repo_name)
                        data_res['test'].append(filename)
                        data_res['source_code_before'].append(source_code_before)
                        data_res['source_code_after'].append(mods_sorted[index].source_code)
                        data_res['commit_before'].append(commit_hash_before)
                        data_res['commit_after'].append(commit.hash)
                        data_res['commit_message_after'].append(commit.msg)
                        data_res['given_count'].append(given_count)
                        data_res['label'].append('')
                        data_res['manually_check_required'].append(True)
                        data_res['introduced_later'].append('')
                        return

            else:
                if mods_sorted[index].source_code is not None:
                    has_hypothesis, given_count = PBTRepositoryAnalyzer.check_pbt_file(None, mods_sorted[index].source_code,True)
                    if has_hypothesis and given_count > 0:
                        data_res['repo'].append(repo_name)
                        data_res['test'].append(filename)
                        data_res['source_code_before'].append(source_code_before)
                        data_res['source_code_after'].append(mods_sorted[index].source_code)
                        data_res['commit_before'].append(commit_hash_before)
                        data_res['commit_after'].append(commit.hash)
                        data_res['commit_message_after'].append(commit.msg)
                        data_res['given_count'].append(given_count)
                        data_res['label'].append('')
                        data_res['manually_check_required'].append(False)
                        data_res['introduced_later'].append(True)
                        return
                    else:
                        commit_hash_before = commit.hash
                        source_code_before = mods_sorted[index].source_code

    @staticmethod
    def analyze_repos(start,end,process_id):

        changes_over_time = {
            'repo': [],
            'test': [],
            'manually_check_required':[],
            'source_code_before':[],
            'source_code_after':[],
            'commit_before':[],
            'commit_after':[],
            'commit_message_after': [],
            'given_count': [],
            'introduced_later':[],
            'label':[]
        }

        for repository_to_analyze in PBTRepositoryAnalyzer.repos[start:end]:
            path_folder_clone =f"/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/clone/"
            cloner = Cloner(path_folder_clone)
            cloner.clone_repository(repository_to_analyze)
            original_name = repository_to_analyze.replace('/', '\\')
            new_name = repository_to_analyze.replace('/', '_')
            print(f"Dir renamed: {original_name} -> {new_name}")
            PBTRepositoryAnalyzer.rename_dir(original_name, new_name)
            repo_path = Path(path_folder_clone+""+new_name)  # Change this
            python_files = list(repo_path.rglob("*.py"))
            for py_file in python_files:
                has_hypothesis, given_count=PBTRepositoryAnalyzer.check_pbt_file(py_file,None,False)
                if has_hypothesis==True and given_count> 0:
                    print(py_file)
                    PBTRepositoryAnalyzer.analyze_test_history(changes_over_time,path_folder_clone+""+new_name,repository_to_analyze,py_file)

            PBTRepositoryAnalyzer.clear_directory(f"../clone/")
            PBTRepositoryAnalyzer.empty_recycle_bin()
        df = pd.DataFrame(changes_over_time)
        df.to_csv('pbt_files_changes'+str(process_id)+'.csv', index=False)

    @staticmethod
    def run_parallel_analysis():
        project_ranges = [
            [0,1],
            [1,2]
        ]
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = {
                executor.submit(PBTRepositoryAnalyzer.analyze_repos, start, end, i): i
                for i, (start, end) in enumerate(project_ranges)
            }

            for future in concurrent.futures.as_completed(futures):
                process_id = futures[future]  # Get process index
                try:
                    result = future.result()  # Get process result
                    print(f"Process {process_id} finished: {result}")
                except Exception as exc:
                    print(f"Process {process_id} encountered an error: {exc}")



if __name__ == "__main__":
    #CommitAnalyzerPerf.run_parallel_analysis()
    PBTRepositoryAnalyzer.run_parallel_analysis()

