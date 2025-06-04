import os
from pathlib import Path
import  pandas as pd
from Dataset.Repository import E2ERepository


class CreateE2ERepoTable:
    java_folder = f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/data/java_test_analysis'
    js_ts_folder = f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/data/js_ts_test_analysis'
    py_folder = f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/data/py_test_analysis'
    missed_repo = f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/data/missed_repo'

    @staticmethod
    def check_java_test(file,e2e_repo):
        df = pd.read_csv(CreateE2ERepoTable.java_folder+"/"+file)
        filtered_df = df[df['Number of @Test']>0]
        for index, row in filtered_df.iterrows():
            is_selenium = row['Is Selenium']
            is_playwright = row['Is Playwright']
            with_junit = row['With JUnit']
            with_testng = row['With TestNG']
            num_test = row['Number of @Test']

            if is_selenium == 1 and with_testng ==1:
                e2e_repo.with_testng+=1
                e2e_repo.selenium_java+=1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_selenium == 1 and with_junit==1:
                e2e_repo.with_junit+=1
                e2e_repo.selenium_java+=1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            if is_playwright ==1 and with_testng==1:
                e2e_repo.with_testng += 1
                e2e_repo.playwright_java += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_playwright == 1 and with_junit == 1:
                e2e_repo.with_junit += 1
                e2e_repo.playwright_java += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test

    @staticmethod
    def check_js_ts_test(file,e2e_repo):
        df = pd.read_csv(CreateE2ERepoTable.js_ts_folder+"/"+file)
        filtered_df = df[df['Number of @Test'] > 0]
        for index, row in filtered_df.iterrows():
            is_selenium_js = row['Is Selenium JS']
            is_selenium_ts = row['Is Selenium TS']
            is_play_js = row['Is Playwright JS']
            is_play_ts = row['Is Playwright TS ']
            is_puppeteer_js = row['Is Puppeteer JS']
            is_puppeteer_ts = row['Is Puppeteer TS']
            is_cypress_js = row[ 'Is Cypress JS']
            is_cypress_ts = row['Is Cypress TS']
            with_jest = row['With Jest']
            with_mocha= row['With Mocha']
            with_jasmine =row['With Jasmine']
            num_test= row['Number of @Test']
               #selenium
            if is_selenium_js ==1 and with_jest==1:
                e2e_repo.selenium_js+=1
                e2e_repo.with_jest+=1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_selenium_js==1 and with_mocha==1:
                e2e_repo.selenium_js+=1
                e2e_repo.with_mocha+=1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_selenium_js==1 and with_jasmine==1:
                e2e_repo.selenium_js+=1
                e2e_repo.with_jasmine+=1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test

            if is_selenium_ts ==1 and with_jest==1:
                e2e_repo.selenium_ts+=1
                e2e_repo.with_jest+=1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_selenium_ts==1 and with_mocha==1:
                e2e_repo.selenium_ts+=1
                e2e_repo.with_mocha+=1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_selenium_ts==1 and with_jasmine==1:
                e2e_repo.selenium_ts+=1
                e2e_repo.with_jasmine+=1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test

            #playwright
            if is_play_js == 1 and with_jest == 1:
                e2e_repo.playwright_js += 1
                e2e_repo.with_jest += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_play_js == 1 and with_mocha == 1:
                e2e_repo.playwright_js += 1
                e2e_repo.with_mocha += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_play_js == 1 and with_jasmine == 1:
                e2e_repo.playwright_js += 1
                e2e_repo.with_jasmine += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test

            if is_play_ts == 1 and with_jest == 1:
                e2e_repo.playwright_ts += 1
                e2e_repo.with_jest += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_play_ts == 1 and with_mocha == 1:
                e2e_repo.playwright_ts += 1
                e2e_repo.with_mocha += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_play_ts == 1 and with_jasmine == 1:
                e2e_repo.playwright_ts += 1
                e2e_repo.with_jasmine += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test

            #puppeteer
            if is_puppeteer_js == 1 and with_jest == 1:
                e2e_repo.puppeteer_js += 1
                e2e_repo.with_jest += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_puppeteer_js == 1 and with_mocha == 1:
                e2e_repo.puppeteer_js += 1
                e2e_repo.with_mocha += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_puppeteer_js == 1 and with_jasmine == 1:
                e2e_repo.puppeteer_js += 1
                e2e_repo.with_jasmine += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test

            if is_puppeteer_ts == 1 and with_jest == 1:
                e2e_repo.puppeteer_ts += 1
                e2e_repo.with_jest += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_puppeteer_ts == 1 and with_mocha == 1:
                e2e_repo.puppeteer_ts += 1
                e2e_repo.with_mocha += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_puppeteer_ts == 1 and with_jasmine == 1:
                e2e_repo.puppeteer_ts += 1
                e2e_repo.with_jasmine += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test

            #cypress
            if is_cypress_js == 1:
                e2e_repo.cypress_js += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test

            if is_cypress_ts == 1:
                e2e_repo.cypress_ts += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test



    @staticmethod
    def check_py_test(file,e2e_repo):
        df = pd.read_csv(CreateE2ERepoTable.py_folder+"/"+file)
        filtered_df = df[df['Number of @Test'] > 0]
        for index, row in filtered_df.iterrows():
            is_selenium = row['Is Selenium']
            is_play = row['Is Playwright']
            is_puppeteer = row['Is Puppeteer']
            with_pytest = row['With Pytest']
            with_unittest= row['With Unittest']
            num_test= row['Number of @Test']

            if is_selenium == 1 and with_pytest==1:
                e2e_repo.selenium_py+=1
                e2e_repo.with_pytest+=1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_selenium == 1 and with_unittest==1:
                e2e_repo.selenium_py+=1
                e2e_repo.with_unittest+=1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test

            if is_play == 1 and with_pytest == 1:
                e2e_repo.playwright_py += 1
                e2e_repo.with_pytest += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_play == 1 and with_unittest == 1:
                e2e_repo.playwright_py += 1
                e2e_repo.with_unittest += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test

            if is_puppeteer == 1 and with_pytest == 1:
                e2e_repo.puppeteer_py += 1
                e2e_repo.with_pytest += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_puppeteer == 1 and with_unittest == 1:
                e2e_repo.puppeteer_py += 1
                e2e_repo.with_unittest += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test


    @staticmethod
    def check_missed_repo_test(file,e2e_repo):
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
            with_junit = row['with_junit']
            with_testng = row['with_testng']
            with_jest = row['with_jest']
            with_mocha = row['with_mocha']
            with_jasmine = row['with_jasmine']
            with_pytest = row['with_pytest']
            with_unittest= row['with_unittest']
            num_test = row['number of test']


            #java
            if is_selenium_java == 1 and with_testng == 1:
                e2e_repo.with_testng += 1
                e2e_repo.selenium_java += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_selenium_java == 1 and with_junit == 1:
                e2e_repo.with_junit += 1
                e2e_repo.selenium_java += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            if is_play_java == 1 and with_testng == 1:
                e2e_repo.with_testng += 1
                e2e_repo.playwright_java += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_play_java == 1 and with_junit == 1:
                e2e_repo.with_junit += 1
                e2e_repo.playwright_java += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test

            #js ts
            # selenium
            if is_selenium_js == 1 and with_jest == 1:
                e2e_repo.selenium_js += 1
                e2e_repo.with_jest += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_selenium_js == 1 and with_mocha == 1:
                e2e_repo.selenium_js += 1
                e2e_repo.with_mocha += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_selenium_js == 1 and with_jasmine == 1:
                e2e_repo.selenium_js += 1
                e2e_repo.with_jasmine += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test

            if is_selenium_ts == 1 and with_jest == 1:
                e2e_repo.selenium_ts += 1
                e2e_repo.with_jest += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_selenium_ts == 1 and with_mocha == 1:
                e2e_repo.selenium_ts += 1
                e2e_repo.with_mocha += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_selenium_ts == 1 and with_jasmine == 1:
                e2e_repo.selenium_ts += 1
                e2e_repo.with_jasmine += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test

            # playwright
            if is_play_js == 1 and with_jest == 1:
                e2e_repo.playwright_js += 1
                e2e_repo.with_jest += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_play_js == 1 and with_mocha == 1:
                e2e_repo.playwright_js += 1
                e2e_repo.with_mocha += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_play_js == 1 and with_jasmine == 1:
                e2e_repo.playwright_js += 1
                e2e_repo.with_jasmine += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test

            if is_play_ts == 1 and with_jest == 1:
                e2e_repo.playwright_ts += 1
                e2e_repo.with_jest += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_play_ts == 1 and with_mocha == 1:
                e2e_repo.playwright_ts += 1
                e2e_repo.with_mocha += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_play_ts == 1 and with_jasmine == 1:
                e2e_repo.playwright_ts += 1
                e2e_repo.with_jasmine += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test

            # puppeteer
            if is_puppeteer_js == 1 and with_jest == 1:
                e2e_repo.puppeteer_js += 1
                e2e_repo.with_jest += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_puppeteer_js == 1 and with_mocha == 1:
                e2e_repo.puppeteer_js += 1
                e2e_repo.with_mocha += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_puppeteer_js == 1 and with_jasmine == 1:
                e2e_repo.puppeteer_js += 1
                e2e_repo.with_jasmine += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test

            if is_puppeteer_ts == 1 and with_jest == 1:
                e2e_repo.puppeteer_ts += 1
                e2e_repo.with_jest += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_puppeteer_ts == 1 and with_mocha == 1:
                e2e_repo.puppeteer_ts += 1
                e2e_repo.with_mocha += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_puppeteer_ts == 1 and with_jasmine == 1:
                e2e_repo.puppeteer_ts += 1
                e2e_repo.with_jasmine += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test

            # cypress
            if is_cypress_js == 1:
                e2e_repo.cypress_js += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test

            if is_cypress_ts == 1:
                e2e_repo.cypress_ts += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test

            #python
            if is_selenium_py == 1 and with_pytest == 1:
                e2e_repo.selenium_py += 1
                e2e_repo.with_pytest += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_selenium_py == 1 and with_unittest == 1:
                e2e_repo.selenium_py += 1
                e2e_repo.with_unittest += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test

            if is_play_py == 1 and with_pytest == 1:
                e2e_repo.playwright_py += 1
                e2e_repo.with_pytest += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_play_py == 1 and with_unittest == 1:
                e2e_repo.playwright_py += 1
                e2e_repo.with_unittest += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test

            if is_puppeteer_py == 1 and with_pytest == 1:
                e2e_repo.puppeteer_py += 1
                e2e_repo.with_pytest += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test
            elif is_puppeteer_py == 1 and with_unittest == 1:
                e2e_repo.puppeteer_py += 1
                e2e_repo.with_unittest += 1
                e2e_repo.number_of_file += 1
                e2e_repo.number_of_test += num_test

    @staticmethod
    def create_e2e_obj(csv_file_name):
        repo_name = csv_file_name.replace('.csv', '').replace('_', '/', 1)
        e2e_repo = E2ERepository(repo_name)
        if os.path.exists(CreateE2ERepoTable.java_folder+"/"+csv_file_name):
            CreateE2ERepoTable.check_java_test(csv_file_name,e2e_repo)
        if os.path.exists(CreateE2ERepoTable.js_ts_folder+"/"+csv_file_name):
            CreateE2ERepoTable.check_js_ts_test(csv_file_name,e2e_repo)
        if os.path.exists(CreateE2ERepoTable.py_folder+"/"+csv_file_name):
            CreateE2ERepoTable.check_py_test(csv_file_name,e2e_repo)
        if os.path.exists(CreateE2ERepoTable.missed_repo+"/"+csv_file_name):
            CreateE2ERepoTable.check_missed_repo_test(csv_file_name,e2e_repo)
        if e2e_repo.number_of_test > 0:
            e2e_repo.add_e2erepository_to_db()

    @staticmethod
    def add_rows_to_e2erepository_db():

        paths = [CreateE2ERepoTable.java_folder, CreateE2ERepoTable.js_ts_folder,CreateE2ERepoTable.py_folder,CreateE2ERepoTable.missed_repo]
        unique_filenames = set()
        for path in paths:
            p = Path(path)
            if p.is_dir():
                for file in p.iterdir():
                    if file.is_file():
                        if file.name != "result.csv":
                            unique_filenames.add(file.name)

        #unique_filenames = {filename.replace('.csv', '').replace('_', '/', 1) for filename in unique_filenames}
        for unique_filename in unique_filenames:
            print(unique_filename)
            CreateE2ERepoTable.create_e2e_obj(unique_filename)



if __name__ == "__main__":
    CreateE2ERepoTable.add_rows_to_e2erepository_db()