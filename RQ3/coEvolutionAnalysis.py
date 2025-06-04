import os.path
from itertools import islice
import re
import pandas as pd
import polars as pl
from time import perf_counter
class CoEvolutionAnalysis:


    @staticmethod
    def count_common_elements(A, B):
        set_A = set(A)
        set_B = set(B)
        common_elements = set_A.intersection(set_B)
        return len(common_elements)

    def count_elements_in_A_not_in_B(A, B):
        set_A = set(A)
        set_B = set(B)
        unique_in_A = set_A.difference(set_B)
        return len(unique_in_A)

    @staticmethod
    def calculate_span_metrics(file_path):
        if os.path.exists(file_path):
            # Carica il file Excel
            df = pl.read_excel(file_path)

            # Numero di righe del file
            row_count = df.height  # Usa .height per ottenere il numero di righe

            # Calcola la media delle colonne 'commit' e 'days'
            commit_mean = df['commit'].mean()
            days_mean = df['days'].mean()

            return row_count, commit_mean, days_mean
        else:
            print(f'Error: file {file_path} not exists')
            return None  # Restituisci None o una tupla di valori di default

    @staticmethod
    def count_elements_in_range(A, B):
        count = 0
        for x in A:
            # Controlla se esiste un elemento in B che soddisfa x <= b <= x + 3
            if any(x <= b <= x + 3 for b in B):
                count += 1
        return count

    @staticmethod
    def get_no_null_colums(file_path):
        # Carica il file in formato Excel o CSV
        if os.path.exists(file_path):
            df = pl.read_excel(file_path)
        else:
            file_path_csv = file_path.replace('.xlsx', '.csv')
            if os.path.exists(file_path_csv):
                df = pl.read_csv(file_path_csv)
            else:
                print(f'{file_path} e {file_path_csv} non trovati!')
                return []  # Restituisce una lista vuota se nessun file esiste

        # Numero totale di righe
        total_rows = df.height

        # Calcola il conteggio dei valori nulli per ciascuna colonna, escludendo la prima
        null_counts = df[:, 1:].select(pl.all().is_null().sum()).to_dict(as_series=False)

        # Trova le colonne che hanno almeno un valore non nullo
        non_null_columns = [col for col, counts in null_counts.items() if counts[0] < total_rows]

        # Trova le colonne che hanno almeno un valore non nullo e estrai l'indice del commit
        commit_indices = []
        for col, counts in null_counts.items():
            if counts[0] < total_rows:  # Colonna con almeno un valore non nullo
                match = re.search(r'Commit (\d+)', col)
                if match:
                    commit_indices.append(int(match.group(1)))  # Aggiungi l'indice del commit

        return commit_indices

        #print(f"Colonne con almeno un valore non nullo: {non_null_columns}")
        #return non_null_columns


    @staticmethod
    def calculate_C(file_path):

        num_commit = 0
        df = None

        # Carica il file Excel
        if os.path.exists(file_path):
            df = pl.read_excel(file_path)
        else:
            print(f'{file_path} non trovato, cambio in csv')
            file_path = file_path.replace('.xlsx', '.csv')
            if os.path.exists(file_path):
                df = pl.read_csv(file_path)
            else:
                print(f'{file_path} non trovato!')
                return num_commit  # Restituisci 0 se il file non esiste

        # Numero totale di righe
        total_rows = df.height

        # Calcola il conteggio dei valori nulli per ciascuna colonna, escludendo la prima
        null_counts = df[:, 1:].select(pl.all().is_null().sum()).to_dict(as_series=False)

        # Conta le colonne che hanno meno valori nulli rispetto al numero totale di righe
        non_null_columns_count = sum(1 for col, counts in null_counts.items() if counts[0] < total_rows)
        print(f"Numero di colonne con almeno un valore non nullo: {non_null_columns_count}")
        return non_null_columns_count  # Restituisci solo il conteggio

    @staticmethod
    def calculate_last_commit():
        commit_analysis_folder = f'/home/sergio/ICST25-E2EMining/webguirepo_commit_analysis'
        df = pd.read_csv(
            f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ1/repo_to_analyze.csv',
            header=None)

        data = []
        #for index, row in islice(df.iterrows(),0,1):
        for index, row in df.iterrows():
            repo_name = row[0]
            repo_commit_analysis_folder = commit_analysis_folder + "/" + repo_name + "/"
            file_path = repo_commit_analysis_folder + "commits_analysis" + repo_name + "_only_gui.xlsx"
            if repo_name != 'keycloak_keycloak':
                print(f'sto processando {row[0]}')
                # Carica il file Excel
                if os.path.exists(file_path):
                    df = pl.read_excel(file_path)
                else:
                    print(f'{file_path} non trovato, cambio in csv')
                    file_path = file_path.replace('.xlsx', '.csv')
                    if os.path.exists(file_path):
                        df = pl.read_csv(file_path)
                    else:
                        print(f'{file_path} non trovato!')

                col_name = df.columns[-1]
                ultimo_commit_data= re.search(r"\((\d{4}-\d{2}-\d{2})", col_name)
                data.append([repo_name,ultimo_commit_data.group(1)])

        # Crea un DataFrame finale e salva in Excel
        res = pd.DataFrame(data, columns=['Repo', 'LastCommitDate'])
        res.to_excel('last_commit.xlsx', index=False)
        print("Dati salvati in 'last_commit.xlsx'")

    @staticmethod
    def calculate_resume_with_metric(start,end):

        # Lista per accumulare le righe
        data = []
        commit_analysis_folder= f'/home/sergio/ICST25-E2EMining/webguirepo_commit_analysis'
        df = pd.read_csv(
            f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ1/repo_to_analyze.csv',
            header=None)
        #for index, row in islice(df.iterrows(),start,end):
        for index, row in df.iterrows():
            repo_name = row[0]
            repo_commit_analysis_folder= commit_analysis_folder+"/"+repo_name+"/"
            app_span_file = repo_commit_analysis_folder+"commits_analysis"+repo_name+"_app_span_analysis.xlsx"
            gui_span_file = repo_commit_analysis_folder+"commits_analysis"+repo_name+"_gui_span_analysis.xlsx"
            only_app_file = repo_commit_analysis_folder+"commits_analysis"+repo_name+"_only_app.xlsx"
            only_gui_file = repo_commit_analysis_folder+"commits_analysis"+repo_name+"_only_gui.xlsx"
            print(f'sto processando {row[0]}')
            start = perf_counter()

            #sc_value =len(CoEvolutionAnalysis.get_no_null_colums(only_gui_file))
            sc_value = 0
            print('calcolato sc value')
            end = perf_counter()
            print(f"Tempo impiegato: {end - start:.4f} secondi")

            #ac_value = CoEvolutionAnalysis.calculate_C(only_app_file)
            ac_value = 0
            print('calcolato ac value')
            end = perf_counter()
            print(f"Tempo impiegato: {end - start:.4f} secondi")

            ss_value,ssc_value,ssd_value = CoEvolutionAnalysis.calculate_span_metrics(gui_span_file)
            print('calcolato metriche span gui')
            as_value,asc_value,asd_value = CoEvolutionAnalysis.calculate_span_metrics(app_span_file)
            print('calcolato metriche span app')
            # Esempio di aggiunta dati (in un ciclo o funzione)
            data.append({
                'repo': repo_name,
                'SC': sc_value,
                'AC': ac_value,
                'SS': ss_value,
                'AS': as_value,
                'SSd': ssd_value,
                'SSc': ssc_value,
                'ASc': asc_value,
                'ASd': asd_value
            })

        #print(data)
        # Alla fine del ciclo, converte la lista in un DataFrame
        res = pd.DataFrame(data, columns=['repo', 'SC', 'AC', 'SS', 'AS', 'SSd', 'SSc', 'ASc', 'ASd'])
        res.to_excel(f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ3/coevolution-metrics_new.xlsx')


    @staticmethod
    def check_missed_repo():
        repo_performed = pd.read_excel(f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ3/coevolution-metrics1.xlsx',header=0)
        list_repo_perf = repo_performed['repo'].to_list()
        df = pd.read_csv(
            f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ1/repo_to_analyze.csv',
            header=None)
        for index, row in df.iterrows():
            repo_name = row[0]
            if repo_name not in list_repo_perf:
                print(f'{repo_name} manca.')



    @staticmethod
    def calculate_metric_for_ass_rule(start,end):
        data = []
        commit_analysis_folder = f'/home/sergio/ICST25-E2EMining/webguirepo_commit_analysis'
        df = pd.read_csv(
            f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ1/repo_to_analyze.csv',
            header=None)
        for index, row in islice(df.iterrows(),start,end):
        #for index, row in df.iterrows():
            repo_name = row[0]
            repo_commit_analysis_folder= commit_analysis_folder+"/"+repo_name+"/"

            only_app_file = repo_commit_analysis_folder+"commits_analysis"+repo_name+"_only_app.xlsx"
            only_gui_file = repo_commit_analysis_folder+"commits_analysis"+repo_name+"_only_gui.xlsx"
            print(f'sto processando {row[0]}')
            start = perf_counter()
            gui_col = CoEvolutionAnalysis.get_no_null_colums(only_gui_file)
            end = perf_counter()
            print(f"Tempo impiegato: {end - start:.4f} secondi")

            app_coll = CoEvolutionAnalysis.get_no_null_colums(only_app_file)
            end = perf_counter()
            print(f"Tempo impiegato: {end - start:.4f} secondi")

            #common_commit = CoEvolutionAnalysis.count_common_elements(gui_col,app_coll)
            #end = perf_counter()
            #print(f"Tempo impiegato: {end - start:.4f} secondi")

            #commit_only_gui = CoEvolutionAnalysis.count_elements_in_A_not_in_B(gui_col,app_coll)
            #end = perf_counter()
            #print(f"Tempo impiegato: {end - start:.4f} secondi")
            #commit_only_app = CoEvolutionAnalysis.count_elements_in_A_not_in_B(app_coll,gui_col)
            commit_app_gui_range =CoEvolutionAnalysis.count_elements_in_range(app_coll,gui_col)
            end = perf_counter()
            print(f"Tempo impiegato: {end - start:.4f} secondi")

            data.append({
                'repo':repo_name,
                'app+gui_3range': commit_app_gui_range,
            })
        # Alla fine del ciclo, converte la lista in un DataFrame
        res = pd.DataFrame(data, columns=['repo', 'app+gui_3range'])
        res.to_excel(f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ3/ass_rule-metrics_range.xlsx')


if __name__ == "__main__":
    CoEvolutionAnalysis.calculate_resume_with_metric(0,1)
    #CoEvolutionAnalysis.check_missed_repo()
    #CoEvolutionAnalysis.calculate_last_commit()
    #CoEvolutionAnalysis.calculate_metric_for_ass_rule(0,1)