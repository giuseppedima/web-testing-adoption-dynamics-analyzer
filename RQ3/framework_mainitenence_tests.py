import os

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

class FrameworkTest:

    java_folder_path = f'/home/sergio/IdeaProjects/MSR25-WebGUITesting/RQ1/number_of_test_analysis/java_test_analysis'
    js_ts_folder_path = f'/home/sergio/IdeaProjects/MSR25-WebGUITesting/RQ1/number_of_test_analysis/js_ts_test_analysis'
    py_folder_path = f'/home/sergio/IdeaProjects/MSR25-WebGUITesting/RQ1/number_of_test_analysis/py_test_analysis'
    missed_repo = f'/home/sergio/IdeaProjects/MSR25-WebGUITesting/RQ1/number_of_test_analysis/js_ts_test_analysis/missed_repo'

    @staticmethod
    def java_check(csv_file_path,test_path):
        to_replace ='/home/sergio/ICST25-E2EMining/clone/'
        # Scorri tutti i file nella directory e nelle sue sottocartelle
        #java_folder_path = Path(java_folder_path)
        try:
            '''
            for root, dirs, files in os.walk(java_folder_path):
                for file in files:
                    if file.endswith('.csv') and file != 'result.csv':
                        file_path = os.path.join(root, file)
            '''
            csv_file = pd.read_csv(csv_file_path)
            for index,row in csv_file.iterrows():
                repo= row.iloc[0]
                new_repo = repo.replace('/','_')
                test = row.iloc[1]
                test = test.replace(to_replace+new_repo+'/','')
                if test == test_path:
                    selenium = row.iloc[4]
                    play = row.iloc[5]
                    if selenium == 1:
                        return 'selenium'
                    elif play == 1:
                        return 'playwright'
        except Exception as e:
            print(f' errore :{csv_file_path} {e}')
            exit(0)
        return  None
    @staticmethod
    def js_ts_check(csv_file_path, test_path):
        to_replace ='/home/sergio/ICST25-E2EMining/clone/'
        # Scorri tutti i file nella directory e nelle sue sottocartelle
        #java_folder_path = Path(js_ts_folder_path)
        try:
            ''''
            for root, dirs, files in os.walk(java_folder_path):
                for file in files:
                    if file.endswith('.csv') and file != 'result.csv':
                        file_path = os.path.join(root, file)
            '''
            csv_file = pd.read_csv(csv_file_path)
            for index,row in csv_file.iterrows():
                repo= row.iloc[0]
                new_repo = repo.replace('/','_')
                test = row.iloc[1]
                test = test.replace(to_replace+new_repo+'/','')
                if test == test_path:
                    if int(row.iloc[4])+int(row.iloc[5]) == 1:
                        return 'selenium'
                    elif int(row.iloc[6])+int(row.iloc[7]) == 1:
                        return 'playwright'
                    elif int(row.iloc[8])+int(row.iloc[9]) == 1:
                        return 'puppeteer'
                    elif int(row.iloc[10])+int(row.iloc[11]) == 1:
                        return 'cypress'
        except Exception as e:
            print(f' errore :{csv_file_path} {e}')
            exit(0)
        return  None

    @staticmethod
    def py_check(csv_file_path,test_path):
        to_replace ='/home/sergio/ICST25-E2EMining/clone/'
        # Scorri tutti i file nella directory e nelle sue sottocartelle
        #java_folder_path = Path(py_folder_path)
        try:
            '''
            for root, dirs, files in os.walk(java_folder_path):
                for file in files:
                    if file.endswith('.csv') and file != 'result.csv':
                        file_path = os.path.join(root, file)
                        '''
            csv_file = pd.read_csv(csv_file_path)
            for index,row in csv_file.iterrows():
                repo= row.iloc[0]
                new_repo = repo.replace('/','_')
                test = row.iloc[1]
                test = test.replace(to_replace+new_repo+'/','')
                if test == test_path:
                    if int(row.iloc[4])== 1:
                        return 'selenium'
                    elif int(row.iloc[5]) == 1:
                        return 'playwright'
                    elif int(row.iloc[6]) == 1:
                        return 'puppeteer'
        except Exception as e:
            print(f' errore :{csv_file_path} {e}')
            exit(0)
        return  None

    @staticmethod
    def missed_repo_check(csv_file_path,test_path):
        to_replace = '/home/sergio/ICST25-E2EMining/clone/'
        # Scorri tutti i file nella directory e nelle sue sottocartelle
       # java_folder_path = Path(missed_repo)
        try:
            '''
            for root, dirs, files in os.walk(java_folder_path):
                for file in files:
                    if file.endswith('.csv') and file != 'result.csv':
                        file_path = os.path.join(root, file)
                        '''
            csv_file = pd.read_csv(csv_file_path)
            for index, row in csv_file.iterrows():
                repo = row.iloc[0]
                new_repo = repo.replace('/', '_')
                test = row.iloc[1]
                test = test.replace(to_replace + new_repo + '/', '')
                if test == test_path:
                    if int(row.iloc[2]) + int(row.iloc[3]) + int(row.iloc[4]) + int(row.iloc[5]) == 1:
                        return 'selenium'
                    elif int(row.iloc[6]) + int(row.iloc[7]) + int(row.iloc[8]) + int(row.iloc[9]) == 1:
                        return 'playwright'
                    elif int(row.iloc[10]) + int(row.iloc[11]) + int(row.iloc[12]):
                        return 'puppeteer'
                    elif int(row.iloc[13]) + int(row.iloc[14]):
                        return 'cypress'
        except Exception as e:
            print(f' errore :{csv_file_path} {e}')
            exit(0)
        return None

    @staticmethod
    def retrive_framework(test_path,num_test_file):
        if os.path.exists(os.path.join(FrameworkTest.java_folder_path,num_test_file)):
            framework = FrameworkTest.java_check(os.path.join(FrameworkTest.java_folder_path,num_test_file),test_path)
            if(framework is not None):
                return framework
        if os.path.exists(os.path.join(FrameworkTest.js_ts_folder_path, num_test_file)):
            framework = FrameworkTest.js_ts_check(os.path.join(FrameworkTest.js_ts_folder_path, num_test_file),test_path)
            if (framework is not None):
                return framework
        if os.path.exists(os.path.join(FrameworkTest.py_folder_path, num_test_file)):
            framework= FrameworkTest.py_check(os.path.join(FrameworkTest.py_folder_path, num_test_file),test_path)
            if framework is not None:
                    return framework
        if os.path.exists(os.path.join(FrameworkTest.missed_repo, num_test_file)):
            framework= FrameworkTest.missed_repo_check(os.path.join(FrameworkTest.missed_repo, num_test_file),test_path)
            if framework is not None:
                return  framework
        return None


    '''
    @staticmethod
    def fetch_frameworks_for_test():
        df_tests = pd.read_excel('/home/sergio/IdeaProjects/MSR25-WebGUITesting/RQ3/tests_maintenance_metrics.xlsx')
        df_tests['testpath(blob)'] = df_tests['testpath(blob)'].str.replace(r'_\(\d+\)$', '', regex=True)
        # Aggiunge una nuova colonna 'framework' vuota
        df_tests['framework'] = ''
        previous_test =''
        for index,row in df_tests.iterrows():
            test_path = row.iloc[0]
            if previous_test != test_path:
                framework = FrameworkTest.retrive_framework(test_path)
                # Assegna il framework alla colonna 'framework' della riga corrente
                df_tests.at[index, 'framework'] = framework

            # Assegno lo stesso framework allo stesso test_path
            df_tests.at[index, 'framework'] = framework
            previous_test = test_path
        # Salva il DataFrame aggiornato nel file Excel (sovrascrive il file originale)
        df_tests.to_excel('/home/sergio/IdeaProjects/MSR25-WebGUITesting/RQ3/tests_maintenance_metrics.xlsx',index=False)
    '''


    @staticmethod
    def fetch_framewroks_for_test():
        # Crea un DataFrame vuoto con le colonne desiderate
        columns = ['repo','testpath(blob)', 'svday', 'svmod', 'svac', 'svsc','framework']
        df_res = pd.DataFrame(columns=columns)
        directory_path=f'/home/sergio/IdeaProjects/MSR25-WebGUITesting/RQ3/commits_analysis'
        previous_test =''
        for root, dirs, files in os.walk(directory_path):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                tests_file_cycle= f'commits_analysis'+dir_name+'_tests_lifecycle_analysis.xlsx'
                if(os.path.exists(os.path.join(dir_path,tests_file_cycle))):
                    df_tests = pd.read_excel(os.path.join(dir_path,tests_file_cycle))
                    df_tests['testpath(blob)'] = df_tests['testpath(blob)'].str.replace(r'_\(\d+\)$', '', regex=True)
                    for index, row in df_tests.iterrows():
                        test_path = row.iloc[0]
                        if previous_test != test_path:
                            num_test_file = dir_name+'.csv'
                            framework = FrameworkTest.retrive_framework(test_path,num_test_file)
                            # Assegna il framework alla colonna 'framework' della riga corrente
                            new_row = {
                                'repo':dir_name,
                                'testpath(blob)': test_path,
                                'svday': row.iloc[1],
                                'svmod': row.iloc[2],
                                'svac': row.iloc[3],
                                'svsc': row.iloc[4],
                                'framework' : framework
                            }
                            # Aggiungi la riga al DataFrame
                            df_res = pd.concat([df_res, pd.DataFrame([new_row])], ignore_index=True)
                        # Assegno lo stesso framework allo stesso test_path
                        new_row = {
                            'repo': dir_name,
                            'testpath(blob)': test_path,
                            'svday': row.iloc[1],
                            'svmod': row.iloc[2],
                            'svac': row.iloc[3],
                            'svsc': row.iloc[4],
                            'framework': framework
                        }
                        # Aggiungi la riga al DataFrame
                        df_res = pd.concat([df_res, pd.DataFrame([new_row])], ignore_index=True)
                        previous_test = test_path
        df_res.to_excel('/home/sergio/IdeaProjects/MSR25-WebGUITesting/RQ3/tests_maintenance_metrics_frameworks.xlsx',index=False)


    @staticmethod
    def create_box_plot():
        # Leggi il file Excel
        df = pd.read_excel('/home/sergio/IdeaProjects/MSR25-WebGUITesting/RQ3/tests_maintenance_metrics_frameworks.xlsx')

        # Raggruppa i dati per framework (selenium, cypress, playwright, puppeteer)
        frameworks = ['selenium', 'cypress', 'playwright', 'puppeteer']

        # Definisci una palette di colori per i framework
        palette = {
            'selenium': 'skyblue',  # Colore per Selenium
            'cypress': 'lightgreen',  # Colore per Cypress
            'playwright': 'salmon',  # Colore per Playwright
            'puppeteer': 'lightcoral'  # Colore per Puppeteer
        }

        # Crea una figura con 4 sottotrame (4 boxplot)
        fig, axes = plt.subplots(1, 4, figsize=(20, 5))

        # Dati per ogni metrica
        metrics = ['svday', 'svmod', 'svac', 'svsc']

        # Itera sulle metriche e crea un boxplot per ciascuna
        for i, metric in enumerate(metrics):
            ax = axes[i]
            sns.boxplot(x='framework', y=metric, data=df[df['framework'].isin(frameworks)], ax=ax,
                        hue='framework', palette=palette, legend=False)  # Usa hue per associare i colori
            ax.set_title(f'Boxplot per {metric}')
            ax.set_xlabel('Framework')
            ax.set_ylabel(metric)

        # Aggiusta la disposizione degli elementi
        plt.tight_layout()

        # Mostra i boxplot
        plt.show()





FrameworkTest.create_box_plot()