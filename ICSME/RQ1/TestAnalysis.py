import os
import re
import shutil

import pandas as pd

from CommitAnalyzer.commitAnalyzer_perf import CommitAnalyzerPerf


class TestAnalysis:

    @staticmethod
    def create_perf_repo_details():
        path = f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/CommitAnalyzer/changes_to_analyze.csv'
        df = pd.read_csv(path)
        valori_unici = df['test']
        return  valori_unici


    @staticmethod
    def save_file_without_index():
        records = CommitAnalyzerPerf.get_repos_and_perf_test()
        map = CommitAnalyzerPerf.create_repo_test_map(records)
        #keys = list(map.keys())  # Ottieni le chiavi come lista
        keys = ['eugenp/tutorials']
        prefix = f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/ICSME/performance_test_commit_analysis/'
        pattern = re.compile(r"(.+)_([0-9]+)\.txt$")
        for repo_name in keys:
            new_name = repo_name.replace('/', '_')
            folder_change = prefix + '' + new_name + '/test_changes/'
            if os.path.exists(folder_change):
                file_groups = {}
                for file in os.listdir(folder_change):
                    match = pattern.match(file)
                    if match:
                        base_name, index = match.groups()
                        index = int(index)
                        if base_name not in file_groups or index > file_groups[base_name][1]:
                            file_groups[base_name] = (file, index)

                for base_name, (highest_file, _) in file_groups.items():
                    src_path = os.path.join(folder_change, highest_file)
                    dest_path = os.path.join(folder_change, base_name)  # Senza estensione
                    shutil.copy(src_path, dest_path)
                    print(f"Copied: {src_path} -> {dest_path}")




    @staticmethod
    def create_csv_for_test_type_and_metrics():
        res = []
        path = f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/CommitAnalyzer/commit_message_perf_tests_new.csv'
        df = pd.read_csv(path)
        tests = df['test'].unique()
        for test in tests:
            res.append([
                test,
                '',
                ''
            ])
        df_res = pd.DataFrame(res,columns=['test','type','metrics'])
        df_res.to_csv('/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/ICSME/RQ1/tests_type_metrics.csv',index=False)


if __name__ == "__main__":
   #TestAnalysis.save_file_without_index()
    TestAnalysis.create_csv_for_test_type_and_metrics()