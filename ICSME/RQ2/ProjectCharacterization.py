from CommitAnalyzer.commitAnalyzer_perf import CommitAnalyzerPerf
import pandas as pd

class ProjectCharacterization:

    @staticmethod
    def summary_test_changes():
        # records = CommitAnalyzerPerf.get_repos_and_perf_test()
        # repo_test_map = CommitAnalyzerPerf.create_repo_test_map(records)  # Renamed variable
        # keys = list(repo_test_map.keys())  # Get keys as a list
        df = pd.read_csv(
            '/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/CommitAnalyzer/commit_message_perf_tests_new.csv')
        keys = df['repo'].unique()
        result_rows = []
        for repo in keys:
            df_repo = df[(df['repo'] == repo)]
            tests = df_repo['test'].unique()
            for test in tests:
                df_test = df_repo[(df_repo['test'] == test)]
                add_count = df_test[df_test['change type'] == "ModificationType.ADD"].shape[0]
                rename_count = df_test[df_test['change type'] == "ModificationType.RENAME"].shape[0]
                modify_count = df_test[df_test['change type'] == "ModificationType.MODIFY"].shape[0]
                delete_count = df_test[df_test['change type'] == "ModificationType.DELETE"].shape[0]

                history = ";".join(sorted(df_test['commit date'].astype(str).unique()))
                result_rows.append([repo, test, add_count, rename_count, modify_count, delete_count, history])
        # Creazione DataFrame finale
        df_result = pd.DataFrame(result_rows, columns=['repo', 'test', 'ADD', 'RENAME', 'MODIFY', 'DELETE', 'HISTORY'])

        # Salva il DataFrame in un nuovo CSV
        df_result.to_csv(
            '/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/ICSME/RQ2/repo_test_summary.csv',
            index=False)

        print("File CSV creato con successo!")

    @staticmethod
    def create_csv_project_type():
        result_rows = []

        df = pd.read_csv(
            '/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/CommitAnalyzer/commit_message_perf_tests_new.csv')
        keys = df['repo'].unique()
        result_rows = []
        for repo in keys:
            result_rows.append([repo,''])


        df_result = pd.DataFrame(result_rows,columns=['repo', 'category'])

        # Salva il DataFrame in un nuovo CSV
        df_result.to_csv('/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/ICSME/RQ2/repo_category.csv',index=False)
        print("File CSV creato con successo!")

if __name__ == "__main__":
    ProjectCharacterization.create_csv_project_type()



