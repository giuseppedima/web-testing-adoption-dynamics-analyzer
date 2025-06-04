import os.path
from itertools import islice

import requests
from CommitAnalyzer.commitAnalyzer import CommitAnalyzer
from Dataset.DBconnector import Session, engine
from Dataset.Repository import Repository
import  numpy as np
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from pydriller import Repository
from ProjectAnalyzer.JSTS.JavascriptDataAnalyzer import JavascriptDataAnalyzer
from RepositoryAnalyzer.RepositoryCloner import Cloner


class TemporalAnalysisDate:
    keycloak_keycloak_e2e_adoption = 2013
    tools_years = {
        "Selenium": 2004,
        "Cypress": 2015,
        "Playwright": 2020,
        "Puppeteer": 2017
    }

    @staticmethod
    def get_repo_details_by_name(repo_name):
        '''
        try:
            session = Session(bind=engine)
            print("Connection successful!")
            records = session.query(Repository).filter(Repository.name == repo_name).all()
            return records[0]
        except Exception as e:
            print(f"Error connecting to the database: {e}")
        finally:
            session.close()  # Assicurati che la sessione venga chiusa dopo l'uso
        '''
        df = pd.read_excel(f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ1/first_commit.xlsx',header=None)
        for index,row in df.iterrows():
            name = row.iloc[0]
            date = row.iloc[1]
            if name == repo_name:
                return date
        return None


    @staticmethod
    def get_e2e_adoption_date(repo_name):
        new_name = repo_name.replace('/', '_')
        commits_analyzed_file_excel = '/home/sergio/ICST25-E2EMining/webguirepo_commit_analysis/' + new_name + '/commits_analysis' + new_name+"_only_gui.xlsx"
        commits_analyzed_file_csv = '/home/sergio/ICST25-E2EMining/webguirepo_commit_analysis/' + new_name + '/commits_analysis' + new_name+"_only_gui.csv"
        if os.path.exists(commits_analyzed_file_excel):
            df = pd.read_excel(commits_analyzed_file_excel)
            commit_str = df.columns[2]
            year = commit_str[commit_str.index('(') + 1:commit_str.index('-')]
            return  int(year)
        elif os.path.exists(commits_analyzed_file_csv):
            df = pd.read_csv(commits_analyzed_file_csv)
            commit_str= df.columns[2]
            year = commit_str[commit_str.index('(') + 1:commit_str.index('-')]
            return  int(year)
        else:
            print(f"{repo_name} non esiste!")

    @staticmethod
    def draw_scatter_plot(matrix):
        x = []
        y = []
        size = []
        plt.figure(figsize=(16, 16))

        colors = ["red", "green", "darkgoldenrod", "purple"]
        for (tool, year), color in zip(TemporalAnalysisDate.tools_years.items(), colors):
            y_index = year - 2001
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
        plt.ylabel('Web GUI adoption (year)', fontsize=20)
        plt.xlim(-1, matrix.shape[1])  # Imposta i limiti dell'asse x
        plt.ylim(2003 - 2001, matrix.shape[0])  # Imposta l'asse y per partire dal 2003
        # Etichette assi x e y con font size maggiore e rotazione delle etichette x
        plt.xticks(ticks=np.arange(0, matrix.shape[1]), labels=np.arange(2001, 2025), fontsize=14, rotation=45)
        plt.yticks(ticks=np.arange(2003 - 2001, matrix.shape[0]), labels=np.arange(2003, 2025), fontsize=14)
        # Mantiene l'aspetto quadrato e la griglia con trasparenza
        plt.gca().set_aspect('equal', adjustable='box')
        plt.grid(True, alpha=0.1)

        # Salva il grafico
        plt.savefig(
            '/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ1/adoption-creation-comparison.png',
            bbox_inches='tight')

    @staticmethod
    def create_scatter_plot_e2e_adoption(path):
        res = np.zeros((24,24)) #2001 to 2024
        df= pd.read_csv(f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ1/repo_to_analyze.csv',header=None)
        #for index, row in islice(df.iterrows(), 0, 1):
        for index,row in df.iterrows():
            #for repo, e2e_repo in repos[:12]:
            repo_name = row[0]
            repo_name = repo_name.replace('_','/')
            created_at = str(TemporalAnalysisDate.get_repo_details_by_name(row[0]))
            create_at_date_obj = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
            # Estrazione dell'anno
            create_at_year = create_at_date_obj.year
            col = create_at_year % 2001
            if row[0] == 'keycloak_keycloak':
                e2e_year = TemporalAnalysisDate.keycloak_keycloak_e2e_adoption
            else:
                e2e_year = TemporalAnalysisDate.get_e2e_adoption_date(row[0])
            print(f"name :{repo_name} - created-at:{create_at_year} e2e_adoption: {e2e_year} col:{col} row {e2e_year % 2001}")
            if e2e_year >= create_at_year:
                row = e2e_year % 2001
                res[row][col]+=1
        TemporalAnalysisDate.draw_scatter_plot(res)
        print(res)
        return res


    @staticmethod
    def create_first_commit_date_file():
        res = []
        path = f'/home/sergio/ICST25-E2EMining/webguirepo_commit_analysis/'
        path_folder_clone = f"/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/clone"
        if not os.path.exists(path):
            print(f"Il path {path} non esiste.")
            return
        items = os.listdir(path)
        for item in items:
            # for repo, e2e_repo in repos[:12]:
            repo_name = item
            repo_name = repo_name.replace('_', '\\',1)
            cloned_repository = path_folder_clone + "/" + item
            cloner = Cloner(path_folder_clone)
            cloner.clone_repository(repo_name)
            JavascriptDataAnalyzer.rename_dir(repo_name, item)
            repo = Repository(cloned_repository)
            all_commits = list(repo.traverse_commits())
            sorted_commits = sorted(all_commits, key=lambda commit: commit.committer_date)
            res.append([item,sorted_commits[0].committer_date.replace(tzinfo=None)])
            CommitAnalyzer.clear_directory(path_folder_clone + "/" + item)
            CommitAnalyzer.empty_recycle_bin()
        df = pd.DataFrame(res)
        df.to_excel(f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ1/first_commit.xlsx',index=False,header=False)


if __name__ == "__main__":
    '''
    #repos = CommitAnalyzer.get_e2e_repo_with_n_more_test(30)
    path = f'/home/sergio/ICST25-E2EMining/webguirepo_commit_analysis/'
    res = TemporalAnalysisDate.create_scatter_plot_e2e_adoption(path)
    #TemporalAnalysisDate.create_first_commit_date_file()

    extra= [
        'toeverything_blocksuite',
        'niivue_niivue',
        'determined-ai_determined',
        'boxyhq_jackson',
        'axa-ch-webhub-cloud_pattern-library',
        'epistimio_orion',
        'toeverything_AFFiNE',
        'github_docs',
        'withastro_astro',
        'sveltejs_kit',
        'ensdomains_ens-app-v3',
        'codeinwp_neve',
        'tagspaces_tagspaces',
    ]

    toavoid = [
        'determined-ai_determined',
        'github_docs',
        'codeinwp_neve',
    ]

    path = f'/home/sergio/ICST25-E2EMining/webguirepo_commit_analysis/'
    repo_to_analyze = []
    if not os.path.exists(path):
        print(f"Il path {path} non esiste.")
        exit(0)
    items = os.listdir(path)
    print(len(items))
    for item in items:
        if item not in toavoid:
            repo_to_analyze.append(item)
    print(len(repo_to_analyze))
    df = pd.DataFrame(repo_to_analyze)
    df.to_csv(f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ1/repo_to_analyze.csv',index=False,header=False)
    '''

    matrix = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 4, 0, 3, 1, 3, 1, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 4, 0, 3, 2, 4, 0, 0, 0, 0, 0],
                     [0, 0, 0, 1, 0, 0, 1, 1, 2, 1, 0, 3, 1, 2, 2, 1, 2, 1, 3, 4, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 0, 0, 1, 4, 3, 0, 1, 4, 6, 5, 0, 0, 0],
                     [0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 2, 1, 0, 6, 1, 5, 6, 4, 9, 8, 4, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 0, 1, 1, 3, 3, 5, 1, 3, 1, 6, 2, 1, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 3, 0, 0, 0],])
    TemporalAnalysisDate.draw_scatter_plot(matrix)
