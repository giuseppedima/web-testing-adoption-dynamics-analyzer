from datetime import datetime

from sqlalchemy import or_

from CommitAnalyzer.commitAnalyzer_perf import CommitAnalyzerPerf
from Dataset.DBconnector import Session, engine
from Dataset.Repository import NonTrivialRepo, Repository, GUITestingRepoDetails
import pandas as pd

class Utils:


    @staticmethod
    def fill_perf_test():
        records = CommitAnalyzerPerf.get_repos_and_perf_test()
        map = CommitAnalyzerPerf.create_repo_test_map(records)
        keys = list(map.keys())
        file_path = '/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/ICSME/RQ2/rq2_data.xlsx'
        df = pd.read_excel(file_path)

        for index,row in df.iterrows():
            repo_name = row["repoName"]
            if repo_name in keys:
                df.at[index,"PerfTest"]=1
            else:
                df.at[index,"PerfTest"]=0

        df.to_excel(file_path,index=False,engine="openpyxl")
        print("Modified!")



    @staticmethod
    def get_nontrivial_repo():
        try:
            session = Session(bind=engine)
            print("Connection successful!")

            # Query directly on Repository table
            records = session.query(NonTrivialRepo).filter(
                or_(
                    NonTrivialRepo.is_web_java == True,
                    NonTrivialRepo.is_web_python==True,
                    NonTrivialRepo.is_web_typescript==True,
                    NonTrivialRepo.is_web_javascript == True
                )
            ).all()

            return records

        except Exception as e:
            print(f"Error connecting to the database: {e}")

        finally:
            session.close()  # Ensure the session is closed after use


    @staticmethod
    def get_repos_from_file():
        file_path = '/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/ICSME/RQ2/rq2_data.xlsx'
        dt = pd.read_excel(file_path)
        repos = dt['repoName'].tolist()
        return repos


    @staticmethod
    def get_missed_repo(non_toy,repo_file):
        not_present= []
        for repo in non_toy:
            repo_name= repo.name
            if repo_name not in repo_file:
                #print(f'{repo_name} non presented!')
                not_present.append(repo_name)
        return not_present;


    @staticmethod
    def calculate_repo_age(last_commit_date, created_at_date):
        last_commit_date_obj = datetime.strptime(last_commit_date, '%Y-%m-%dT%H:%M:%S')
        create_at_date_obj = datetime.strptime(created_at_date, '%Y-%m-%dT%H:%M:%S')
        #current_date = datetime.now()
        years_diff = last_commit_date_obj.year - create_at_date_obj.year
        return years_diff


    @staticmethod
    def get_repo_by_name(repo_name):
        try:
            session = Session(bind=engine)
            print("Connection successful!")
            records = session.query(Repository).filter(
                Repository.name == repo_name
            ).all()
            return  records;
        except Exception as e:
            print(f"Error connecting to the database: {e}")
        finally:
            session.close()  # Ensure the session is closed after use



    @staticmethod
    def fill_missed_repo(missed_repo):
        file_path = '/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/ICSME/RQ2/rq2_data.xlsx'
        df = pd.read_excel(file_path)
        for repo_name in missed_repo:
            print(repo_name)
            repo = Utils.get_repo_by_name(repo_name)[0]
            print(repo.name)
            new_row = {
            "repoName":repo.name,
            "nLOC":repo.code_lines,
            "nContributors":repo.contributors,
            "nStars": repo.stargazers,
            "nCommits":repo.commits,
            "projectAge":Utils.calculate_repo_age(repo.last_commit,repo.created_at),
            "watchers":repo.watchers,
            "size":repo.size,
            "mainLanguage":repo.main_language,
            "nOtherTest":"",
            "PerfTest":"",
            "totalIssue":"",
            "totalIssue_noGA":""
            }
            df = df._append(new_row,ignore_index=True)
        df.to_excel(file_path,index=False, engine='openpyxl')


    @staticmethod
    def get_repo_and_gui_test():
        try:
            session = Session(bind=engine)
            print("Connection successful!")
            records = session.query(GUITestingRepoDetails).all()
            return  records;
        except Exception as e:
            print(f"Error connecting to the database: {e}")
        finally:
            session.close()  # Ensure the session is closed after use

    @staticmethod
    def create_gui_repo_test_list(repos):
        results = []
        for repo in repos:
            repo_name = repo.repository_name
            num_gui_tests = repo.number_of_tests
            results.append({
                'name':repo_name,
                'tests': num_gui_tests
            })
        return results

    @staticmethod
    def get_num_gui_test_by_name(list,repo_name):
        for repo in list:
            if repo['name'] == repo_name:
                return repo['tests']
        return 0



    @staticmethod
    def get_is_web_by_name(list,repo_name):
        for repo in list:
            if repo.name == repo_name:
                return int(repo.is_web_java), int(repo.is_web_javascript), int(repo.is_web_typescript), int(repo.is_web_python)
        print(f'{repo_name} not found!!!')
        return 0,0,0,0


    @staticmethod
    def fill_gui_test_rq2(list):
        file_path = '/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/ICSME/RQ2/rq2_data.xlsx'
        df = pd.read_excel(file_path)
        for index, row in df.iterrows():
            repo_name = row["repoName"]
            num_gui_test = Utils.get_num_gui_test_by_name(list,repo_name)
            df.at[index,"nGUITest"] = num_gui_test
        df.to_excel(file_path, index=False, engine="openpyxl")
        print("Modified!")

    @staticmethod
    def fill_is_web(list):
        file_path = '/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/ICSME/RQ2/rq2_data.xlsx'
        df = pd.read_excel(file_path)
        for index, row in df.iterrows():
            repo_name = row["repoName"]
            is_web_java,is_web_js,is_web_ts,is_web_py = Utils.get_is_web_by_name(list,repo_name)
            df.at[index,"is_web_java"] = is_web_java
            df.at[index,"is_web_js"] = is_web_js
            df.at[index,"is_web_ts"] = is_web_ts
            df.at[index,"is_web_py"] = is_web_py
        df.to_excel(file_path, index=False, engine="openpyxl")
        print("Modified!")






if __name__ == "__main__":

    non_toy_repos = Utils.get_nontrivial_repo()
    print(len(non_toy_repos))
    Utils.fill_is_web(non_toy_repos)


