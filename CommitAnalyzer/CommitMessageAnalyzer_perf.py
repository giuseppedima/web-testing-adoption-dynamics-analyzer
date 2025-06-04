import concurrent
import gc
import os
import time

from CommitAnalyzer.commitAnalyzer_perf import CommitAnalyzerPerf
from Dataset.DBconnector import Session, engine
from Dataset.Repository import PerformanceTestingTestDetails
from ProjectAnalyzer.JSTS.JavascriptDataAnalyzer import JavascriptDataAnalyzer
from RepositoryAnalyzer.RepositoryCloner import Cloner
from pydriller import Repository, ModificationType
import pandas as pd

class CommitMessageAnalyzerPerf:

    missed_repo =['codice/ddf']



    @staticmethod
    def get_tests_path():
        try:
            session = Session(bind=engine)
            print("Connection successful!")

            # Query con distinct su test_path
            records = session.query(PerformanceTestingTestDetails.test_path)\
                .distinct(PerformanceTestingTestDetails.test_path)\
                .all()
            return records

        except Exception as e:
            print(f"Error connecting to the database: {e}")

        finally:
            session.close()  # Assicurati che la sessione venga chiusa dopo l'uso

    @staticmethod
    def get_realcommit_envolved_and_modification(sorted_commits,filename):
        real_envolved_commit = []
        mods = []
        current_filename = filename
        for i in range(len(sorted_commits)):
            commit = sorted_commits[i]
            found = False
            for modification in commit.modified_files:
                type = modification.change_type
                path = modification.new_path
                old_name = modification.old_path
                if type == ModificationType.ADD:
                    if path == current_filename:
                        found = True
                        mods.append(modification)
                        break
                elif type == ModificationType.DELETE:
                    if old_name == current_filename:
                        found = True
                        mods.append(modification)
                        break
                elif type == ModificationType.MODIFY:
                    if path == current_filename:
                        found = True
                        mods.append(modification)
                        break
                elif type == ModificationType.RENAME:
                    if  path == current_filename:
                        found = True
                        mods.append(modification)
                        current_filename = old_name
                        break
            if found:
                real_envolved_commit.append(commit)
        return real_envolved_commit,mods


    @staticmethod
    def get_commit_message_of_perf_test(repo_name,map,data_res,hash):
        JavascriptDataAnalyzer.enable_git_long_paths()
        path_folder_clone = f"/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/clone"
        cloner = Cloner(path_folder_clone)
        cloner.clone_repository(repo_name)
        original_name = repo_name.replace('/', '\\')
        new_name = repo_name.replace('/', '_')
        print(f"rename dir: {original_name} -> {new_name}")
        JavascriptDataAnalyzer.rename_dir(original_name, new_name)
        cloned_repository = path_folder_clone + "/" + new_name
        #repo_gitpy = git.Repo(cloned_repository)
        #repo_gitpy.git.checkout(hash)
        files_name = map[repo_name]
        print(f"The repo {repo_name} has {len(files_name)} number of performance test files.")
        sel_commits = []
        for file in files_name:
            try:
                repo_name = repo_name.strip()
                file = file.strip()
                new_file_name = file.replace('\\', '/')
                new_file_name = new_file_name.replace(repo_name, repo_name.replace('/', '_'))
                new_file_name = '/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/clone' + new_file_name

                repo = Repository(cloned_repository, filepath=new_file_name)
                file_commit_involved = list(repo.traverse_commits())
                non_merge_commits = [commit for commit in file_commit_involved if not commit.merge]
                discendent_non_merge_commits = sorted(non_merge_commits, key=lambda c: c.committer_date, reverse=True)
                #sorted_commits = sorted(discendent_non_merge_commits, key=lambda commit: commit.committer_date)
                print(f'lunghezza sorted_commit :{len(discendent_non_merge_commits)}')
                filename = file.replace("\\", '/')
                filename = filename.replace("/" + repo_name + "/", '')
                real_envolved_commit,mods = CommitMessageAnalyzerPerf.get_realcommit_envolved_and_modification(discendent_non_merge_commits, filename)
                print(f"{file} envoles {len(real_envolved_commit)} commit!")

                for index, commit in enumerate(real_envolved_commit,start=1):
                    data_res['repo'].append(repo_name)
                    data_res['test'].append(file)
                    data_res['index'].append(index)
                    data_res['commit date'].append(commit.committer_date)
                    data_res['change type'].append(mods[index-1].change_type)
                    data_res['diff'].append(mods[index-1].diff)
                    data_res['commit message'].append(commit.msg)

            finally:
                if repo:
                    del repo
                gc.collect()



    @staticmethod
    def analyze_projects(start, end):
        data_res = {
            'repo':[],
            'test':[],
            'index':[],
            'commit date':[],
            'change type':[],
            'diff': [],
            'commit message': []
        }
        records = CommitAnalyzerPerf.get_repos_and_perf_test()
        map = CommitAnalyzerPerf.create_repo_test_map(records)
        #keys = list(map.keys())  # Ottieni le chiavi come lista
        #for repo in keys:  # Itera sulle chiavi nell'intervallo start:end
        for repo in CommitMessageAnalyzerPerf.missed_repo[0:1]:
            start_time = time.time()  # Starting time
            CommitMessageAnalyzerPerf.get_commit_message_of_perf_test(repo,map,data_res,hash)
            path_folder_clone = f"/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/clone"
            new_name = repo.replace('/', '_')
            #CommitAnalyzerPerf.clear_directory(path_folder_clone + "/" + new_name)
            CommitAnalyzerPerf.empty_recycle_bin()
            #perf_rep,rep_rep = CommitAnalyzerPerf.get_commit_hash_by_reponame(repo)
            #print(perf_rep)
            #print(rep_rep)

        end_time = time.time()  # Tempo di fine
        execution_time = end_time - start_time  # Time taken
        print(f"Time taken : {execution_time:.6f}s")
        df = pd.DataFrame(data_res)
        df.to_csv('commit_message_perf_tests_missed.csv',index=False)


    @staticmethod
    def run_parallel_analysis():
        # range progetti da analizzare
        project_ranges = [
            [1,2]
        ]
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = [executor.submit(CommitMessageAnalyzerPerf.analyze_projects, start, end) for start, end in
                       project_ranges]
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()  # Recupera il risultato del processo
                    print("Analisi completata per un batch.")
                except Exception as exc:
                    print(f"Si è verificato un errore durante l'analisi: {exc}")


    @staticmethod
    def check_missed_message_analysis_repo():
        repos = []
        records = CommitAnalyzerPerf.get_repos_and_perf_test()
        map = CommitAnalyzerPerf.create_repo_test_map(records)
        keys = list(map.keys())  # Ottieni le chiavi come lista

        df = pd.read_csv('/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/CommitAnalyzer/commit_message_perf_tests.csv')
        column_to_iterate = df['repo']
        for current_repo in column_to_iterate:
            if current_repo not in repos:
                repos.append(current_repo)
        print(f" le repo totalis sono: {len(repos)}")

        for repo in keys:
            if repo not in repos:
                print(f"{repo} not analyzed!")


    @staticmethod
    def check_missed_repo():
        folder = '/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/ICSME/performance_test_commit_analysis/'
        records = CommitAnalyzerPerf.get_repos_and_perf_test()
        repo_map = CommitAnalyzerPerf.create_repo_test_map(records)
        keys = list(repo_map.keys())  # Get the keys as a list
        print(len(keys))

        for index, repo in enumerate(keys,start=1):
            new_name = repo.replace('/', '_')
            if not os.path.exists(folder + '/' + new_name):  # Fixed the syntax error here
                print(f'[{index}]. {repo} not analyzed!')



    @staticmethod
    def get_repo_changes_byfolder():
        res= []
        records = CommitAnalyzerPerf.get_repos_and_perf_test()
        map = CommitAnalyzerPerf.create_repo_test_map(records)
        keys = list(map.keys())  # Ottieni le chiavi come lista
        prefix= f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/ICSME/performance_test_commit_analysis/'
        for repo_name in keys:
            new_name = repo_name.replace('/','_')
            folder_change = prefix+''+new_name+'/test_changes/'
            if os.path.exists(folder_change):
                files = []
                for file in os.listdir(folder_change):
                    files.append(file)
                res.append({
                    'repo':repo_name,
                    'changes':len(files)
                })
            else:
                print(f'{folder_change} doesnt exist!')
        return res

    @staticmethod
    def get_num_changes_by_reponame(repo_name):
        df = pd.read_csv('/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/CommitAnalyzer/commit_message_perf_tests_new.csv')
        df_filtered = df[(df['repo'] == repo_name) & (df['change type'] != 'ModificationType.RENAME')]

        return df_filtered


    @staticmethod
    def create_csv_to_labeling():
        df = pd.read_csv('/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/CommitAnalyzer/commit_message_perf_tests.csv')
        print(f'size {df.shape[0]}')
        #df_filtered = df[df['index']!=1]
        #df_filtered['label']=''
        #df_filtered.to_csv('prova.csv',index=False)

    @staticmethod
    def check_new_csv():
        df = pd.read_csv('/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/CommitAnalyzer/commit_message_perf_tests_new.csv')
        print(df.shape[0])
        #df_filtered = df[df['change type']=="ModificationType.ADD"]
        test_list = df["test"].unique()
        '''
        for index,row in df_filtered.iterrows():
            print(f'{row["test"]} {row["index"]}')
        '''
        return [s.strip() for s in test_list]




    @staticmethod
    def check(map):
        diff= 0
        for couple in map:
            repo_name= couple['repo']
            num_changes= couple['changes']
            df_filtered = CommitMessageAnalyzerPerf.get_num_changes_by_reponame(repo_name)
            file_num_changes =df_filtered.shape[0]
            if num_changes != file_num_changes:
                print(f'[{repo_name}] folder: {num_changes}  file csv: {file_num_changes} diversi!!')
                diff+=(num_changes-file_num_changes)
        print(f'diff ={diff}')

    @staticmethod
    def is_in(list,item_to_find):
        for item in list:
            if item == item_to_find:
                return True
        return False

    @staticmethod
    def fill_already_labeled_changes():
        old = pd.read_csv('/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/CommitAnalyzer/changes_to_analyze.csv')
        found = 0
        new = pd.read_csv('/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/CommitAnalyzer/changes_to_analyze_new.csv')

        new["label"] = ""

        matching_columns = ["repo", "test", "commit date", "change type","commit message"]

        for new_index, new_row in new.iterrows():
            new_repo = new_row['repo']
            new_test = new_row['test']
            new_commit_date = new_row['commit date']
            new_change_type = new_row['change type']
            new_commit_message = new_row['commit message'].strip()
            for old_index, old_row in old.iterrows():
                old_repo = old_row['repo']
                old_test = old_row['test']
                old_commit_date = old_row['commit date']
                old_change_type = old_row['change type']
                old_commit_message = old_row['commit message'].strip()
                if new_repo==old_repo and new_test == old_test and new_commit_date == old_commit_date and new_change_type == old_change_type and new_commit_message == old_commit_message:
                    print(f'{new_row["repo"]}, {new_row["test"]}, {new_row["commit date"]}')
                    print('---')
                    new.at[new_index, "label"] = old_row["label"]
                    found+=1

        print(f'trovate :{found}')
        new.to_csv('/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/CommitAnalyzer/changes_to_analyze_new_merged.csv',index=False)





if __name__ == "__main__":
    CommitMessageAnalyzerPerf.run_parallel_analysis()
    #CommitMessageAnalyzerPerf.check_missed_repo()
    #CommitMessageAnalyzerPerf.create_csv_to_labeling()
    #res = CommitMessageAnalyzerPerf.get_repo_changes_byfolder()
    #CommitMessageAnalyzerPerf.check(res)
    #CommitMessageAnalyzerPerf.fill_already_labeled_changes()
    #df  = pd.read_csv('/home/sergio/PycharmProjects/ICSME-be/changes_to_analyze_new_merged.csv')
    # Clean the 'label' column by stripping spaces and converting to string (if needed)
    #df['label'] = df['label'].str.strip().fillna('')
    # Now apply the filtering
    #df_filtered = df[df['label'] != '']

    # Print the shapes
    #print(df.shape[0])  # Original number of rows
    #print(df_filtered.shape[0])