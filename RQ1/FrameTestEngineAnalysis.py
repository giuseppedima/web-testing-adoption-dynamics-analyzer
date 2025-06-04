import os

import pandas as pd

from Dataset.Repository import WebRepositoryDAO
from ProjectAnalyzer.createE2ERepositoryTable import CreateE2ERepoTable
from Dataset.DBconnector import Session, engine


class FrameTestEngineAnalysis:


    @staticmethod
    def retrive_repo_byname(name):
        try:
            session = Session(bind=engine)
            print("Connection successful!")
            query = session.query(WebRepositoryDAO).filter(
                        WebRepositoryDAO.name==name
                    )
            records = query.all()
            return records
        except Exception as e:
            print(f"Error connecting to the databse : {e}")

    data = {
        'java_web' : {
            'java': {
                'selenium': 0,
                'playwright': 0
            },
            'typescript': {
                'selenium': 0,
                'playwright': 0,
                'puppeeter': 0,
                'cypress': 0
            },
            'javascript': {
                'selenium': 0,
                'playwright': 0,
                'puppeeter': 0,
                'cypress': 0
            },
            'python': {
                'selenium': 0,
                'playwright': 0,
                'puppeeter': 0,
            }
        },
        'js_web': {
            'java': {
                'selenium': 0,
                'playwright': 0
            },
            'typescript': {
                'selenium': 0,
                'playwright': 0,
                'puppeeter': 0,
                'cypress': 0
            },
            'javascript': {
                'selenium': 0,
                'playwright': 0,
                'puppeeter': 0,
                'cypress': 0
            },
            'python': {
                'selenium': 0,
                'playwright': 0,
                'puppeeter': 0,
            }
        },
        'ts_web': {
            'java': {
                'selenium': 0,
                'playwright': 0
            },
            'typescript': {
                'selenium': 0,
                'playwright': 0,
                'puppeeter': 0,
                'cypress': 0
            },
            'javascript': {
                'selenium': 0,
                'playwright': 0,
                'puppeeter': 0,
                'cypress': 0
            },
            'python': {
                'selenium': 0,
                'playwright': 0,
                'puppeeter': 0,
            }
        },
        'py_web': {
            'java': {
                'selenium': 0,
                'playwright': 0
            },
            'typescript': {
                'selenium': 0,
                'playwright': 0,
                'puppeeter': 0,
                'cypress': 0
            },
            'javascript': {
                'selenium': 0,
                'playwright': 0,
                'puppeeter': 0,
                'cypress': 0
            },
            'python': {
                'selenium': 0,
                'playwright': 0,
                'puppeeter': 0,
            }
        }
    }



    @staticmethod
    def check_java_test(file, is_web):
        df = pd.read_csv(CreateE2ERepoTable.java_folder + "/" + file)
        filtered_df = df[df['Number of @Test'] > 0]
        flag_selenium_java = 0
        flag_play_java=0

        for index, row in filtered_df.iterrows():
            is_selenium = row['Is Selenium']
            is_playwright = row['Is Playwright']
            if is_selenium == 1:
                if flag_selenium_java == 0:
                    if is_web[0] == True:
                        FrameTestEngineAnalysis.data['java_web']['java']['selenium']+=1
                    if is_web[1] == True:
                        FrameTestEngineAnalysis.data['js_web']['java']['selenium']+=1
                    if is_web[2] == True:
                        FrameTestEngineAnalysis.data['ts_web']['java']['selenium']+=1
                    if is_web[3] == True:
                        FrameTestEngineAnalysis.data['py_web']['java']['selenium']+=1
                    flag_selenium_java=1

            if is_playwright == 1:
                if flag_play_java == 0:
                    if is_web[0] == True:
                        FrameTestEngineAnalysis.data['java_web']['java']['playwright']+=1
                    if is_web[1] == True:
                        FrameTestEngineAnalysis.data['js_web']['java']['playwright']+=1
                    if is_web[2] == True:
                        FrameTestEngineAnalysis.data['ts_web']['java']['playwright']+=1
                    if is_web[3] == True:
                        FrameTestEngineAnalysis.data['py_web']['java']['playwright']+=1
                    flag_play_java =1


    @staticmethod
    def check_js_ts_test(file,is_web):
        df = pd.read_csv(CreateE2ERepoTable.js_ts_folder + "/" + file)
        flag_selenium_js = 0
        flag_selenium_ts = 0
        flag_play_js =0
        flag_play_ts = 0
        flag_pupp_js = 0
        flag_pupp_ts = 0
        flag_cypress_js = 0
        flag_cypress_ts = 0

        filtered_df = df[df['Number of @Test'] > 0]
        for index, row in filtered_df.iterrows():
            is_selenium_js = row['Is Selenium JS']
            is_selenium_ts = row['Is Selenium TS']
            is_play_js = row['Is Playwright JS']
            is_play_ts = row['Is Playwright TS ']
            is_puppeteer_js = row['Is Puppeteer JS']
            is_puppeteer_ts = row['Is Puppeteer TS']
            is_cypress_js = row['Is Cypress JS']
            is_cypress_ts = row['Is Cypress TS']
            num_test = row['Number of @Test']
            # selenium
            if is_selenium_js == 1 :
                if flag_selenium_js ==0:
                    if is_web[0] == True:
                        FrameTestEngineAnalysis.data['java_web']['javascript']['selenium']+=1
                    if is_web[1] == True:
                        FrameTestEngineAnalysis.data['js_web']['javascript']['selenium']+=1
                    if is_web[2] == True:
                        FrameTestEngineAnalysis.data['ts_web']['javascript']['selenium']+=1
                    if is_web[3] == True:
                        FrameTestEngineAnalysis.data['py_web']['javascript']['selenium']+=1
                    flag_selenium_js=1

            if is_selenium_ts == 1 :
                if flag_selenium_ts ==0:
                    if is_web[0] == True:
                        FrameTestEngineAnalysis.data['java_web']['typescript']['selenium']+=1
                    if is_web[1] == True:
                        FrameTestEngineAnalysis.data['js_web']['typescript']['selenium']+=1
                    if is_web[2] == True:
                        FrameTestEngineAnalysis.data['ts_web']['typescript']['selenium']+=1
                    if is_web[3] == True:
                        FrameTestEngineAnalysis.data['py_web']['typescript']['selenium']+=1
                    flag_selenium_ts=1
           

            # playwright
            if is_play_js == 1 :
                if flag_play_js==0:
                    if is_web[0] == True:
                        FrameTestEngineAnalysis.data['java_web']['javascript']['playwright']+=1
                    if is_web[1] == True:
                        FrameTestEngineAnalysis.data['js_web']['javascript']['playwright']+=1
                    if is_web[2] == True:
                        FrameTestEngineAnalysis.data['ts_web']['javascript']['playwright']+=1
                    if is_web[3] == True:
                        FrameTestEngineAnalysis.data['py_web']['javascript']['playwright']+=1
                    flag_play_js=1
            

            if is_play_ts == 1 :
                if flag_play_ts==0:
                    if is_web[0] == True:
                        FrameTestEngineAnalysis.data['java_web']['typescript']['playwright']+=1
                    if is_web[1] == True:
                        FrameTestEngineAnalysis.data['js_web']['typescript']['playwright']+=1
                    if is_web[2] == True:
                        FrameTestEngineAnalysis.data['ts_web']['typescript']['playwright']+=1
                    if is_web[3] == True:
                        FrameTestEngineAnalysis.data['py_web']['typescript']['playwright']+=1
                    flag_play_ts=1
            

            # puppeteer
            if is_puppeteer_js == 1 :
                if flag_pupp_js ==0:
                    if is_web[0] == True:
                        FrameTestEngineAnalysis.data['java_web']['javascript']['puppeeter']+=1
                    if is_web[1] == True:
                        FrameTestEngineAnalysis.data['js_web']['javascript']['puppeeter']+=1
                    if is_web[2] == True:
                        FrameTestEngineAnalysis.data['ts_web']['javascript']['puppeeter']+=1
                    if is_web[3] == True:
                        FrameTestEngineAnalysis.data['py_web']['javascript']['puppeeter']+=1
                    flag_pupp_js =1
            
            if is_puppeteer_ts == 1 :
                if flag_pupp_ts ==0:
                    if is_web[0] == True:
                        FrameTestEngineAnalysis.data['java_web']['typescript']['puppeeter']+=1
                    if is_web[1] == True:
                        FrameTestEngineAnalysis.data['js_web']['typescript']['puppeeter']+=1
                    if is_web[2] == True:
                        FrameTestEngineAnalysis.data['ts_web']['typescript']['puppeeter']+=1
                    if is_web[3] == True:
                        FrameTestEngineAnalysis.data['py_web']['typescript']['puppeeter']+=1
                    flag_pupp_ts=1
            
            # cypress
            if is_cypress_js == 1:
                if flag_cypress_js == 0:
                    if is_web[0] == True:
                        FrameTestEngineAnalysis.data['java_web']['javascript']['cypress']+=1
                    if is_web[1] == True:
                        FrameTestEngineAnalysis.data['js_web']['javascript']['cypress']+=1
                    if is_web[2] == True:
                        FrameTestEngineAnalysis.data['ts_web']['javascript']['cypress']+=1
                    if is_web[3] == True:
                        FrameTestEngineAnalysis.data['py_web']['javascript']['cypress']+=1
                    flag_cypress_js =1
            if is_cypress_ts == 1:
                if flag_cypress_ts == 0:
                    if is_web[0] == True:
                        FrameTestEngineAnalysis.data['java_web']['typescript']['cypress']+=1
                    if is_web[1] == True:
                        FrameTestEngineAnalysis.data['js_web']['typescript']['cypress']+=1
                    if is_web[2] == True:
                        FrameTestEngineAnalysis.data['ts_web']['typescript']['cypress']+=1
                    if is_web[3] == True:
                        FrameTestEngineAnalysis.data['py_web']['typescript']['cypress']+=1
                    flag_cypress_ts=1

    @staticmethod
    def check_py_test(file,is_web):
        flag_selenium_py=0
        flag_play_py=0
        flag_pupp_py=0
        df = pd.read_csv(CreateE2ERepoTable.py_folder+"/"+file)
        filtered_df = df[df['Number of @Test'] > 0]
        for index, row in filtered_df.iterrows():
            is_selenium = row['Is Selenium']
            is_play = row['Is Playwright']
            is_puppeteer = row['Is Puppeteer']
            num_test= row['Number of @Test']

            if is_selenium == 1 :
                if flag_selenium_py ==0:
                    if is_web[0] == True:
                        FrameTestEngineAnalysis.data['java_web']['python']['selenium']+=1
                    if is_web[1] == True:
                        FrameTestEngineAnalysis.data['js_web']['python']['selenium']+=1
                    if is_web[2] == True:
                        FrameTestEngineAnalysis.data['ts_web']['python']['selenium']+=1
                    if is_web[3] == True:
                        FrameTestEngineAnalysis.data['py_web']['python']['selenium']+=1
                    flag_selenium_py=1


            if is_play == 1 :
                if flag_play_py ==0:
                    if is_web[0] == True:
                        FrameTestEngineAnalysis.data['java_web']['python']['playwright']+=1
                    if is_web[1] == True:
                        FrameTestEngineAnalysis.data['js_web']['python']['playwright']+=1
                    if is_web[2] == True:
                        FrameTestEngineAnalysis.data['ts_web']['python']['playwright']+=1
                    if is_web[3] == True:
                        FrameTestEngineAnalysis.data['py_web']['python']['playwright']+=1
                    flag_play_py=1


            if is_puppeteer == 1 :
                if flag_pupp_py==0:
                    if is_web[0] == True:
                        FrameTestEngineAnalysis.data['java_web']['python']['puppeeter']+=1
                    if is_web[1] == True:
                        FrameTestEngineAnalysis.data['js_web']['python']['puppeeter']+=1
                    if is_web[2] == True:
                        FrameTestEngineAnalysis.data['ts_web']['python']['puppeeter']+=1
                    if is_web[3] == True:
                        FrameTestEngineAnalysis.data['py_web']['python']['puppeeter']+=1
                    flag_pupp_py=1


    @staticmethod
    def check_missed_repo_test(file,is_web):
        flag_selenium_java = 0
        flag_play_java=0
        flag_selenium_js = 0
        flag_selenium_ts = 0
        flag_play_js = 0
        flag_play_ts = 0
        flag_pupp_js = 0
        flag_pupp_ts = 0
        flag_cypress_js = 0
        flag_cypress_ts = 0
        flag_selenium_py=0
        flag_play_py=0
        flag_pupp_py=0


        df = pd.read_csv(CreateE2ERepoTable.missed_repo+"/"+file)
        filtered_df = df[df['number of test'] > 0]
        for index, row in filtered_df.iterrows():
            is_selenium_java = row['selenium_java']
            is_selenium_js= row['selenium_js']
            is_selenium_ts= row['selenium_ts']
            is_selenium_py =row['selenium_py']
            is_play_java = row['playwright_java']
            is_play_js = row['playwright_js']
            is_play_ts =row['playwright_ts']
            is_play_py =row['playwright_py']
            is_puppeteer_js = row['puppeteer_js']
            is_puppeteer_ts = row['puppeteer_ts']
            is_puppeteer_py = row['puppeteer_py']
            is_cypress_js =row['cypress_js']
            is_cypress_ts = row['cypress_ts']
            num_test = row['number of test']

            #JAVA
            if is_selenium_java == 1:
                if flag_selenium_java == 0:
                    if is_web[0] == True:
                        FrameTestEngineAnalysis.data['java_web']['java']['selenium'] += 1
                    if is_web[1] == True:
                        FrameTestEngineAnalysis.data['js_web']['java']['selenium'] += 1
                    if is_web[2] == True:
                        FrameTestEngineAnalysis.data['ts_web']['java']['selenium'] += 1
                    if is_web[3] == True:
                        FrameTestEngineAnalysis.data['py_web']['java']['selenium'] += 1
                    flag_selenium_java = 1

            if is_play_java == 1:
                if flag_play_java == 0:
                    if is_web[0] == True:
                        FrameTestEngineAnalysis.data['java_web']['java']['playwright'] += 1
                    if is_web[1] == True:
                        FrameTestEngineAnalysis.data['js_web']['java']['playwright'] += 1
                    if is_web[2] == True:
                        FrameTestEngineAnalysis.data['ts_web']['java']['playwright'] += 1
                    if is_web[3] == True:
                        FrameTestEngineAnalysis.data['py_web']['java']['playwright'] += 1
                    flag_play_java = 1

            #JS TS
            # selenium
            if is_selenium_js == 1:
                if flag_selenium_js == 0:
                    if is_web[0] == True:
                        FrameTestEngineAnalysis.data['java_web']['javascript']['selenium'] += 1
                    if is_web[1] == True:
                        FrameTestEngineAnalysis.data['js_web']['javascript']['selenium'] += 1
                    if is_web[2] == True:
                        FrameTestEngineAnalysis.data['ts_web']['javascript']['selenium'] += 1
                    if is_web[3] == True:
                        FrameTestEngineAnalysis.data['py_web']['javascript']['selenium'] += 1
                    flag_selenium_js = 1

            if is_selenium_ts == 1:
                if flag_selenium_ts == 0:
                    if is_web[0] == True:
                        FrameTestEngineAnalysis.data['java_web']['typescript']['selenium'] += 1
                    if is_web[1] == True:
                        FrameTestEngineAnalysis.data['js_web']['typescript']['selenium'] += 1
                    if is_web[2] == True:
                        FrameTestEngineAnalysis.data['ts_web']['typescript']['selenium'] += 1
                    if is_web[3] == True:
                        FrameTestEngineAnalysis.data['py_web']['typescript']['selenium'] += 1
                    flag_selenium_ts = 1

            # playwright
            if is_play_js == 1:
                if flag_play_js == 0:
                    if is_web[0] == True:
                        FrameTestEngineAnalysis.data['java_web']['javascript']['playwright'] += 1
                    if is_web[1] == True:
                        FrameTestEngineAnalysis.data['js_web']['javascript']['playwright'] += 1
                    if is_web[2] == True:
                        FrameTestEngineAnalysis.data['ts_web']['javascript']['playwright'] += 1
                    if is_web[3] == True:
                        FrameTestEngineAnalysis.data['py_web']['javascript']['playwright'] += 1
                    flag_play_js = 1

            if is_play_ts == 1:
                if flag_play_ts == 0:
                    if is_web[0] == True:
                        FrameTestEngineAnalysis.data['java_web']['typescript']['playwright'] += 1
                    if is_web[1] == True:
                        FrameTestEngineAnalysis.data['js_web']['typescript']['playwright'] += 1
                    if is_web[2] == True:
                        FrameTestEngineAnalysis.data['ts_web']['typescript']['playwright'] += 1
                    if is_web[3] == True:
                        FrameTestEngineAnalysis.data['py_web']['typescript']['playwright'] += 1
                    flag_play_ts = 1

            # puppeteer
            if is_puppeteer_js == 1:
                if flag_pupp_js == 0:
                    if is_web[0] == True:
                        FrameTestEngineAnalysis.data['java_web']['javascript']['puppeeter'] += 1
                    if is_web[1] == True:
                        FrameTestEngineAnalysis.data['js_web']['javascript']['puppeeter'] += 1
                    if is_web[2] == True:
                        FrameTestEngineAnalysis.data['ts_web']['javascript']['puppeeter'] += 1
                    if is_web[3] == True:
                        FrameTestEngineAnalysis.data['py_web']['javascript']['puppeeter'] += 1
                    flag_pupp_js = 1

            if is_puppeteer_ts == 1:
                if flag_pupp_ts == 0:
                    if is_web[0] == True:
                        FrameTestEngineAnalysis.data['java_web']['typescript']['puppeeter'] += 1
                    if is_web[1] == True:
                        FrameTestEngineAnalysis.data['js_web']['typescript']['puppeeter'] += 1
                    if is_web[2] == True:
                        FrameTestEngineAnalysis.data['ts_web']['typescript']['puppeeter'] += 1
                    if is_web[3] == True:
                        FrameTestEngineAnalysis.data['py_web']['typescript']['puppeeter'] += 1
                    flag_pupp_ts = 1

            # cypress
            if is_cypress_js == 1:
                if flag_cypress_js == 0:
                    if is_web[0] == True:
                        FrameTestEngineAnalysis.data['java_web']['javascript']['cypress'] += 1
                    if is_web[1] == True:
                        FrameTestEngineAnalysis.data['js_web']['javascript']['cypress'] += 1
                    if is_web[2] == True:
                        FrameTestEngineAnalysis.data['ts_web']['javascript']['cypress'] += 1
                    if is_web[3] == True:
                        FrameTestEngineAnalysis.data['py_web']['javascript']['cypress'] += 1
                    flag_cypress_js = 1
            if is_cypress_ts == 1:
                if flag_cypress_ts == 0:
                    if is_web[0] == True:
                        FrameTestEngineAnalysis.data['java_web']['typescript']['cypress'] += 1
                    if is_web[1] == True:
                        FrameTestEngineAnalysis.data['js_web']['typescript']['cypress'] += 1
                    if is_web[2] == True:
                        FrameTestEngineAnalysis.data['ts_web']['typescript']['cypress'] += 1
                    if is_web[3] == True:
                        FrameTestEngineAnalysis.data['py_web']['typescript']['cypress'] += 1
                    flag_cypress_ts = 1

            #python
            if is_selenium_py == 1:
                if flag_selenium_py == 0:
                    if is_web[0] == True:
                        FrameTestEngineAnalysis.data['java_web']['python']['selenium'] += 1
                    if is_web[1] == True:
                        FrameTestEngineAnalysis.data['js_web']['python']['selenium'] += 1
                    if is_web[2] == True:
                        FrameTestEngineAnalysis.data['ts_web']['python']['selenium'] += 1
                    if is_web[3] == True:
                        FrameTestEngineAnalysis.data['py_web']['python']['selenium'] += 1
                    flag_selenium_py = 1

            if is_play_py == 1:
                if flag_play_py == 0:
                    if is_web[0] == True:
                        FrameTestEngineAnalysis.data['java_web']['python']['playwright'] += 1
                    if is_web[1] == True:
                        FrameTestEngineAnalysis.data['js_web']['python']['playwright'] += 1
                    if is_web[2] == True:
                        FrameTestEngineAnalysis.data['ts_web']['python']['playwright'] += 1
                    if is_web[3] == True:
                        FrameTestEngineAnalysis.data['py_web']['python']['playwright'] += 1
                    flag_play_py = 1

            if is_puppeteer_py == 1:
                if flag_pupp_py == 0:
                    if is_web[0] == True:
                        FrameTestEngineAnalysis.data['java_web']['python']['puppeeter'] += 1
                    if is_web[1] == True:
                        FrameTestEngineAnalysis.data['js_web']['python']['puppeeter'] += 1
                    if is_web[2] == True:
                        FrameTestEngineAnalysis.data['ts_web']['python']['puppeeter'] += 1
                    if is_web[3] == True:
                        FrameTestEngineAnalysis.data['py_web']['python']['puppeeter'] += 1
                    flag_pupp_py = 1


    @staticmethod
    def calculate_details():
        df = pd.read_csv(
            f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ1/repo_to_analyze.csv',
            header=None)
        for index, row in df.iterrows():
            repo_name= row[0]
            name_to_fetch = repo_name.replace('_','/',1)
            repo = FrameTestEngineAnalysis.retrive_repo_byname(name_to_fetch)[0]
            is_web = [ repo.is_web_java, repo.is_web_javascript, repo.is_web_typescript, repo.is_web_python]
            csv_file_name = repo_name+".csv"
            if os.path.exists(CreateE2ERepoTable.java_folder + "/" + csv_file_name):
                FrameTestEngineAnalysis.check_java_test(csv_file_name,is_web)
            if os.path.exists(CreateE2ERepoTable.js_ts_folder + "/" + csv_file_name):
                FrameTestEngineAnalysis.check_js_ts_test(csv_file_name,is_web)
            if os.path.exists(CreateE2ERepoTable.py_folder + "/" + csv_file_name):
                FrameTestEngineAnalysis.check_py_test(csv_file_name,is_web)
            if os.path.exists(CreateE2ERepoTable.missed_repo + "/" + csv_file_name):
                FrameTestEngineAnalysis.check_missed_repo_test(csv_file_name,is_web)


if __name__ == "__main__":
    FrameTestEngineAnalysis.calculate_details()
    print(FrameTestEngineAnalysis.data)



