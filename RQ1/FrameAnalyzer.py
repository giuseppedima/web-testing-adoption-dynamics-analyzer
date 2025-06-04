
import  pandas as pd

from Dataset.DBconnector import Session, engine
from Dataset.Repository import GUITestingRepoDetails


class FrameAnalyzer:


    @staticmethod
    def get_repo_by_name(repo_name):
        try:
            session = Session(bind=engine)
            print("Connection successful!")
            records = session.query(GUITestingRepoDetails).filter(
                GUITestingRepoDetails.repository_name==repo_name
            ).first()
            return records;
        except Exception as e:
            print(f"Error connecting to the database: {e}")
        finally:
            session.close()  # Ensure the session is closed after use

    @staticmethod
    def get_191_repo_name():
        df = pd.read_csv('/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/totalIssueAnalysis/repo_191_query.csv')
        list_repo  = df['name']
        return list_repo


    @staticmethod
    def create_csv_frame_adoption(repos):
        result_rows = []
        for repo_name in repos:
            repo = FrameAnalyzer.get_repo_by_name(repo_name)
            num_fil_sel_java = repo.number_files_selenium_java
            num_fil_sel_js = repo.number_files_selenium_js
            num_fil_sel_ts = repo.number_files_selenium_ts
            num_fil_sel_py = repo.number_files_selenium_py
            is_selenium_tested = (num_fil_sel_java+num_fil_sel_js+num_fil_sel_ts+num_fil_sel_py)>0

            num_fil_play_java = repo.number_files_playwright_java
            num_fil_play_js = repo.number_files_playwright_js
            num_fil_play_ts = repo.number_files_playwright_ts
            num_fil_play_py = repo.number_files_playwright_py
            is_playwright_tested = (num_fil_play_py+num_fil_play_ts+num_fil_play_js+num_fil_play_java)>0

            num_fil_pupp_js = repo.number_files_puppeteer_js
            num_fil_pupp_ts = repo.number_files_puppeteer_ts
            num_fil_pupp_py = repo.number_files_puppeteer_py
            is_puppeteer_tested = (num_fil_pupp_js+num_fil_pupp_ts+num_fil_pupp_py)>0

            num_fil_cypress_js = repo.number_files_cypress_js
            num_fil_cypress_ts = repo.number_files_cypress_ts
            is_cypress_tested = (num_fil_cypress_ts+num_fil_cypress_js)>0

            result_rows.append([repo_name,is_selenium_tested,is_playwright_tested,is_puppeteer_tested,is_cypress_tested])

        df_result = pd.DataFrame(result_rows,columns=['repo','selenium_tested','playwright_tested','puppeeter_tested','cypress_tested'])
        df_result.to_csv('/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ1/frame_adoption.csv',index=False)
        print('file csv created!')

if __name__ == "__main__":
    repos = FrameAnalyzer.get_191_repo_name()
    print(len(repos))
    FrameAnalyzer.create_csv_frame_adoption(repos)