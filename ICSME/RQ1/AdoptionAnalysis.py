import os
from datetime import datetime
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from CommitAnalyzer.commitAnalyzer import CommitAnalyzer
from CommitAnalyzer.commitAnalyzer_perf import CommitAnalyzerPerf
from Dataset.DBconnector import Session, engine
from Dataset.Repository import PerformanceTestingTestDetails,Repository
from ICSME.RQ2.OtherTestResearch import OtherTestResearch
from ProjectAnalyzer.JSTS.JavascriptDataAnalyzer import JavascriptDataAnalyzer
from RepositoryAnalyzer.RepositoryCloner import Cloner
from pydriller import Repository



class AdoptionAnalysis:

    tools_years = {
        "JMeter": 2004,
        "Locust": 2011
    }



    black_list=[
        'undera/jmeter-plugins',
        'splicemachine/spliceengine',
        'marklogic/marklogic-data-hub',
        'ant-media/ant-media-server',
        'mindsdb/mindsdb',
        'googlecloudplatform/professional-services',
        'medic/cht-core'
    ]

    @staticmethod
    def get_perf_repo():
        try:
            session = Session(bind=engine)
            print("Connection successful!")

            # Query con distinct su test_path
            records = session.query(
                PerformanceTestingTestDetails.repository_name,
            ).distinct().all()

            return records

        except Exception as e:
            print(f"Error connecting to the database: {e}")

        finally:
            session.close()  # Assicurati che la sessione venga chiusa dopo l'uso

    @staticmethod
    def get_created_at_by_reponame(repo_name):
        '''
        try:
            session = Session(bind=engine)
            print("Connection successful!")

            # Query con distinct su test_path
            records = session.query(
                PerformanceTestingTestDetails,Repository).join(
                Repository,
                Repository.name == PerformanceTestingTestDetails.repository_name
            ).filter(
                Repository.name == repo_name
            ).all()
            return records[0]

        except Exception as e:
            print(f"Error connecting to the database: {e}")

        finally:
            session.close()  # Assicurati che la sessione venga chiusa dopo l'uso
        '''
        df = pd.read_excel(f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/ICSME/RQ1/first_commit.xlsx',header=None)
        for index, row in df.iterrows():
            name = row.iloc[0]
            date = row.iloc[1]
            if name == repo_name:
                return date
        return None

    @staticmethod
    def get_performace_testing_adoption(repo_name):

        eug_data ='2019-08-30 21:11:18+01:00'
        if repo_name != 'eugenp/tutorials':

            new_name = repo_name.replace('/', '_')
            commits_analyzed_file_excel = '/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/ICSME/performance_test_commit_analysis/' + new_name + '/commits_analysis' + new_name + "_only_gui.xlsx"
            commits_analyzed_file_csv = '/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/ICSME/performance_test_commit_analysis/' + new_name + '/commits_analysis' + new_name + "_only_gui.csv"
            if os.path.exists(commits_analyzed_file_excel):
                df = pd.read_excel(commits_analyzed_file_excel)
                commit_str = df.columns[2]
                year = commit_str[commit_str.index('(') + 1:commit_str.index('-')]
                return int(year)
            elif os.path.exists(commits_analyzed_file_csv):
                df = pd.read_csv(commits_analyzed_file_csv)
                commit_str = df.columns[2]
                year = commit_str[commit_str.index('(') + 1:commit_str.index('-')]
                return int(year)
            else:
                print(f"{repo_name} non esiste!")
        else:
            return 2019


    @staticmethod
    def rename_dir(original_name, new_name):
        path_folder_clone = "/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/clone"
        original_path = os.path.join(path_folder_clone, original_name)
        new_path = os.path.join(path_folder_clone, new_name)

        print(f"Rinominando {original_path} -> {new_path}")

        if os.path.exists(original_path):
            os.rename(original_path, new_path)
            print("Rinomina riuscita!")
        else:
            print(f"Errore: La cartella {original_path} non esiste!")



    @staticmethod
    def create_first_commit_date_file(repos):
        res = []
        records = CommitAnalyzerPerf.get_repos_and_perf_test()
        map = CommitAnalyzerPerf.create_repo_test_map(records)
        keys = list(map.keys())  # Ottieni le chiavi come lista
        for repo_name in keys:
            JavascriptDataAnalyzer.enable_git_long_paths()
            path_folder_clone = f"/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/clone"
            cloner = Cloner(path_folder_clone)
            cloner.clone_repository(repo_name)
            original_name = repo_name.replace('/', '\\')
            new_name = repo_name.replace('/', '_')
            OtherTestResearch.rename_dir(original_name, new_name)
            cloned_repository = path_folder_clone + "/" + new_name
            repo = Repository(cloned_repository)
            all_commits = list(repo.traverse_commits())
            sorted_commits = sorted(all_commits, key=lambda commit: commit.committer_date)
            res.append([repo_name, sorted_commits[0].committer_date.replace(tzinfo=None)])
            CommitAnalyzer.clear_directory(cloned_repository)
            CommitAnalyzer.empty_recycle_bin()
        df = pd.DataFrame(res)
        df.to_excel(f'//home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/ICSME/RQ1/first_commit.xlsx',index=False, header=False)






    @staticmethod
    def create_scatter_plot_performance_adoption(repos):
        res = np.zeros((21,21))
        for repos_name in repos:
            repo_name = repos_name[0]
            if repo_name not in AdoptionAnalysis.black_list:
                created_at = str(AdoptionAnalysis.get_created_at_by_reponame(repo_name))
                create_at_date_obj = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
                # Estrazione dell'anno
                create_at_year = create_at_date_obj.year
                print(create_at_year)
                col = create_at_year % 2004
                perf_year = AdoptionAnalysis.get_performace_testing_adoption(repo_name)
                print(f"name :{repo_name} - created-at:{create_at_year} perfadoption: {perf_year} col:{col} row {perf_year % 2001}")
                row = perf_year % 2004
                if perf_year >= create_at_year:
                    res[row][col] += 1
                else:
                    print('caso strano!!')

        print(res)
        return res

    @staticmethod
    def draw_scatter_plot(matrix):
        x = []
        y = []
        size = []
        plt.figure(figsize=(16, 16))

        colors = ["red", "green"]
        for (tool, year), color in zip(AdoptionAnalysis.tools_years.items(), colors):
            y_index = year - 2005
            plt.axhline(y=y_index, color=color, linestyle="--", linewidth=1, zorder=1)  # Imposta zorder per le linee
            plt.text(matrix.shape[1] + 0.5, y_index, tool, color=color, fontsize=15, ha='left', va='center')

        # Disegna la diagonale tratteggiata e sbiadita
        plt.plot([0, matrix.shape[1] - 1], [0, matrix.shape[0] - 1],
                 color='black', linestyle='--', linewidth=1, alpha=0.3)

        # Creazione dello scatter plot
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                count = int(matrix[i, j])  # Numero di palline da disegnare
                if count > 0:
                    plt.scatter(j, i, s=750, color='blue', alpha=0.7,
                                zorder=3)  # Aumenta la dimensione del pallino e zorder
                    plt.text(j, i, str(count), fontsize=20, ha='center', va='center', color='white')

        # Ingrandisci etichette assi e titolo
        plt.xlabel('Repository creation (year)', fontsize=20)
        plt.ylabel('Performance Testing adoption (year)', fontsize=20)
        plt.xlim(-1, matrix.shape[1])  # Imposta i limiti dell'asse x
        plt.ylim(2003 - 2001, matrix.shape[0])  # Imposta l'asse y per partire dal 2003
        # Etichette assi x e y con font size maggiore e rotazione delle etichette x
        plt.xticks(ticks=np.arange(0, matrix.shape[1]), labels=np.arange(2005, 2025), fontsize=14, rotation=45)
        plt.yticks(ticks=np.arange(2003 - 2001, matrix.shape[0]), labels=np.arange(2005, 2025), fontsize=14)
        # Mantiene l'aspetto quadrato e la griglia con trasparenza
        plt.gca().set_aspect('equal', adjustable='box')
        plt.grid(True, alpha=0.1)

        # Salva il grafico
        plt.savefig(
            '/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/ICSME/RQ1/adoption-creation-comparison.png',
            bbox_inches='tight')


if __name__=="__main__":
    repos_name = AdoptionAnalysis.get_perf_repo()
    print(len(repos_name))
    path ='/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/ICSME/performance_test_commit_analysis/'
    AdoptionAnalysis.create_scatter_plot_performance_adoption(repos_name)
    #AdoptionAnalysis.create_first_commit_date_file(repos_name)

    '''
    matrix = np.array([
                     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [1, 0, 0, 0, 0, 2, 1, 0, 3, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 1, 0, 2, 0, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 1, 1, 2, 0, 0, 0, 1, 2, 2, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3, 0, 1, 3, 1, 0, 0, 0, 0],
                     [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 2, 0, 1, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 3, 1, 0, 5, 0, 2, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 0, 0, 1, 0, 0, 0],])
    AdoptionAnalysis.draw_scatter_plot(matrix)
    '''