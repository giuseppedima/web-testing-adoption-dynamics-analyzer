import csv
import os.path
import subprocess
from datetime import datetime

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.outliers_influence import variance_inflation_factor
from scipy.stats import pearsonr

from Dataset.DBconnector import Session, engine
from Dataset.Repository import WebRepositoryDAO, Repository
from sqlalchemy import or_, and_
from sklearn.preprocessing import MinMaxScaler
from statsmodels.stats.diagnostic import lilliefors
import seaborn as sns
import matplotlib.pyplot as plt
from cliffs_delta import cliffs_delta

from RepositoryAnalyzer.RepositoryCloner import Cloner


class LinearModel:

    # Creare il DataFrame
    data = {
        'repoName' :[],
        'nLOC': [],
        'nContributors': [],
        'nStars': [],
        'nCommits': [],
        'projectAge': [],
        'watchers':[],
        'size':[],
        'mainLanguage':[],
        'totalIssue':[],
        'nOtherTest' : [],
        'nE2ETests': []

    }

    black_list = ['workiva/frugal','curiefense\curiefense','serverdensity\sd-agent','azure\azure-xplat-cli','moddio/moddio2','xrfoundation/xrengine','smartive/smartive.ch ','plotly/dash-docs','voltdb/voltdb','teamcodestream/codestream','voltdb/voltdb','porter-dev/porter','DeBankDeFi/DeBankChain', 'laboratoria/bootcamp', 'invoiceninja/invoiceninja','zerocracy/farm','workiva/frugal','teamcodestream/codestream','EtherealEngine\etherealengine',]
    other_test_java_folder= f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/other_test_analysis/java_web_app/'
    other_test_js_ts_folder= f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/other_test_analysis/js_ts_web_app/'
    other_test_py_folder= f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/other_test_analysis/py_web_app/'
    e2e_test_java_folder =f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/data/java_test_analysis/'
    e2e_test_js_ts_folder =f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/data/js_ts_test_analysis/'
    e2e_test_py_folder= f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/data/py_test_analysis/'
    e2e_test_missed_folder= f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/data/missed_repo/'


    @staticmethod
    def get_web_repos():
        try:
            # Tenta di connetterti al database
            session = Session(bind=engine)
            print("Connection successful!")
            # Esegui il fetch di tutti i record
            # records = session.query(WebRepositoryDAO).all()
            # Stampa i record

            query = session.query(WebRepositoryDAO, Repository).join(
                Repository,
                 WebRepositoryDAO.name == Repository.name
            ).filter(
                    or_(
                        WebRepositoryDAO.is_web_javascript == True,
                        WebRepositoryDAO.is_web_typescript==True,
                        WebRepositoryDAO.is_web_python==True,
                        WebRepositoryDAO.is_web_java == True,
                    )
            )
            records = query.all()
            return records
        except Exception as e:
            print(f'Error value : {e}')


    @staticmethod
    def calculate_repo_age(last_commit_date, created_at_date):
        last_commit_date_obj = datetime.strptime(last_commit_date, '%Y-%m-%dT%H:%M:%S')
        create_at_date_obj = datetime.strptime(created_at_date, '%Y-%m-%dT%H:%M:%S')
        #current_date = datetime.now()
        years_diff = last_commit_date_obj.year - create_at_date_obj.year
        return years_diff


    @staticmethod
    def get_num_of_test_by_path(csv_file_path,index):
        total_sum = 0
        with open(csv_file_path, mode='r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Salta la prima riga (header)
            for row in csv_reader:
                # Somma il valore dell'ultima colonna (converte in float o int a seconda del tipo di dato)
                if row[index].startswith("("):
                    values = row[index].strip("()").split(",")
                    first_value = int(values[0])
                    total_sum+=first_value
                else:
                    total_sum += int(row[index])  # Usa int(row[-1]) se i valori sono interi
        return total_sum


    @staticmethod
    def calculate_num_other_test_by_reponame(repo_name):
        original_name = repo_name.replace('/', '\\')
        new_name = repo_name.replace('/', '_')
        num_tes = 0
        if os.path.exists(LinearModel.other_test_java_folder+new_name+".csv"):
            num_tes+=LinearModel.get_num_of_test_by_path(LinearModel.other_test_java_folder+new_name+".csv",-1)
        if os.path.exists(LinearModel.other_test_js_ts_folder + new_name + ".csv"):
            num_tes+=LinearModel.get_num_of_test_by_path(LinearModel.other_test_js_ts_folder+new_name+".csv",-1)
        if os.path.exists(LinearModel.other_test_py_folder + new_name + ".csv"):
            num_tes+=LinearModel.get_num_of_test_by_path(LinearModel.other_test_py_folder+new_name+".csv",-1)
        return num_tes




    @staticmethod
    def calculate_num_e2e_test_by_reponame(repo_name):
        original_name = repo_name.replace('/', '\\')
        new_name = repo_name.replace('/', '_')
        num_tes = 0
        if os.path.exists(LinearModel.e2e_test_java_folder+new_name+".csv"):
            num_tes+=LinearModel.get_num_of_test_by_path(LinearModel.e2e_test_java_folder+new_name+".csv",-2)
        if os.path.exists(LinearModel.e2e_test_js_ts_folder + new_name + ".csv"):
            num_tes+=LinearModel.get_num_of_test_by_path(LinearModel.e2e_test_js_ts_folder+new_name+".csv",-2)
        if os.path.exists(LinearModel.e2e_test_py_folder + new_name + ".csv"):
            num_tes+=LinearModel.get_num_of_test_by_path(LinearModel.e2e_test_py_folder+new_name+".csv",-2)
        if os.path.exists(LinearModel.e2e_test_missed_folder+new_name+".csv"):
            num_tes+=LinearModel.get_num_of_test_by_path(LinearModel.e2e_test_missed_folder+new_name+".csv",-2)
        return num_tes


    @staticmethod
    def create_dataset(repos_to_accept):
        output_path =f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ2/'
        repos = LinearModel.get_web_repos()
        for web_repo,repo in repos:
            repo_name = web_repo.name
            if repo_name not in LinearModel.black_list:
                num_gui_tests = LinearModel.calculate_num_e2e_test_by_reponame(repo_name)
                if num_gui_tests==0 or (num_gui_tests>0 and repo_name in repos_to_accept):
                    LinearModel.data['repoName'].append(repo_name)
                    LinearModel.data['nLOC'].append(repo.code_lines)
                    LinearModel.data['nContributors'].append(repo.contributors)
                    LinearModel.data['nStars'].append(repo.stargazers)
                    LinearModel.data['nCommits'].append(repo.commits)
                    LinearModel.data['watchers'].append(repo.watchers)
                    LinearModel.data['size'].append(repo.size)
                    LinearModel.data['projectAge'].append(LinearModel.calculate_repo_age(repo.last_commit,repo.created_at))
                    LinearModel.data['mainLanguage'].append(repo.main_language)
                    LinearModel.data['totalIssue'].append(repo.total_issues)
                    LinearModel.data['nOtherTest'].append(LinearModel.calculate_num_other_test_by_reponame(repo_name))
                    LinearModel.data['nE2ETests'].append(num_gui_tests)
        df = pd.DataFrame(LinearModel.data)
        df.to_excel(output_path+"rq2_data.xlsx",index=False)


    @staticmethod
    def calculate_correlation(df_with_e2e,df_without_e2e):
        # Lista delle variabili indipendenti
        ind_vars = ['nLOC', 'nContributors', 'nStars', 'nCommits', 'watchers', 'size', 'githubAge', 'nOtherTest','nE2ETests']

        # Verifica se ci sono valori nulli nella colonna nE2ETest
        if df_without_e2e['nE2ETests'].isnull().any():
            print("Ci sono valori nulli nella colonna 'nE2ETest'.")
        else:
            print("Non ci sono valori nulli nella colonna 'nE2ETest'.")

        # Inizializza il DataFrame con la dimensione corretta e aggiungi nomi di righe e colonne
        df_rs = pd.DataFrame(index=ind_vars, columns=ind_vars)

        # Inserisci i valori di correlazione e p-value nel DataFrame
        for i in range(len(ind_vars)):
            for j in range(i + 1, len(ind_vars)):
                ind_var_i = ind_vars[i]
                ind_var_j = ind_vars[j]
                corr, p_value = pearsonr(df_without_e2e[ind_var_i], df_without_e2e[ind_var_j])
                # Inserisci i risultati in formato stringa nella posizione corretta
                df_rs.loc[ind_var_i, ind_var_j] = f"(corr: {corr:.4f}, p-value: {p_value:.4e})"
                df_rs.loc[ind_var_j, ind_var_i] = f"(corr: {corr:.4f}, p-value: {p_value:.4e})"
                # Stampa i risultati per verifica
                print(f'------[{ind_var_i},{ind_var_j}]--------------')
                print("Pearson Correlation Coefficient:", corr)
                print("P-value:", p_value)

        # Salva i risultati in un file Excel
        df_rs.to_excel(f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ2/pearsonr.xlsx',index=False)

    @staticmethod
    def normalize_and_split_dataframe():
        output_path = f'/RQ2/rq2_data.xlsx'
        df = pd.read_excel(output_path)
        columns_to_normalize = ['nLOC', 'nContributors', 'nStars', 'nCommits','watchers','size','projectAge', 'nOtherTest']

        scaler = MinMaxScaler()
        df[columns_to_normalize] = scaler.fit_transform(df[columns_to_normalize])

        df_with_e2e = df[df['nE2ETests'] > 0]
        df_without_e2e = df[df['nE2ETests'] == 0]

        return df_with_e2e,df_without_e2e


    @staticmethod
    def normalize_ind_var():
        output_path = f'/RQ2/rq2_data.xlsx'
        df = pd.read_excel(output_path)
        columns_to_normalize = ['nLOC', 'nContributors', 'nStars', 'nCommits','watchers','size','githubAge', 'nOtherTest']

        scaler = MinMaxScaler()
        df[columns_to_normalize] = scaler.fit_transform(df[columns_to_normalize])
        return df

    @staticmethod
    def check_normal_distribution(df_with_e2e,df_without_e2e):
        columns_to_test = ['nLOC', 'nContributors', 'nStars', 'nCommits', 'githubAge', 'nOtherTest']
        normality_results = {}
        for column in columns_to_test:
            statistic_with_e2e, p_value_with_e2e = lilliefors(df_with_e2e[column])
            statistic_without_e2e, p_value_without_e2e = lilliefors(df_without_e2e[column])

            normality_results[column] = {
                'df_with_e2e': {'statistic': statistic_with_e2e, 'p-value': p_value_with_e2e},
                'df_without_e2e': {'statistic': statistic_without_e2e, 'p-value': p_value_without_e2e}
            }
        return normality_results


    @staticmethod
    def create_boxplot(df_with_e2e,df_without_e2e):
        df_with_e2e['set'] = 'GUI Tested'
        df_without_e2e['set'] = 'No GUI Tested'
        # Concatena i DataFrame per creare un unico DataFrame
        df_combined = pd.concat([df_with_e2e, df_without_e2e])

        # Variabili di interesse per il boxplot
        columns_to_test = ['nLOC', 'nContributors', 'nStars', 'nCommits', 'githubAge', 'nOtherTest']

        # Converti il DataFrame in formato long per il plotting
        df_long = df_combined.melt(id_vars='set', value_vars=columns_to_test, var_name='indipendent variable', value_name='normalized value')

        # Crea il boxplot
        plt.figure(figsize=(10, 8))
        sns.boxplot(data=df_long, x='normalized value', y='indipendent variable', hue='set', palette="Set2",showfliers=False)
        plt.title("Boxplot Independent Variables")
        plt.legend(title="", loc="upper right")
        #plt.show()
        plt.tight_layout()  # Ottimizza il layout
        output_path = f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ2/your_plot.png'  # Modifica il percorso di salvataggio
        plt.savefig(output_path, bbox_inches='tight')  # bbox_inches='tight' per ridurre gli spazi bianchi

    @staticmethod
    def calculate_mann_delta(df_with_e2e,df_without_e2e):
        results = {}
        columns_to_test = ['nLOC', 'nContributors', 'nStars', 'nCommits', 'githubAge', 'nOtherTest']
        for column in columns_to_test:
            group1 = df_with_e2e[column]
            group2 = df_without_e2e[column]

            # Test di Mann-Whitney
            u_statistic, p_value = stats.mannwhitneyu(group1, group2, alternative='two-sided')
            d,res = cliffs_delta(group1,group2)
            # Salvataggio dei risultati
            results[column] = {
                'U statistic': u_statistic,
                'p-value': p_value,
                'Cliff\'s Delta': res
            }
        return results


    @staticmethod
    def create_logistic_model(df):
        df['nE2ETests'] = df['nE2ETests'].apply(lambda x: 1 if x > 0 else 0)
        #X = df[['nLOC', 'nContributors', 'nStars', 'nCommits','watchers','size','githubAge', 'nOtherTest']]
        X = df[['nLOC', 'nContributors','size','githubAge', 'nOtherTest']]
        y = df[['nE2ETests']]
        # Add a constant to the independent variables
        X = sm.add_constant(X)
        # Fit the logistic regression model
        model = sm.Logit(y, X)
        result = model.fit()
        # Print the summary of the model
        print(result.summary())
        # Calculate VIF for each feature
        vif_data = pd.DataFrame()
        vif_data["feature"] = X.columns
        vif_data["VIF"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]

        # Display features with VIF > 5
        print(vif_data[vif_data["VIF"] > 5])


    @staticmethod
    def get_repo_to_accept():
        res = []
        df = pd.read_csv(
            f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ1/repo_to_analyze.csv',
            header=None)
        for index, row in df.iterrows():
            # repo_name = web_repo.name
            # original_name = repo_name.replace('/', '\\')
            # new_name = repo_name.replace('/', '_')
            repo_name = row[0].replace('_', '/', 1)
            res.append(repo_name)
            #original_name = repo_name.replace('/', '\\')
            #new_name = repo_name.replace('/', '_')
        return  res



repos_with_gui_to_accept = LinearModel.get_repo_to_accept()
print(len(repos_with_gui_to_accept))
LinearModel.create_dataset(repos_with_gui_to_accept)
#LinearModel.calculate_correlation()

df_with_e2e, df_without_e2e = LinearModel.normalize_and_split_dataframe()
print(len(df_with_e2e))
print(len(df_without_e2e))
#df = LinearModel.normalize_ind_var()

#LinearModel.create_boxplot(df_with_e2e,df_without_e2e)

#normality_results = LinearModel.check_normal_distribution(df_with_e2e,df_without_e2e)
#print(normality_results)

#res = LinearModel.calculate_mann_delta(df_with_e2e,df_without_e2e)
#print(res)

#LinearModel.calculate_correlation(df_with_e2e,df_without_e2e)

#LinearModel.create_logistic_model(df)
