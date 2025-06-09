import concurrent.futures
'''
import errno
import gc
import os.path
import shutil
import stat
import time
import warnings
'''
from pathlib import Path
'''
from pandas.errors import PerformanceWarning

from Dataset.Repository import GUITestingRepoDetails,RepositoryModel, GUITestingTestDetails
from ProjectAnalyzer.JSTS.JavascriptDataAnalyzer import JavascriptDataAnalyzer
import os.path
'''
import pandas as pd
from pydriller import Repository
from datetime import datetime
'''
from pydriller import ModificationType
from Dataset.DBconnector import Session, engine
'''
from RepositoryAnalyzer.RepositoryCloner import Cloner


class CommitAnalyzer:
    '''
    warnings.simplefilter(action='ignore', category=PerformanceWarning)
    java_analysis_folder = '../data/java_test_analysis'
    js_ts_analysis_folder = '../data/js_ts_test_analysis'
    py_analysis_folder = '../data/py_test_analysis'
    missed_repo_folder = '../data/missed_repo'

    file_extensions_to_consider = ['.java', '.js', '.ts', '.py', '.html', '.css', '.jsx', '.tsx', '.scss', '.sass', '.vue', '.jsp', '.xhtml']

    max_rows_excel = 1048576  # excel's row limitations
    max_cols_excel = 16384  # excel's column limitations


    @staticmethod
    def filter_false_envolved_commit(sorted_commits,filename):
        real_envolved_commit = []
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
    def get_repo_with_number_of_test_lower_than_n(n):
        try:
            session = Session(bind=engine)
            print("Connection successful!")

            records = session.query(RepositoryModel, GUITestingRepoDetails).join(
                GUITestingRepoDetails,
                RepositoryModel.name == GUITestingRepoDetails.repository_name
            ).filter(
                GUITestingRepoDetails.number_of_tests <= n
            ).all()

            return records
        except Exception as e:
            print(f"Error connecting to the database: {e}")
        finally:
            session.close()

    @staticmethod
    def get_first_available_row(df):
        non_empty_rows = df[0].dropna()  # Trova tutte le righe non vuote nella colonna 'File Name'
        return len(non_empty_rows) + 1  # La prima riga disponibile è dopo l'ultima non vuota


    @staticmethod
    def create_history_excel_file(repo_name,commits):
        df = pd.DataFrame()
        df.at[0,0]="FilePath"

        for i in range(len(commits)):
            try:
                committer_date = commits[i].committer_date.strftime("%Y-%m-%d %H:%M:%S")
                df.at[0,i+1] = f"Commit {i + 1} ({committer_date})"
            except Exception as e:
                print(f"Error processing commit {i + 1}: {e}")
                continue

        for i in range(len(commits)):
            try:
                commit = commits[i]
                for modification in commit.modified_files:
                    type = modification.change_type
                    path = modification.new_path
                    old_name = modification.old_path
                    if (type != ModificationType.DELETE and CommitAnalyzer.has_extension(path)) or (type == ModificationType.DELETE and CommitAnalyzer.has_extension(old_name)):
                        if type  == ModificationType.ADD:
                            row_idx = CommitAnalyzer.get_first_available_row(df)  # Trova la prima riga disponibile
                            df.at[row_idx, 0] = path
                            df.at[row_idx,i+1] = 'A'
                        elif type == ModificationType.DELETE:
                            path = modification.old_path
                            file_row_idx = df.index[df[0]==path].tolist()
                            if file_row_idx:
                                row_idx = file_row_idx[0]
                                df.at[row_idx,i+1]='D'
                            else:
                                row_idx = CommitAnalyzer.get_first_available_row(df)  # Trova la prima riga disponibile
                                df.at[row_idx, 0] = path
                                df.at[row_idx, i + 1] = 'D'
                        elif type == ModificationType.RENAME:
                            file_row_idx = df.index[df[0] == old_name].tolist()
                            if file_row_idx:
                                row_idx = file_row_idx[0]
                                df.at[row_idx, i + 1] = 'R('+old_name+")"
                                df.at[row_idx,0] = path
                            else:
                                row_idx = CommitAnalyzer.get_first_available_row(df)  # Trova la prima riga disponibile
                                df.at[row_idx, 0] = path
                                df.at[row_idx, i + 1] = 'R('+old_name+")"
                        elif type == ModificationType.MODIFY:
                            total_lines = len(modification.source_code.splitlines()) if modification.source_code else 0
                            lines_changed = modification.added_lines + modification.deleted_lines
                            if total_lines > 0:
                                percentage_change = (lines_changed / total_lines) * 100
                            else:
                                percentage_change = 100  # Se non ci sono righe precedenti, considera il cambiamento come 100%

                            modification_str = f'M({int(percentage_change)})'
                            file_row_idx = df.index[df[0] == path].tolist()
                            if file_row_idx:
                                row_idx = file_row_idx[0]
                                df.at[row_idx, i + 1] = modification_str
                            else:
                                row_idx = CommitAnalyzer.get_first_available_row(df)  # Trova la prima riga disponibile
                                df.at[row_idx, 0] = path
                                df.at[row_idx, i + 1] = modification_str
            except Exception as e:
                print(f"Error processing modification in commit {i + 1}: {e}")
                continue
        return df



    @staticmethod
    def get_file_history(commits,file_path):
        for commit in commits:
            # Ottenere le modifiche relative ai file nel commit
            for modification in commit.modified_files:
                print(f"Commit: {commit.hash}")
                print(f"Data: {commit.committer_date}")
                print(f"Tipo di cambiamento: {modification.change_type}")  # Aggiunta, Modifica, Rimozione, etc.
                if modification.change_type == ModificationType.RENAME:
                    print(f"Vecchio nome: {modification.old_path}")  # Nome precedente
                    print(f"Nuovo nome: {modification.filename}")  # Nome nuovo
                else:
                    print(f"Path: {modification.filename}")
                print('---')

    @staticmethod
    def get_files_in_commit(commit):
        tree = commit.tree
        file_paths = []

        for blob in tree.traverse():
            if blob.type == 'blob':
                file_paths.append(blob.path)
        return  file_paths

    @staticmethod
    def get_tests_by_repo_name(repo_name):
        try:
            session = Session(bind=engine)
            print("Connection successful!")
            records = session.query(GUITestingTestDetails).filter(
                GUITestingTestDetails.repository_name == repo_name
            ).all()

            return records
        except Exception as e:
            print(f"Error connecting to the database: {e}")
        finally:
            session.close()


    @staticmethod
    def get_commits_before_the_first_webgui(all_commits, first_guiweb_commit):
        previous_commit = 0
        for i in range(len(all_commits)):
            if all_commits[i].hash == first_guiweb_commit.hash:
                return  all_commits[previous_commit:]
            previous_commit = i
    @staticmethod
    def get_all_commits_sorted(repo,repo_name):
        all_commits = list(repo.traverse_commits())
        non_merge_commits = [commit for commit in all_commits if not commit.merge]
        sorted_non_merge_commits = sorted(non_merge_commits, key=lambda commit: commit.committer_date)
        print(f"First commit was : {sorted_non_merge_commits[0].committer_date}")
        print(f"The repo {repo_name} has : {len(all_commits)} commits overall!")
        return sorted_non_merge_commits
    @staticmethod
    def get_all_guiweb_commits_sorted(repo_path,tests,repo_name):
        prefix = '/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/clone'
        # Add the prefix
        full_paths = [f"{prefix}{path}" for path in tests]
        print(f"The repo {repo_name} has {len(tests)} number of e2e test files.")
        sel_commits = []
        for file in full_paths:
            try:
                repo = Repository(repo_path, filepath = file)
                file_commit_involved = list(repo.traverse_commits())
                non_merge_commits = [commit for commit in file_commit_involved if not commit.merge]
                discendent_non_merge_commits = sorted(non_merge_commits, key=lambda c: c.committer_date, reverse=True)
                to_replace = '/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/clone/'+ repo_name.replace('/', '_')
                filename = file.replace(to_replace + "/", '')
                real_envolved_commit = CommitAnalyzer.filter_false_envolved_commit(discendent_non_merge_commits,filename)
                print(f"{file} envoles {len(real_envolved_commit)} commit!")
                sel_commits.extend(real_envolved_commit)
            finally:
                if repo:
                    del repo
                gc.collect()
        sorted_commits = sorted(sel_commits, key=lambda commit: commit.committer_date)
        print(f"Number of commits that envolve webguitests are: {len(sel_commits)}")
        print(f"First commit about a webguitest: {sorted_commits[0].committer_date}")
        return sorted_commits

    @staticmethod
    def build_list_tests(tests):
        list = []
        for test in tests:
            list.append(test.test_path)
        return list

    @staticmethod
    def get_commits_by_filepath(repo_name,commit_sha,tests):
        JavascriptDataAnalyzer.enable_git_long_paths()
        path_folder_clone = f"../clone"
        cloner = Cloner(path_folder_clone)
        cloner.clone_repository(repo_name,commit_sha)
        original_name = repo_name.replace('/', '\\')
        new_name = repo_name.replace('/', '_')
        print(f"rename dir: {original_name} -> {new_name}")
        JavascriptDataAnalyzer.rename_dir(original_name, new_name)
        cloned_repository = path_folder_clone + "/" + new_name
        repo = Repository(cloned_repository)
        sorted_all_commits = CommitAnalyzer.get_all_commits_sorted(repo,repo_name)
        sorted_webgui_commits = CommitAnalyzer.get_all_guiweb_commits_sorted(cloned_repository,tests,repo_name)
        print(sorted_all_commits[0].committer_date)
        print(sorted_webgui_commits[0].committer_date)
        new_row = {
            sorted_all_commits[0].committer_date,
            sorted_webgui_commits[0].committer_date
        }
        first_commit_df = pd.read_csv('/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ1/adoption-gui.csv')
        df_res = pd.concat([first_commit_df,pd.DataFrame([new_row])],ignore_index=True)
        df_res.to_csv('/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ1/adoption-gui.csv',index=False)
        commits_to_analyze = CommitAnalyzer.get_commits_before_the_first_webgui(sorted_all_commits,sorted_webgui_commits[0])
        print(f'commit to analyze[{len(commits_to_analyze)}] {commits_to_analyze[0].committer_date} -> {commits_to_analyze[len(commits_to_analyze)-1].committer_date}')
        df = CommitAnalyzer.create_history_excel_file(repo_name,commits_to_analyze)
        return df

    @staticmethod
    def split_appcommit_guiweb_commit(df,paths_to_prioritize):
        print(paths_to_prioritize)
        df_new = pd.DataFrame()
        df_new = pd.concat([df_new, df.iloc[0:1]], ignore_index=True)
        for index, row in df.iterrows():
            if row.iloc[0] in paths_to_prioritize.values:
                df_new = pd.concat([df_new, row.to_frame().T], ignore_index=True)

        # remove the guiwebtest rows from the first dataframe
        df = df[~df.iloc[:, 0].isin(paths_to_prioritize.values)]
        return df,df_new


    @staticmethod
    def has_extension(filepath):
        return any(filepath.endswith(ext) for ext in CommitAnalyzer.file_extensions_to_consider)

    @staticmethod
    def get_gui_span(df):
        spans = []
        commits = []
        current_span = []
        df.columns = df.iloc[0]
        df = df[1:]
        for col in df.columns[1:]:
            if not df[col].isna().all():
                current_span.append(col)
                commits.append(col)
            else:
                if current_span and len(current_span) > 1:
                    spans.append(current_span.copy())
                current_span.clear()
        if current_span and len(current_span) > 1:
            spans.append(current_span)

        return spans, commits

    @staticmethod
    def get_app_span(df, commit):
        spans = []
        commits = []
        current_span = []
        df.columns = df.iloc[0]
        df = df[1:]
        for col in df.columns[1:]:
            if not df[col].isna().all():
                commits.append(col)
                if col not in commit:
                    current_span.append(col)
                else:
                    if current_span and len(current_span) > 1:
                        spans.append(current_span.copy())
                    current_span.clear()
            else:
                if current_span and len(current_span) > 1:
                    spans.append(current_span.copy())
                current_span.clear()
        return spans, commits
    @staticmethod
    def extract_date(commit_str):
        date_str = commit_str.split('(')[1].split(')')[0]  # Estrae la parte della data
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")  # Converte la stringa in oggetto datetime
    @staticmethod
    def calculate_number_of_commits_between_two_dates(current_blob_commits, commits):
        first_data = CommitAnalyzer.extract_date(current_blob_commits[0])
        last_date = CommitAnalyzer.extract_date(current_blob_commits[-1])
        count = 0
        for commit in commits:
            commit_date = CommitAnalyzer.extract_date(commit)
            if first_data <= commit_date <= last_date:
                count+=1
        return count

    @staticmethod
    def create_excel_with_test_lifecycle_metrics(outputfile,df_gui,commits_app,commits_gui):
        #columns : test(blob), svday,svmod, svac, svsc
        data = []
        for index,row in df_gui.iterrows():
            number_of_blobs = 0
            current_blob_commits = []
            filepath = row.iloc[0]
            for i in range(1,len(row)):
                value = row.iloc[i]
                current_commit = df_gui.columns[i]
                if pd.notna(value):
                    if value == 'A':
                        #we could meet A just when number_of_blobs is 0
                        current_blob_commits.append(current_commit)
                    elif value == 'D':
                        mod = len(current_blob_commits)
                        current_blob_commits.append(current_commit)
                        data.append([filepath+'_('+str(number_of_blobs)+")",
                                     CommitAnalyzer.calculate_days(current_blob_commits.copy()),
                                      mod,
                                     CommitAnalyzer.calculate_number_of_commits_between_two_dates(current_blob_commits,commits_app),
                                     CommitAnalyzer.calculate_number_of_commits_between_two_dates(current_blob_commits,commits_gui)])
                        current_blob_commits.clear()
                        number_of_blobs+=1
                    elif value.startswith('R'):
                        current_blob_commits.append(current_commit)
                    elif value.startswith('M'):
                        number = int(value[value.index("(")+1:value.index(")")])
                        if number< 44: # 66% of code not modified
                            current_blob_commits.append(current_commit)
                        else: # equals to D
                            mod = len(current_blob_commits)
                            current_blob_commits.append(current_commit)
                            data.append([filepath + '_(' + str(number_of_blobs) + ")",
                                         CommitAnalyzer.calculate_days(current_blob_commits.copy()),
                                         mod,
                                         CommitAnalyzer.calculate_number_of_commits_between_two_dates(current_blob_commits,commits_app),
                                         CommitAnalyzer.calculate_number_of_commits_between_two_dates(current_blob_commits,commits_gui)])
                            current_blob_commits.clear()
                            current_blob_commits.append(current_commit) #like A
                            number_of_blobs += 1
            if current_blob_commits:
                mod = len(current_blob_commits)
                current_blob_commits.append(current_commit)
                data.append([filepath + '_(' +str(number_of_blobs) + ")",
                             CommitAnalyzer.calculate_days(current_blob_commits.copy()),
                             mod,
                             CommitAnalyzer.calculate_number_of_commits_between_two_dates(current_blob_commits,commits_app),
                             CommitAnalyzer.calculate_number_of_commits_between_two_dates(current_blob_commits,commits_gui)])
                current_blob_commits.clear()
        df = pd.DataFrame(data, columns=["testpath(blob)", "svday", "svmod","svac","svsc"])
        df.to_excel(outputfile +'_tests_lifecycle_analysis.xlsx', index=False)



    @staticmethod
    def calculate_days(span):
        dates = []
        for commit in span:
            date_str = commit.split('(')[1].strip(')')
            date_obj = datetime.strptime(date_str,'%Y-%m-%d %H:%M:%S')
            dates.append(date_obj)
        if dates:
            delta_days = (max(dates)-min(dates)).days
            if delta_days == 0:
                delta_days=1
        else:
            delta_days = 0

        return  delta_days

    @staticmethod
    def create_excel_with_span_metrics(outputfile,type,spans):
        data = []
        for span in spans:
            span_str =  ', '.join(span)
            commit_count = len(span)
            days = CommitAnalyzer.calculate_days(span)
            data.append([span_str,commit_count,days])
        df = pd.DataFrame(data,columns=["span","commit","days"])
        df.to_excel(outputfile+'_'+type+'_span_analysis.xlsx',index=False)

    @staticmethod
    def calculate_commit_test_metrics(df_app,df_gui,repo_name):
        new_name = repo_name.replace('/', '_')
        commits_analyzed_file = '../webguirepo_commit_analysis/'+new_name+ '/commits_analysis' + new_name
        #calculate spans
        spans_gui, commits_gui = CommitAnalyzer.get_gui_span(df_gui)
        spans_app, commits_app = CommitAnalyzer.get_app_span(df_app, commits_gui)

        print(f" spans_gui : {len(spans_gui)} commits : {len(commits_gui)} ")
        print(f" spans_app : {len(spans_app)} commits : {len(commits_app)} ")

        CommitAnalyzer.create_excel_with_span_metrics(commits_analyzed_file,'gui',spans_gui)
        CommitAnalyzer.create_excel_with_span_metrics(commits_analyzed_file,'app',spans_app)

        CommitAnalyzer.create_excel_with_test_lifecycle_metrics(commits_analyzed_file, df_gui, commits_app, commits_gui)


    @staticmethod
    def empty_recycle_bin():
        try:
            CommitAnalyzer.clear_directory("/home/sergio/.local/share/Trash/files")
            print("Cestino svuotato con successo.")
        except Exception as e:
            print(f"Errore durante lo svuotamento del cestino: {e}")

    @staticmethod
    def handle_remove_readonly(func, path, exc):
        excvalue = exc[1]
        if func in (os.rmdir, os.remove, os.unlink) and excvalue.errno == errno.EACCES:
            os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
            func(path)
        else:
            raise

    @staticmethod
    def clear_directory(directory_path):
        if not os.path.exists(directory_path):
            print(f"Directory {directory_path} does not exist, nothing to clear.")
            return
        try:
            shutil.rmtree(directory_path)
            print(f"Folder '{directory_path}' deleted successfully!.")
        except Exception as e:
            print(f"Error during the folder {directory_path} deletion: {e}")

    
        # for item in os.listdir(directory_path):
        #     item_path = os.path.join(directory_path, item)
        #     try:
        #         if os.path.isdir(item_path):
        #             shutil.rmtree(item_path, ignore_errors=False, onerror=CommitAnalyzer.handle_remove_readonly)
        #         else:
        #             os.remove(item_path)
        #     except Exception as e:
        #         print(f"Error removing {item_path}: {e}")
        # print('Folder succesfully cleaned!')


    @staticmethod
    def save_df(df,directory,name):
        if df.shape[0] > CommitAnalyzer.max_rows_excel or df.shape[1] > CommitAnalyzer.max_cols_excel:
            csv_filename = directory+name+".csv"
            print(f"Data too large for Excel. Saving as CSV: {csv_filename}")
            df.to_csv(csv_filename, index=False, header=False)
        else:
            excel_filename= directory+name+".xlsx"
            print(f"Data saved as Excel. {directory+name}.xlsx")
            df.to_excel(excel_filename, index=False, header=False)
    '''	

    
    @staticmethod
    def get_repos_with_first_gui_testing_commit():
        input_file = Path(__file__).resolve().parent.parent / 'resources' / 'first_commit.xlsx'
        df = pd.read_excel(input_file, header=None)
        found_repos = []
        for row in df.itertuples(index=False):
            repo_name, commit_date = row[0], row[1]
            if pd.notna(repo_name) and pd.notna(commit_date):
                found_repos.append([repo_name.replace("_","/"), commit_date])
        return found_repos

    @staticmethod
    def get_repos_with_first_commit_that_introduces_a_framework():
        input_file = Path(__file__).resolve().parent.parent / 'resources' / 'frame_deps.xlsx'
        df = pd.read_excel(input_file, header=None)
        found_repos = []
        for row in df.itertuples(index=False):
            key = row[0]
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
    def execute_in_parallel(tasks, threads=10):

        futures = []
        with concurrent.futures.ProcessPoolExecutor(max_workers=threads) as executor:
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

            repo = Repository(path)
    
            commits = []
            
            for commit in repo.traverse_commits():
                # return n+1 commits
                if n >= 0 and commit.committer_date.replace(tzinfo=None) <= start_date:
                    commits.append(commit)
                    n -= 1

            # commits = sorted(commits, key=lambda c: c.committer_date, reverse=True)
            if not commits:
                raise ValueError(f"No commits found for repository {repository} at date {start_date}.")

            return commits

        except Exception as e:
            print(f"Error getting commits from repository {repository}: {e}")

    @staticmethod
    def migration_analysis():
   
        repos = CommitAnalyzer.get_repos_with_first_commit_that_introduces_a_framework()

        tasks=[]
        for repo in repos:
            for key, values in repo.items():
                for value in values:
                    print(f"Processing repository: {key} with commit date: {value['timestamp']}, frameworks: {value['frameworks']}")
                    tasks.append((CommitAnalyzer.get_previous_n_commits_starting_from_date, (key, value["timestamp"], 10)))

        all_commits = CommitAnalyzer.execute_in_parallel(
            tasks=tasks,
            threads=10
        )
        for commits in all_commits:
            if commits:
                for commit in commits:
                    print(f"Commit: {commit.hash} on {commit.committer_date}")
            else:
                print("No commits found for this repository.")     
        #TODO: store the results in a file
        #TODO: cleanup clone directories

    @staticmethod
    def adoption_analysis():

        repos = CommitAnalyzer.get_repos_with_first_gui_testing_commit()

        tasks=[]
        for repo, commit_date in repos:
            print(f"Processing repository: {repo} with first GUI testing commit date: {commit_date}")
            tasks.append((CommitAnalyzer.get_previous_n_commits_starting_from_date, (repo, commit_date, 10)))


        all_commits = CommitAnalyzer.execute_in_parallel(
            tasks=tasks,
            threads=10
        )
        for commits in all_commits:
            if commits:
                for commit in commits:
                    print(f"Commit: {commit.hash} on {commit.committer_date}")
            else:
                print("No commits found for this repository.")

        #TODO: store the results in a file
        #TODO: cleanup clone directories

        '''
        for repo, e2e_repo in repos[start:end]:
            print(f'{repo.name} and commit: {repo.last_commit} - {repo.last_commit_sha}')
            repo_name = e2e_repo.repository_name
            new_name = repo_name.replace('/', '_')
            directory = '../webguirepo_commit_analysis/' + new_name + "/"
            Path(directory).mkdir(parents=True, exist_ok=True)
            commits_analyzed_file = '../webguirepo_commit_analysis/' + new_name + '/commits_analysis' + new_name
            start_time = time.time() #Starting time
            tests = CommitAnalyzer.build_list_tests(CommitAnalyzer.get_tests_by_repo_name(repo_name))
            df = CommitAnalyzer.get_commits_by_filepath(repo_name,repo.last_commit_sha,tests)
            df,only_gui = CommitAnalyzer.split_appcommit_guiweb_commit(df,repo_name,tests)
            #perform metrics
            CommitAnalyzer.calculate_commit_test_metrics(df,only_gui,repo_name)
            #clear clone directory
            CommitAnalyzer.clear_directory(path_folder_clone+"/"+new_name)
            CommitAnalyzer.empty_recycle_bin()
            #save files
            CommitAnalyzer.save_df(only_gui,commits_analyzed_file,"_only_gui")
            CommitAnalyzer.save_df(df,commits_analyzed_file,"_only_app")
            end_time = time.time()  # Tempo di fine
            execution_time = end_time - start_time  # Time taken
            print(f"Time taken : {execution_time:.6f}s")
        '''
    '''
    @staticmethod
    def run_parallel_analysis():
        #range progetti da analizzare
        project_ranges = [
            [0, 1]
        ]
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = [executor.submit(CommitAnalyzer.analyze_projects, start, end) for start, end in project_ranges]
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()  # Recupera il risultato del processo
                    print("Analisi completata per un batch.")
                except Exception as exc:
                    print(f"Si è verificato un errore durante l'analisi: {exc}")
    '''

if __name__ == "__main__":
    Cloner.enable_git_long_paths()
    # CommitAnalyzer.adoption_analysis()
    CommitAnalyzer.migration_analysis()
