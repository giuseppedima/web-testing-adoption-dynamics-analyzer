import concurrent
import csv
import gc
import os
from pathlib import Path

import pandas as pd

from Dataset.DBconnector import Session, engine
from Dataset.Repository import WebRepositoryDAO, E2ERepository
from RepositoryAnalyzer.Analyzer import DependencyFinderInterface
from RepositoryAnalyzer.AnalyzerInterface import DependencyFileFinderInterface
from RepositoryAnalyzer.RepositoryCloner import Cloner
from RepositoryAnalyzer.TestFinderInterface import SeleniumTestDependencyFinder, PuppeteerTestDependencyFinder, \
    CypressTestDependencyFinder, PlayWrightTestDependencyFinder
from TemporalAnalysisDate import TemporalAnalysisDate
from pydriller import Repository,ModificationType
from CommitAnalyzer.commitAnalyzer import CommitAnalyzer
from ProjectAnalyzer.JSTS.JavascriptDataAnalyzer import JavascriptDataAnalyzer
class FileDependencyAnalysis:



    test_dependency = [SeleniumTestDependencyFinder(), PlayWrightTestDependencyFinder(),
                       PuppeteerTestDependencyFinder(), CypressTestDependencyFinder()]

    @staticmethod
    def get_unique_e2e_file_path(file_path,name):
        clone_path = '/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/clone/'
        to_replace = '/home/sergio/ICST25-E2EMining/clone/'
        df = pd.read_csv(file_path)
        file_paths = df[name]
        unique_paths = file_paths.apply(lambda x: os.path.dirname(x)).unique()
        unique_paths = [path.replace(to_replace, clone_path) for path in unique_paths]
        return unique_paths

    @staticmethod
    def get_unique_e2e_file_path_main(file_analysis_name):
        files_name = []
        if os.path.exists(CommitAnalyzer.java_analysis_folder + "/" + file_analysis_name):
            files_name.extend(FileDependencyAnalysis.get_unique_e2e_file_path(CommitAnalyzer.java_analysis_folder + "/" + file_analysis_name,'File Path'))
        if os.path.exists(CommitAnalyzer.js_ts_analysis_folder + "/" + file_analysis_name):
            files_name.extend(FileDependencyAnalysis.get_unique_e2e_file_path(CommitAnalyzer.js_ts_analysis_folder + "/" + file_analysis_name,'File Path'))
        if os.path.exists(CommitAnalyzer.py_analysis_folder + "/" + file_analysis_name):
            files_name.extend(FileDependencyAnalysis.get_unique_e2e_file_path(CommitAnalyzer.py_analysis_folder + "/" + file_analysis_name,'File Path'))
        if os.path.exists(CommitAnalyzer.missed_repo_folder + "/" + file_analysis_name):
            files_name.extend(FileDependencyAnalysis.get_unique_e2e_file_path(CommitAnalyzer.missed_repo_folder+"/"+file_analysis_name,'file_path'))
        return list(set(files_name))
    @staticmethod
    def remove_levels(path):
        paths = []
        normalized_path = os.path.normpath(path)
        path_parts = normalized_path.split(os.sep)
        for i in range(len(path_parts), 0, -1):
            new_path = os.sep.join(path_parts[:i])
            paths.append(new_path)
        return paths

    @staticmethod
    def check_path_in_dep(path,deps):
        for dep in deps:
            if path == os.path.dirname(dep):
                return True,dep
        return False,None

    @staticmethod
    def filter_file_dep(unique_e2e_paths,deps):
        filtered_dep = set([])
        for e2e_path in unique_e2e_paths:
            paths = FileDependencyAnalysis.remove_levels(e2e_path)
            for path in paths:
                founded, dep = FileDependencyAnalysis.check_path_in_dep(path, deps)
                if founded:
                    filtered_dep.add(dep)
                    break
        return filtered_dep



    @staticmethod
    def filter_file_dep_main(dep_java,dep_js,dep_ts,dep_py,new_name):
        filtered_dep_java = set([])
        filtered_dep_js = set([])
        filtered_dep_ts = set([])
        filtered_dep_py = set([])
        unique_e2e_paths = FileDependencyAnalysis.get_unique_e2e_file_path_main(new_name + ".csv")

        if len(dep_java)>0:
            filtered_dep_java = FileDependencyAnalysis.filter_file_dep(unique_e2e_paths,dep_java)
        if len(dep_js)>0:
            filtered_dep_js = FileDependencyAnalysis.filter_file_dep(unique_e2e_paths,dep_js)
        if len(dep_ts)>0:
            filtered_dep_ts = FileDependencyAnalysis.filter_file_dep(unique_e2e_paths,dep_ts)
        if len(dep_py)>0:
            filtered_dep_py = FileDependencyAnalysis.filter_file_dep(unique_e2e_paths,dep_py)

        return filtered_dep_java,filtered_dep_js,filtered_dep_ts,filtered_dep_py


    @staticmethod
    def retrive_commits_envolved_file_dep(repo_name, dependency_file_list,cloned_repository):
        results = {
            'file': [],
            'commits': []
        }
        to_replace = f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/clone/' + repo_name.replace('/', '_')
        print(f"The repo {repo_name} has {len(dependency_file_list)} files dependency.")
        for dep in dependency_file_list:
            try:
                repo = Repository(cloned_repository, filepath=dep)
                file_commit_involved = list(repo.traverse_commits())
                print(f'dep : {dep} envolves {len(file_commit_involved)} commit')
                results['file'].append(dep.replace(to_replace+"/",''))
                results['commits'].append(file_commit_involved)
            finally:
                if repo:
                    del repo
                gc.collect()
        return results

    @staticmethod
    def get_list_of_libraries(file,file_content):
        dependencies = []
        dependencies = DependencyFinderInterface.factory_analyzer(file).find_dependency(file_content, dependencies)
        return dependencies



    @staticmethod
    def analyze_commits_files_dep(commits_for_file):
        data =[]
        data.append(['file','commit','web-gui-tools'])
        for i in range(len(commits_for_file['file'])):
            file = commits_for_file['file'][i]
            commits = commits_for_file['commits'][i]
            current_file = file
            commit_sorted = sorted(commits, key=lambda commit: commit.committer_date, reverse=True)
            for commit in commit_sorted:
                dependencies = []
                for modification in commit.modified_files:
                    type = modification.change_type
                    path = modification.new_path
                    old_name = modification.old_path
                    if type == ModificationType.RENAME:
                        if path == current_file:
                            current_file = old_name
                            break
                    elif type == ModificationType.MODIFY or type == ModificationType.ADD:
                        if path == current_file:
                            new_source_code = modification.source_code
                            if new_source_code != None:
                                dependencies = FileDependencyAnalysis.get_list_of_libraries(file,new_source_code)
                            break
                    elif type == ModificationType.DELETE:
                        if old_name == current_file:
                            old_source_code = modification.source_code_before
                            if old_source_code != None:
                                dependencies = FileDependencyAnalysis.get_list_of_libraries(file,old_source_code)
                            break

                gui_deps = []
                if len(dependencies) >0:
                    if 'pom.xml' in file:
                        gui_deps = FileDependencyAnalysis.search_for_gui_dependency(dependencies,['Java'])
                    elif 'build.gradle' in file:
                        gui_deps = FileDependencyAnalysis.search_for_gui_dependency(dependencies,['Java'])
                    elif 'requirements' in file:
                        gui_deps = FileDependencyAnalysis.search_for_gui_dependency(dependencies,['Python'])
                    elif 'package.json' in file or 'package-lock.json' in file:
                        gui_deps = FileDependencyAnalysis.search_for_gui_dependency(dependencies,['JavaScript','TypeScript'])
                data.append([file,commit.committer_date.strftime("%Y-%m-%d %H:%M:%S"),';'.join(gui_deps)])
        return data

    @staticmethod
    def analyze_dep_file(start,end):
        language_to_analyze = ['Java', 'Python', 'JavaScript', 'TypeScript']
        path_folder_clone = f"/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/clone"
        #repos = FileDependencyAnalysis.get_repos_with_gui_tests()
        df = pd.read_csv(
            f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ1/repo_to_analyze.csv',
            header=None)
        for index, row in df.iterrows():
            #repo_name = web_repo.name
            #original_name = repo_name.replace('/', '\\')
            #new_name = repo_name.replace('/', '_')
            repo_name = row[0].replace('_', '/', 1)
            original_name = repo_name.replace('/', '\\')
            new_name = repo_name.replace('/', '_')
            csv_path = f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ1/file_dep_analysis/' + new_name
            if not os.path.exists(csv_path):
                #for web_repo, e2e_repo in repos[start:end]:
                #repo_name = web_repo.name
                print(f"rename dir: {original_name} -> {new_name}")
                cloned_repository = path_folder_clone + "/" + new_name
                directory = f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ1/file_dep_analysis/'+ new_name + "/"
                Path(directory).mkdir(parents=True, exist_ok=True)
                cloner = Cloner(path_folder_clone)
                cloner.clone_repository(repo_name)
                JavascriptDataAnalyzer.rename_dir(original_name, new_name)
                dependency_java_file_list = []
                dependency_js_file_list = []
                dependency_ts_file_list = []
                dependency_py_file_list = []

                dependency_java_file_list += DependencyFileFinderInterface.factory_finder(
                        language_to_analyze[0]).find_dependency_file(cloned_repository)
                dependency_js_file_list += DependencyFileFinderInterface.factory_finder(
                        language_to_analyze[2]).find_dependency_file(cloned_repository)
                dependency_ts_file_list += DependencyFileFinderInterface.factory_finder(
                        language_to_analyze[3]).find_dependency_file(cloned_repository)

                dependency_py_file_list += DependencyFileFinderInterface.factory_finder(
                        language_to_analyze[1]).find_dependency_file(cloned_repository)

                dependency_java_file_list, dependency_js_file_list, dependency_ts_file_list, dependency_py_file_list = FileDependencyAnalysis.filter_file_dep_main(dependency_java_file_list,dependency_js_file_list,dependency_ts_file_list,dependency_py_file_list,new_name)
                if len(dependency_java_file_list) > 0:
                    commits_envolved_java = FileDependencyAnalysis.retrive_commits_envolved_file_dep(repo_name,dependency_java_file_list,cloned_repository)
                    data = FileDependencyAnalysis.analyze_commits_files_dep(commits_envolved_java)
                    df = pd.DataFrame(data)
                    df.to_csv(directory+"java_deps.csv", index=False, header=False)

                if len(dependency_js_file_list) > 0:
                    commits_envolved_js = FileDependencyAnalysis.retrive_commits_envolved_file_dep(repo_name,dependency_js_file_list,cloned_repository)
                    data = FileDependencyAnalysis.analyze_commits_files_dep(commits_envolved_js)
                    df = pd.DataFrame(data)
                    df.to_csv(directory + "js_deps.csv", index=False, header=False)

                if len(dependency_ts_file_list) > 0:
                    commits_envolved_ts = FileDependencyAnalysis.retrive_commits_envolved_file_dep(repo_name,dependency_ts_file_list,cloned_repository)
                    data = FileDependencyAnalysis.analyze_commits_files_dep(commits_envolved_ts)
                    df = pd.DataFrame(data)
                    df.to_csv(directory + "ts_deps.csv", index=False, header=False)

                if len(dependency_py_file_list)> 0:
                    commits_envolved_py = FileDependencyAnalysis.retrive_commits_envolved_file_dep(repo_name,dependency_py_file_list,cloned_repository)
                    data = FileDependencyAnalysis.analyze_commits_files_dep(commits_envolved_py)
                    df = pd.DataFrame(data)
                    df.to_csv(directory + "py_deps.csv", index=False, header=False)

                CommitAnalyzer.clear_directory(path_folder_clone + "/" + new_name)
                CommitAnalyzer.empty_recycle_bin()


    @staticmethod
    def search_for_gui_dependency(dependencies,languages):
        gui_test_dep =set([])
        if 'Java' in languages:
            for dependency in dependencies:
                if dependency[0] == 'org.seleniumhq.selenium' or dependency[0] == 'com.microsoft.playwright':
                    gui_test_dep.add(dependency[0])
        if 'Python' in languages :
            for dependency in dependencies:
                if dependency[0] == 'playwright' or dependency[0] == 'pytest-playwright':
                    gui_test_dep.add(dependency[0])
                if dependency[0] == 'pyppeteer':
                    gui_test_dep.add(dependency[0])
                if dependency[0] == 'selenium':
                    gui_test_dep.add(dependency[0])
        if 'JavaScript' in languages:
            for dependency in dependencies:
                if dependency[0] == 'selenium' or dependency[0] == 'selenium-webdriver':
                    gui_test_dep.add(dependency[0])
                if dependency[0] == 'playwright':
                    gui_test_dep.add(dependency[0])
                if dependency[0] == 'puppeteer':
                    gui_test_dep.add(dependency[0])
                if dependency[0] == 'cypress':
                    gui_test_dep.add(dependency[0])
        if 'TypeScript' in languages:
            for dependency in dependencies:
                if dependency[0] == '@types/selenium' or dependency[0] == '@types/selenium-webdriver':
                    gui_test_dep.add(dependency[0])
                if dependency[0] == 'playwright':
                    gui_test_dep.add(dependency[0])
                if dependency[0] == '@types/puppeteer':
                    gui_test_dep.add(dependency[0])
                if dependency[0] == 'cypress':
                    gui_test_dep.add(dependency[0])
        return gui_test_dep



    @staticmethod
    def clear_file():
        folder_path =f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/data/py_test_analysis'
        for root, dirs, files in os.walk(folder_path):
                for file in files:
                    # Controlla se il file ha estensione .csv
                    if file.endswith(".csv"):

                        file_path = os.path.join(root, file)
                        print(f"Processing file: {file_path}")

                        # Crea una lista per salvare le righe modificate
                        updated_rows = []

                        # Apri e leggi il file CSV
                        with open(file_path, mode='r') as csv_file:
                            reader = csv.reader(csv_file)
                            headers = next(reader)  # Leggi l'intestazione
                            updated_rows.append(headers)  # Aggiungi l'intestazione alla lista

                            # Trova l'indice della colonna "Number of @Test"
                            index_test_column = headers.index("Number of @Test")

                            for row in reader:
                                # Ottieni il valore della colonna "Number of @Test"
                                number_of_tests = row[index_test_column]

                                # Verifica se il valore è nel formato "(n1, n2)" e prendine solo n1
                                if '(' in number_of_tests and ')' in number_of_tests:
                                    n1 = number_of_tests.split(',')[0].replace('(', '')
                                    row[index_test_column] = n1
                                # Aggiungi la riga modificata alla lista
                                updated_rows.append(row)

                        # Sovrascrivi il file con i dati aggiornati
                        with open(file_path, mode='w', newline='') as csv_file:
                            writer = csv.writer(csv_file)
                            writer.writerows(updated_rows)

                        print(f"File {file_path} aggiornato correttamente.")



    @staticmethod
    def run_parallel_analysis():
        project_ranges = [
            [0,250],
            [250,498]
        ]
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = [executor.submit(FileDependencyAnalysis.analyze_dep_file, start, end) for start, end in project_ranges]
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()  # Recupera il risultato del processo
                    print("Analisi completata per un batch.")
                except Exception as exc:
                    print(f"Si è verificato un errore durante l'analisi: {exc}")

    @staticmethod
    def get_repos_with_gui_tests():
        try:
            session = Session(bind=engine)
            print("Connection successful!")

            # Query con join tra WebRepositoryDAO e E2ERepository
            records = session.query(WebRepositoryDAO, E2ERepository).join(
                E2ERepository,
                WebRepositoryDAO.name == E2ERepository.repository
            ).all()
            return records

        except Exception as e:
            print(f"Error connecting to the database: {e}")

        finally:
            session.close()  # Assicurati che la sessione venga chiusa dopo l'uso

    @staticmethod
    def get_missed_indexs():
        '''
        repos = FileDependencyAnalysis.get_repos_with_gui_tests()
        index =1
        for web_repo, e2e_repo in repos:
            repo_name = web_repo.name
            original_name = repo_name.replace('/', '\\')
            new_name = repo_name.replace('/', '_')
            csv_path = f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ1/file_dep_analysis/'+new_name
            if not os.path.exists(csv_path):
                print(f"repo {repo_name} non processata indice :{index}")
            index+=1
        '''
        df = pd.read_csv(
            f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ1/repo_to_analyze.csv',
            header=None)
        # for index, row in islice(df.iterrows(), 0, 1):
        index = 1
        for index, row in df.iterrows():
            #repo_name = web_repo.name
            #original_name = repo_name.replace('/', '\\')
            #new_name = repo_name.replace('/', '_')
            new_name = row[0]
            csv_path = f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ1/file_dep_analysis/' + new_name
            if not os.path.exists(csv_path):
                print(f"repo {new_name} non processata indice :{index}")
            index += 1





if __name__ == "__main__":
    #FileDependencyAnalysis.run_parallel_analysis()
    FileDependencyAnalysis.analyze_dep_file(484,485)
    #FileDependencyAnalysis.get_missed_indexs()

    #186-187
    #241-242
    #484-485