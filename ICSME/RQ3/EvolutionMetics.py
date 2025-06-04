import pandas as pd
from Dataset.DBconnector import Session, engine
from Dataset.Repository import PerformanceTestingTestDetails,Repository
from RQ3.coEvolutionAnalysis import CoEvolutionAnalysis
from time import perf_counter
import os.path



class EvolutionMetric:

    black_list=[
        'undera/jmeter-plugins',
        'splicemachine/spliceengine',
        'marklogic/marklogic-data-hub',
        'ant-media/ant-media-server',
        'mindsdb/mindsdb',
        'googlecloudplatform/professional-services',
        'medic/cht-core',
        'eugenp/tutorials'
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
    def calculate_resume_with_metic(repos):
        data = []
        commit_analysis_folder = r'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/ICSME/performance_test_commit_analysis/'
        for repo in repos:
            repo_name = repo[0]
            if repo_name not in EvolutionMetric.black_list:
                repo_name = repo_name.replace('/','_')
                repo_commit_analysis_folder= commit_analysis_folder+"/"+repo_name+"/"
                app_span_file = repo_commit_analysis_folder + "commits_analysis" + repo_name + "_app_span_analysis.xlsx"
                gui_span_file = repo_commit_analysis_folder + "commits_analysis" + repo_name + "_gui_span_analysis.xlsx"
                only_app_file = repo_commit_analysis_folder + "commits_analysis" + repo_name + "_only_app.xlsx"
                only_gui_file = repo_commit_analysis_folder + "commits_analysis" + repo_name + "_only_gui.xlsx"
                print(f'sto processando {repo[0]}')
                start = perf_counter()

                # sc_value =len(CoEvolutionAnalysis.get_no_null_colums(only_gui_file))
                print('calcolato sc value')
                sc_value = len(CoEvolutionAnalysis.get_no_null_colums(only_gui_file))
                end = perf_counter()
                print(f"Tempo impiegato: {end - start:.4f} secondi")

                # ac_value = CoEvolutionAnalysis.calculate_C(only_app_file)
                print('calcolato ac value')
                end = perf_counter()
                ac_value = len(CoEvolutionAnalysis.get_no_null_colums(only_app_file))
                print(f"Tempo impiegato: {end - start:.4f} secondi")

                ss_value, ssc_value, ssd_value = CoEvolutionAnalysis.calculate_span_metrics(gui_span_file)
                print('calcolato metriche span gui')
                as_value, asc_value, asd_value = CoEvolutionAnalysis.calculate_span_metrics(app_span_file)
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
        res = pd.DataFrame(data, columns=['repo', 'SC', 'AC', 'SS', 'AS', 'SSd', 'SSc', 'ASc', 'ASd'])
        res.to_excel(f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/ICSME/RQ3/coevolution-metrics_new.xlsx')


    @staticmethod
    def create_unique_file_test_lifecycle(repos):
        data = []
        commit_analysis_folder = r'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/ICSME/performance_test_commit_analysis'
        for repo in repos:
            repo_name = repo[0]
            if repo_name not in EvolutionMetric.black_list:
                repo_name = repo_name.replace('/', '_')
                repo_commit_analysis_folder = commit_analysis_folder + "/" + repo_name + "/"
                file = repo_commit_analysis_folder + "commits_analysis" + repo_name+"_tests_lifecycle_analysis.xlsx"
                if os.path.exists(file):
                    df = pd.read_excel(file)
                    for index,row in df.iterrows():
                        testpath=row['testpath(blob)']
                        svday = row['svday']
                        svmod = row['svmod']
                        svac = row['svac']
                        svsc = row['svsc']
                        data.append([
                            testpath,
                            svday,
                            svmod,
                            svac,
                            svsc
                        ])
                else:
                    print('non presente!')
        df_res = pd.DataFrame(data,columns=['testpath(blob)','svday','svmod','svac','svsc'])
        df_res.to_excel('/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/ICSME/RQ3/maintenance_metric_test.xlsx',index=False)

if __name__ == "__main__":
    repos = EvolutionMetric.get_perf_repo()
    #EvolutionMetric.calculate_resume_with_metic(repos)
    EvolutionMetric.create_unique_file_test_lifecycle(repos)
