import concurrent.futures
import errno
import gc
import os.path
import shutil
import stat
import time
import warnings
from pathlib import Path
from pandas.errors import PerformanceWarning

from Dataset.Repository import PerformanceTestingTestDetails,Repository
from ProjectAnalyzer.JSTS.JavascriptDataAnalyzer import JavascriptDataAnalyzer
import os.path
import matplotlib.pyplot as plt
import pandas as pd
from pydriller import Repository, ModificationType
import matplotlib.patches as mpatches
from datetime import  datetime
from Dataset.DBconnector import Session, engine
from RepositoryAnalyzer.RepositoryCloner import Cloner
from sqlalchemy import or_, and_


class CommitAnalyzerPerf:

    warnings.simplefilter(action='ignore', category=PerformanceWarning)
    java_analysis_folder = '../data/java_test_analysis'
    js_ts_analysis_folder = '../data/js_ts_test_analysis'
    py_analysis_folder = '../data/py_test_analysis'
    missed_repo_folder = '../data/missed_repo'

    file_extensions_to_consider = ['.java', '.js', '.ts', '.py', '.html', '.css', '.jsx', '.tsx', '.scss', '.sass', '.vue', '.jsp', '.xhtml','.jmx']

    max_rows_excel = 1048576  # excel's row limitations
    max_cols_excel = 16384  # excel's column limitations


    @staticmethod
    def filter_false_envolved_commit(sorted_commits,filename):
        real_envolved_commit = []
        files = []
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
                        files.append(modification.source_code)
                        break
                elif type == ModificationType.DELETE:
                    if old_name == current_filename:
                        found = True
                        break
                elif type == ModificationType.MODIFY:
                    if path == current_filename:
                        found = True
                        files.append(modification.source_code)
                        break
                elif type == ModificationType.RENAME:
                    if  path == current_filename:
                        found = True
                        current_filename = old_name
                        break
            if found:
                real_envolved_commit.append(commit)
        return real_envolved_commit,files

    @staticmethod
    def get_commit_hash_by_reponame(reponame):
        try:
            session = Session(bind=engine)
            print("Connection successful!")

            # Query directly on Repository table
            records = session.query(Repository).filter(
                Repository.name == reponame
            ).all()

            return records

        except Exception as e:
            print(f"Error connecting to the database: {e}")

        finally:
            session.close()  # Ensure the session is closed after use

    @staticmethod
    #def get_e2e_repo_with_n_more_test(n):
    def get_repos_and_perf_test():
        try:
            session = Session(bind=engine)
            print("Connection successful!")

            # Query con distinct su test_path
            records = session.query(
                PerformanceTestingTestDetails.repository_name,
                PerformanceTestingTestDetails.test_path
            ).distinct(PerformanceTestingTestDetails.test_path
            ).order_by(PerformanceTestingTestDetails.repository_name).all()

            return records

        except Exception as e:
            print(f"Error connecting to the database: {e}")

        finally:
            session.close()  # Assicurati che la sessione venga chiusa dopo l'uso

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
                    if (type != ModificationType.DELETE and CommitAnalyzerPerf.has_extension(path)) or (type == ModificationType.DELETE and CommitAnalyzerPerf.has_extension(old_name)):
                        if type  == ModificationType.ADD:
                            row_idx = CommitAnalyzerPerf.get_first_available_row(df)  # Trova la prima riga disponibile
                            df.at[row_idx, 0] = path
                            df.at[row_idx,i+1] = 'A'
                        elif type == ModificationType.DELETE:
                            path = modification.old_path
                            file_row_idx = df.index[df[0]==path].tolist()
                            if file_row_idx:
                                row_idx = file_row_idx[0]
                                df.at[row_idx,i+1]='D'
                            else:
                                row_idx = CommitAnalyzerPerf.get_first_available_row(df)  # Trova la prima riga disponibile
                                df.at[row_idx, 0] = path
                                df.at[row_idx, i + 1] = 'D'
                        elif type == ModificationType.RENAME:
                            file_row_idx = df.index[df[0] == old_name].tolist()
                            if file_row_idx:
                                row_idx = file_row_idx[0]
                                df.at[row_idx, i + 1] = 'R('+old_name+")"
                                df.at[row_idx,0] = path
                            else:
                                row_idx = CommitAnalyzerPerf.get_first_available_row(df)  # Trova la prima riga disponibile
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
                                row_idx = CommitAnalyzerPerf.get_first_available_row(df)  # Trova la prima riga disponibile
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
    def get_tests_path_without_localpath(filename,repo_name):
        to_replace = '/home/sergio/MSR25-E2EMining/clone/'+repo_name.replace('/','_')
        df = pd.read_csv(filename)
        filtered_data_df = df[df['Number of @Test']>0]
        filtered_data_df['File Path'] = filtered_data_df['File Path'].str.replace(to_replace+"/",'')
        return  filtered_data_df['File Path']

    @staticmethod
    def get_tests_path(filename, repo_name):
        clone_path = '/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/clone/'
        to_replace = '/home/sergio/MSR25-E2EMining/clone/'
        df = pd.read_csv(filename)
        filtered_data_df = df[df['Number of @Test'] > 0]
        #filtered_data_df['File Path'] = filtered_data_df['File Path'].str.replace(to_replace, '')
        return filtered_data_df['File Path'].str.replace(to_replace,clone_path)


    @staticmethod
    def get_tests_path_missed_repo(filename,repo_name):
        clone_path = '/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/clone/'
        to_replace = '/home/sergio/MSR25-E2EMining/clone/'
        df = pd.read_csv(filename)
        filtered_data_df = df[df['number of test'] > 0]
        #filtered_data_df['File Path'] = filtered_data_df['File Path'].str.replace(to_replace, '')
        return filtered_data_df['file_path'].str.replace(to_replace,clone_path)

    @staticmethod
    def get_tests_path_missed_repo_without_localpath(filename,repo_name):
        to_replace = '/home/sergio/MSR25-E2EMining/clone/' + repo_name.replace('/', '_')
        df = pd.read_csv(filename)
        filtered_data_df = df[df['number of test']> 0]
        filtered_data_df['file_path']= filtered_data_df['file_path'].str.replace(to_replace + "/", '')
        return filtered_data_df['file_path']


    @staticmethod
    def get_tests_path_main(file_analysis_name,repo_name,flag):
        files_name = []
        if os.path.exists(CommitAnalyzerPerf.java_analysis_folder + "/" + file_analysis_name):
            if flag:
                files_name = CommitAnalyzerPerf.get_tests_path(CommitAnalyzerPerf.java_analysis_folder + "/" + file_analysis_name,repo_name)
            else:
                files_name = CommitAnalyzerPerf.get_tests_path_without_localpath(CommitAnalyzerPerf.java_analysis_folder + "/" + file_analysis_name,repo_name)

        elif os.path.exists(CommitAnalyzerPerf.js_ts_analysis_folder + "/" + file_analysis_name):
            if flag:
                files_name = CommitAnalyzerPerf.get_tests_path(CommitAnalyzerPerf.js_ts_analysis_folder + "/" + file_analysis_name,repo_name)
            else:
                files_name = CommitAnalyzerPerf.get_tests_path_without_localpath(CommitAnalyzerPerf.js_ts_analysis_folder + "/" + file_analysis_name,repo_name)

        elif os.path.exists(CommitAnalyzerPerf.py_analysis_folder + "/" + file_analysis_name):
            if flag:
                files_name = CommitAnalyzerPerf.get_tests_path(CommitAnalyzerPerf.py_analysis_folder + "/" + file_analysis_name,repo_name)
            else:
                files_name = CommitAnalyzerPerf.get_tests_path_without_localpath(CommitAnalyzerPerf.py_analysis_folder + "/" + file_analysis_name,repo_name)
        elif os.path.exists(CommitAnalyzerPerf.missed_repo_folder + "/" + file_analysis_name):
            if flag:
                files_name = CommitAnalyzerPerf.get_tests_path_missed_repo(CommitAnalyzerPerf.missed_repo_folder + "/" + file_analysis_name,repo_name)
            else:
                files_name = CommitAnalyzerPerf.get_tests_path_missed_repo_without_localpath(CommitAnalyzerPerf.missed_repo_folder + "/" + file_analysis_name,repo_name)
        return files_name

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

    def save_files_in_order(files, save_directory, base_filename):
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

        for index, file_content in enumerate(files, start=1):
            # Crea il nome del file con un indice sequenziale
            filename = f"{save_directory}/{base_filename}_{index}.txt"

            # Salva il contenuto del file
            with open(filename, 'w') as f:
                f.write(file_content)
            print(f"Saved file: {filename}")

    @staticmethod
    def get_all_perf_commits_sorted(repo_path,repo_name,map,dir):
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

                repo = Repository(repo_path, filepath = new_file_name)
                file_commit_involved = list(repo.traverse_commits())
                non_merge_commits = [commit for commit in file_commit_involved if not commit.merge]
                discendent_non_merge_commits = sorted(non_merge_commits, key=lambda c: c.committer_date, reverse=True)

                filename = file.replace("\\", '/')
                filename = filename.replace("/"+repo_name+"/",'')
                real_envolved_commit,files = CommitAnalyzerPerf.filter_false_envolved_commit(discendent_non_merge_commits,filename)
                print(f"{file} envoles {len(real_envolved_commit)} commit!")
                directory = dir+"/test_changes/"
                Path(directory).mkdir(parents=True, exist_ok=True)
                CommitAnalyzerPerf.save_files_in_order(files,directory,os.path.basename(new_file_name))
                sel_commits.extend(real_envolved_commit)

            finally:
                if repo:
                    del repo
                gc.collect()
        sorted_commits = sorted(sel_commits, key=lambda commit: commit.committer_date)
        #print(f"Number of commits that envolve webguitests are: {len(sel_commits)}")
        print(f"First commit about a performance testing: {sorted_commits[0].committer_date}")
        return sorted_commits

    @staticmethod
    def get_commits_by_filepath(repo_name,map,dir):
        JavascriptDataAnalyzer.enable_git_long_paths()
        path_folder_clone = f"/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/clone"
        cloner = Cloner(path_folder_clone)
        cloner.clone_repository(repo_name)
        original_name = repo_name.replace('/', '\\')
        new_name = repo_name.replace('/', '_')
        print(f"rename dir: {original_name} -> {new_name}")
        JavascriptDataAnalyzer.rename_dir(original_name, new_name)
        cloned_repository = path_folder_clone + "/" + new_name
        repo = Repository(cloned_repository)
        sorted_all_commits = CommitAnalyzerPerf.get_all_commits_sorted(repo,repo_name)
        sorted_perf_commits = CommitAnalyzerPerf.get_all_perf_commits_sorted(cloned_repository,repo_name,map,dir)

        commits_to_analyze = CommitAnalyzerPerf.get_commits_before_the_first_webgui(sorted_all_commits,sorted_perf_commits[0])
        print(f'commit to analyze[{len(commits_to_analyze)}] {commits_to_analyze[0].committer_date} -> {commits_to_analyze[len(commits_to_analyze)-1].committer_date}')
        df = CommitAnalyzerPerf.create_history_excel_file(repo_name,commits_to_analyze)
        return df

    @staticmethod
    def split_appcommit_guiweb_commit(df, repo_name,map):
        paths_to_prioritize = list(map[repo_name])  # Converte il set in una lista
        for i in range(len(paths_to_prioritize)):
            paths_to_prioritize[i] = paths_to_prioritize[i].replace("\\", '/')
            paths_to_prioritize[i] = paths_to_prioritize[i].replace("/" + repo_name + "/", '')

        print(paths_to_prioritize)
        df_new = pd.DataFrame()
        df_new = pd.concat([df_new, df.iloc[0:1]], ignore_index=True)
        for index, row in df.iterrows():
            if row.iloc[0] in paths_to_prioritize:
                df_new = pd.concat([df_new, row.to_frame().T], ignore_index=True)

        # remove the guiwebtest rows from the first dataframe
        df = df[~df.iloc[:, 0].isin(paths_to_prioritize)]
        return df,df_new


    @staticmethod
    def has_extension(filepath):
        return any(filepath.endswith(ext) for ext in CommitAnalyzerPerf.file_extensions_to_consider)

    @staticmethod
    def create_scatter_plot(df_app_filtered,df_gui,repo_name):
        new_name = repo_name.replace('/', '_')
        commits_analyzed_file = '../webguirepo_commit_analysis/'+new_name+ '/commits_analysis' + new_name
        num_of_tests = len(df_gui)

        print(f"df_app size: {df_app_filtered.shape}")
        print(f"df_gui size: {df_gui.shape}")

        # check if the first rows of df_gui and df_app are the same
        if df_gui.iloc[0].equals(df_app_filtered.iloc[0]):
            # remove the first row from df_app
            df_app_filtered = df_app_filtered.iloc[1:]

        # merge both df
        merged_df = pd.concat([df_gui, df_app_filtered], ignore_index=True)

        print(f"df_merged size: {merged_df.shape}")

        x_coords = []
        y_coords = []
        colors = []

        # color map
        color_map_app = {
            0: 'grey',
            1: 'orange',
            2: 'lightblue'
        }

        color_map_gui = {
            0: 'yellow',
            1: 'green',
            2: 'blue'
        }

        for i in range(1, merged_df.shape[0]):
            for j in range(1, merged_df.shape[1]):
                value = merged_df.iloc[i, j]

                if pd.isna(value) or value == '':
                    continue

                if i < num_of_tests:
                    color_map = color_map_gui
                else:
                    color_map = color_map_app

                x_coords.append(j)
                y_coords.append(i)
                if value == 'A':
                    colors.append(color_map[0])
                elif value == 'D':
                    colors.append(color_map[1])
                elif value.startswith('M') or value.startswith('R'):
                    colors.append(color_map[2])
                else:
                    print(f'weird case: {value}')

        if len(x_coords) == len(y_coords) == len(colors):
            plt.scatter(x_coords, y_coords, c=colors, alpha=0.7)
        else:
            print("x, y and colors dimensions are not the same. check the input.")

        plt.figure(figsize=(10, 6))
        plt.scatter(x_coords, y_coords, c=colors, alpha=0.7)

        plt.xticks(ticks=[0, merged_df.shape[1] / 2, merged_df.shape[1]],
                   labels=[0, int(merged_df.shape[1] / 2), merged_df.shape[1]], rotation=45)
        plt.yticks(ticks=[0, merged_df.shape[0] / 2, merged_df.shape[0]],
                   labels=[0, int(merged_df.shape[0] / 2), merged_df.shape[0]])

        legend = [
            mpatches.Patch(color='grey', label='added-regular'),
            mpatches.Patch(color='orange', label='delete-regular'),
            mpatches.Patch(color='lightblue', label='edit-regular'),
            mpatches.Patch(color='yellow', label='added-webguitest'),
            mpatches.Patch(color='green', label='deleted-webguitest'),
            mpatches.Patch(color='blue', label='edit-webguitest'),
        ]

        plt.legend(handles=legend, title="Color Legend")
        plt.title('Change History')
        plt.xlabel('Commit')
        plt.ylabel('File Path')

        plt.tight_layout()
        plt.savefig(commits_analyzed_file+'.png')

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
        first_data = CommitAnalyzerPerf.extract_date(current_blob_commits[0])
        last_date = CommitAnalyzerPerf.extract_date(current_blob_commits[-1])
        count = 0
        for commit in commits:
            commit_date = CommitAnalyzerPerf.extract_date(commit)
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
                                     CommitAnalyzerPerf.calculate_days(current_blob_commits.copy()),
                                      mod,
                                     CommitAnalyzerPerf.calculate_number_of_commits_between_two_dates(current_blob_commits,commits_app),
                                     CommitAnalyzerPerf.calculate_number_of_commits_between_two_dates(current_blob_commits,commits_gui)])
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
                                         CommitAnalyzerPerf.calculate_days(current_blob_commits.copy()),
                                         mod,
                                         CommitAnalyzerPerf.calculate_number_of_commits_between_two_dates(current_blob_commits,commits_app),
                                         CommitAnalyzerPerf.calculate_number_of_commits_between_two_dates(current_blob_commits,commits_gui)])
                            current_blob_commits.clear()
                            current_blob_commits.append(current_commit) #like A
                            number_of_blobs += 1
            if current_blob_commits:
                mod = len(current_blob_commits)
                current_blob_commits.append(current_commit)
                data.append([filepath + '_(' +str(number_of_blobs) + ")",
                             CommitAnalyzerPerf.calculate_days(current_blob_commits.copy()),
                             mod,
                             CommitAnalyzerPerf.calculate_number_of_commits_between_two_dates(current_blob_commits,commits_app),
                             CommitAnalyzerPerf.calculate_number_of_commits_between_two_dates(current_blob_commits,commits_gui)])
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
            days = CommitAnalyzerPerf.calculate_days(span)
            data.append([span_str,commit_count,days])
        df = pd.DataFrame(data,columns=["span","commit","days"])
        df.to_excel(outputfile+'_'+type+'_span_analysis.xlsx',index=False)

    @staticmethod
    def calculate_commit_test_metrics(df_app,df_gui,repo_name):
        new_name = repo_name.replace('/', '_')
        commits_analyzed_file = '../ICSME/'+new_name+ '/commits_analysis' + new_name
        #calculate spans
        spans_gui, commits_gui = CommitAnalyzerPerf.get_gui_span(df_gui)
        spans_app, commits_app = CommitAnalyzerPerf.get_app_span(df_app, commits_gui)

        print(f" spans_gui : {len(spans_gui)} commits : {len(commits_gui)} ")
        print(f" spans_app : {len(spans_app)} commits : {len(commits_app)} ")

        CommitAnalyzerPerf.create_excel_with_span_metrics(commits_analyzed_file,'gui',spans_gui)
        CommitAnalyzerPerf.create_excel_with_span_metrics(commits_analyzed_file,'app',spans_app)

        CommitAnalyzerPerf.create_excel_with_test_lifecycle_metrics(commits_analyzed_file, df_gui, commits_app, commits_gui)


    @staticmethod
    def empty_recycle_bin():
        try:
            CommitAnalyzerPerf.clear_directory("/home/sergio/.local/share/Trash/files")
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

        '''
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path, ignore_errors=False, onerror=CommitAnalyzerPerf.handle_remove_readonly)
                else:
                    os.remove(item_path)
            except Exception as e:
                print(f"Error removing {item_path}: {e}")
        print('Folder succesfully cleaned!')
        '''

    @staticmethod
    def save_df(df,directory,name):
        if df.shape[0] > CommitAnalyzerPerf.max_rows_excel or df.shape[1] > CommitAnalyzerPerf.max_cols_excel:
            csv_filename = directory+name+".csv"
            print(f"Data too large for Excel. Saving as CSV: {csv_filename}")
            df.to_csv(csv_filename, index=False, header=False)
        else:
            excel_filename= directory+name+".xlsx"
            print(f"Data saved as Excel. {directory+name}.xlsx")
            df.to_excel(excel_filename, index=False, header=False)


    @staticmethod
    def analyze_projects(start,end):
        records = CommitAnalyzerPerf.get_repos_and_perf_test()
        map = CommitAnalyzerPerf.create_repo_test_map(records)
        path_folder_clone = f"../clone"
        keys = list(map.keys())  # Ottieni le chiavi come lista
        #for repo in keys[start:end]:  # Itera sulle chiavi nell'intervallo start:end
        repo = 'eugenp/tutorials'
        #repo_name = web_repo.name
        new_name = repo.replace('/', '_')
        directory = '../ICSME/' + new_name + "/"
        Path(directory).mkdir(parents=True, exist_ok=True)
        commits_analyzed_file = '../ICSME/' + new_name + '/commits_analysis' + new_name
        start_time = time.time() #Starting time
        df = CommitAnalyzerPerf.get_commits_by_filepath(repo,map,directory)
        df,only_gui = CommitAnalyzerPerf.split_appcommit_guiweb_commit(df,repo,map)

        #create plot
        #CommitAnalyzerPerf.create_scatter_plot(df,only_gui,repo)
        #perform metrics
        CommitAnalyzerPerf.calculate_commit_test_metrics(df,only_gui,repo)
        #clear clone directory
        CommitAnalyzerPerf.clear_directory(path_folder_clone+"/"+new_name)
        CommitAnalyzerPerf.empty_recycle_bin()
        #save files
        CommitAnalyzerPerf.save_df(only_gui,commits_analyzed_file,"_only_gui")
        CommitAnalyzerPerf.save_df(df,commits_analyzed_file,"_only_app")
        end_time = time.time()  # Tempo di fine
        execution_time = end_time - start_time  # Time taken
        print(f"Time taken : {execution_time:.6f}s")


    @staticmethod
    def run_parallel_analysis():
        #range progetti da analizzare
        project_ranges = [
            [54,55]
        ]
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = [executor.submit(CommitAnalyzerPerf.analyze_projects, start, end) for start, end in project_ranges]
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()  # Recupera il risultato del processo
                    print("Analisi completata per un batch.")
                except Exception as exc:
                    print(f"Si è verificato un errore durante l'analisi: {exc}")

    @staticmethod
    def create_repo_test_map(records):
        map = {}
        for row in records:
            name = row[0]
            test = row[1]
            if name in map:
                map[name].add(test)
            else:
                map[name]= {test}
        return map


if __name__ == "__main__":
    CommitAnalyzerPerf.run_parallel_analysis()