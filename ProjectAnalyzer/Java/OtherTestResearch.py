import concurrent
import os
import subprocess
from operator import or_

import pandas as pd
from sqlalchemy.orm import aliased

from CommitAnalyzer.commitAnalyzer import CommitAnalyzer
from Dataset.DBconnector import Session, engine
from Dataset.Repository import WebRepositoryDAO
from ProjectAnalyzer.JSTS.JavascriptDataAnalyzer import JavascriptDataAnalyzer
from RepositoryAnalyzer.RepositoryCloner import Cloner
class OtherTestResearch:


    black_list = ['workiva/frugal','curiefense\curiefense','serverdensity\sd-agent','azure\azure-xplat-cli','moddio/moddio2','xrfoundation/xrengine','smartive/smartive.ch ','plotly/dash-docs','voltdb/voltdb','teamcodestream/codestream','voltdb/voltdb','porter-dev/porter','DeBankDeFi/DeBankChain', 'laboratoria/bootcamp', 'invoiceninja/invoiceninja','zerocracy/farm','workiva/frugal','teamcodestream/codestream','EtherealEngine\etherealengine',]



    @staticmethod
    def fetch_py_repo():
        try:
            session = Session(bind=engine)
            print("Connection successful!")
            query = session.query(WebRepositoryDAO).filter(
                        WebRepositoryDAO.is_web_python==True
                    )
            records = query.all()
            return records
        except Exception as e:
            print(f"Error connecting to the databse : {e}")

    @staticmethod
    def check_jsts_file (path,frameworks):
        is_selenium  = 0
        is_playwright = 0
        is_puppeteer = 0
        is_cypress_js = 0
        with_mocha= 0
        with_jest =0
        with_jasmine= 0
        num_test = 0
        cypress_extensions = ('.cy.js', '.cy.ts', '.cy.jsx', '.cy.tsx')
        if not path.endswith(cypress_extensions):
            if 1 in frameworks:
                with_jest = 1
                num_test = JavascriptDataAnalyzer.get_num_test_test(path)
            if 2 in frameworks:
                with_mocha =1
                num_test,num_lines = JavascriptDataAnalyzer.get_num_test_it(path)
                if num_test == 0:  #caso suite() al posti di describe()
                    num_test = JavascriptDataAnalyzer.get_num_test_test(path)
            if 3 in frameworks:
                with_jasmine =1
                num_test,num_lines = JavascriptDataAnalyzer.get_num_test_it(path)
            try:
                with open(path, 'r') as file:
                    lines = file.readlines()
                for line in lines:
                    if ('selenium-webdriver' in line):
                        is_selenium = 1
                    elif ('@playwright' in line):
                        is_playwright = 1
                        if(num_test == 0): #caso @playwright/test
                            num_test = JavascriptDataAnalyzer.get_num_test_test(path)
                    elif ('puppeteer' in line):
                        is_puppeteer = 1
                        if num_test == 0 and 1 in frameworks: #caso jest-puppeteer
                            num_test,num_lines = JavascriptDataAnalyzer.get_num_test_it(path)
            except FileNotFoundError:
                print(f"File non trovato: {path}")
            except Exception as e:
                print(f"Errore durante l'apertura del file: {e}")
        else:
            num_test,num_lines = JavascriptDataAnalyzer.get_num_test_it(path)
            is_cypress_js= 1

        if is_selenium == 0 and is_playwright==0 and is_puppeteer==0 and is_cypress_js ==0 and num_test>0:
            return True,[path,with_jest,with_mocha,with_jasmine,num_test]
        return False,[]


    @staticmethod
    def enable_git_long_paths():
        try:
            # Enable long paths in Git for the current user
            subprocess.run(['git', 'config', '--global', 'core.longpaths', 'true'], check=True)
            print("Enabled long paths in Git for the current user.")
        except subprocess.CalledProcessError as e:
            print(f"Error enabling long paths in Git: {e}")
            exit(1)

    @staticmethod
    def fetch_jsts_repo():
        try:
            # Tenta di connetterti al database
            session = Session(bind=engine)
            print("Connection successful!")
            query = session.query(WebRepositoryDAO)\
                .filter(
                    or_(
                       WebRepositoryDAO.is_web_javascript == True,
                        WebRepositoryDAO.is_web_typescript==True
                    )
            )
            records = query.all()
            return records

        except Exception as e:
            print(f"Error connecting to the database: {e}")



    @staticmethod
    def fetch_java_webrepo():
        try:
            # Tenta di connetterti al database
            session = Session(bind=engine)
            print("Connection successful!")
            # Esegui il fetch di tutti i record
            # records = session.query(WebRepositoryDAO).all()
            # Stampa i record
            query = session.query(WebRepositoryDAO).filter(
                    WebRepositoryDAO.is_web_java == True,
            )
            records = query.all()
            return records
        except Exception as e:
            print(f"Error connecting to the database: {e}")

    @staticmethod
    def rename_dir(old_name, new_name):
        # Assicurati che il nuovo percorso non esista già
        if not os.path.exists(f"/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/clone/" + new_name):
            # Rinomina la directory
            os.rename(f"/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/clone/" + old_name,
                      f"/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/clone/" + new_name)
            print(f"The directory has been renamed")
        else:
            print(f"Error: The directory already exists!.")


    @staticmethod
    def check_java_file(path):
        is_selenium = 0
        is_playwright= 0
        with_junit = 0
        with_testng = 0
        num_test = 0
        try:
            with open(path, 'r') as file:
                lines = file.readlines()
            for line in lines:
                if 'import org.openqa.selenium' in line:
                    is_selenium = 1
                elif 'import com.microsoft.playwright' in line:
                    is_playwright = 1
                elif 'import org.junit' in line:
                    with_junit = 1
                elif 'import org.testng' in line:
                    with_testng = 1
                elif '@Test' in line:
                    num_test += 1

            if is_selenium == 0 and is_playwright == 0 and num_test >0:
                return  True,[path,with_junit,with_testng,num_test]
            else:
                return False,[]
        except FileNotFoundError:
            print(f"File non trovato: {path}")
        except Exception as e:
            print(f"Errore durante l'apertura del file: {e}")
        return False,[]


    @staticmethod
    def search_other_kind_of_test_java(start,end):
        repos = OtherTestResearch.fetch_java_webrepo()
        path_folder_clone = f"/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/clone"
        for repo in repos[start:end]:
            if repo.name not in OtherTestResearch.black_list:
                repo_name = repo.name
                cloner = Cloner(path_folder_clone)
                cloner.clone_repository(repo_name)
                original_name = repo_name.replace('/', '\\')
                new_name = repo_name.replace('/', '_')
                OtherTestResearch.rename_dir(original_name, new_name)
                cloned_repository = path_folder_clone + "/" + new_name
                # Itera su tutte le directory e file
                df = pd.DataFrame(columns=['path','junit','testng','num of tests'])
                for root, dirs, files in os.walk(cloned_repository):
                    for file in files:
                        if file.endswith(".java"):
                            is_test,data = OtherTestResearch.check_java_file(os.path.join(root, file))
                            if is_test:
                                new_row = pd.DataFrame({'path': [data[0]],'junit':[data[1]],'testng':[data[2]], 'num of tests': [data[3]]})
                                df = pd.concat([df, new_row], ignore_index=True)
                try:
                    df.to_csv(f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/other_test_analysis/java_web_app/'+new_name+'.csv', index=False)
                    print(f'file saved {new_name+".csv"}!')
                except Exception as e:
                    print(f'Error: {e}')
                # clear clone directory
                CommitAnalyzer.clear_directory(path_folder_clone + "/" + new_name)
                CommitAnalyzer.empty_recycle_bin()


    @staticmethod
    def search_other_kind_of_test_jsts(start,end):
        repos = OtherTestResearch.fetch_jsts_repo()
        path_folder_clone = f"/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/clone"
        for repo in repos[start:end]:
            if repo.name not in OtherTestResearch.black_list:
                repo_name = repo.name
                cloner = Cloner(path_folder_clone)
                cloner.clone_repository(repo_name)
                original_name = repo_name.replace('/', '\\')
                new_name = repo_name.replace('/', '_')
                OtherTestResearch.rename_dir(original_name, new_name)
                cloned_repository = path_folder_clone + "/" + new_name
                # Itera su tutte le directory e file
                dependencies = []
                frameworks = []
                df = pd.DataFrame(columns=['path','jest','mocha','jasmine','num of tests'])
                dependency_file_list = JavascriptDataAnalyzer.find_dependency_file(cloned_repository)
                for file in dependency_file_list:
                    dependencies = JavascriptDataAnalyzer.analyze_package_file(file, dependencies)
                    test_framework = JavascriptDataAnalyzer.find_test_dep(dependencies)
                    if test_framework!=0 and test_framework not in frameworks:
                        frameworks.append(test_framework)
                print(f" frameworks: {frameworks}")
                for root, dirs, files in os.walk(cloned_repository):
                    for file in files:
                        if file.endswith(".js") or file.endswith(".ts"):
                            print(f"file : {file}")
                            is_test,data = OtherTestResearch.check_jsts_file(os.path.join(root, file),frameworks)
                            if is_test:
                                new_row = pd.DataFrame({'path': [data[0]],'jest':[data[1]],'mocha':[data[2]],'jasmine':[data[3]] ,'num of tests': [data[4]]})
                                df = pd.concat([df, new_row], ignore_index=True)
                try:
                    df.to_csv(f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/other_test_analysis/js_ts_web_app/'+new_name+'.csv', index=False)
                    print(f'file saved {new_name+".csv"}!')
                except Exception as e:
                    print(f'Error: {e}')
                # clear clone directory
                CommitAnalyzer.clear_directory(path_folder_clone + "/" + new_name)
                CommitAnalyzer.empty_recycle_bin()

    @staticmethod
    def search_other_kind_of_test_python(start,end):
        repos = OtherTestResearch.fetch_py_repo()
        path_folder_clone = f"/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/clone"
        for repo in repos[start:end]:
            if repo.name not in OtherTestResearch.black_list:
                repo_name = repo.name
                cloner = Cloner(path_folder_clone)
                cloner.clone_repository(repo_name)
                original_name = repo_name.replace('/', '\\')
                new_name = repo_name.replace('/', '_')
                OtherTestResearch.rename_dir(original_name, new_name)
                cloned_repository = path_folder_clone + "/" + new_name
                # Itera su tutte le directory e file
                df = pd.DataFrame(columns=['path','pytest','unittest','num of tests'])
                for root, dirs, files in os.walk(cloned_repository):
                    for file in files:
                        if file.endswith(".py"):
                            is_test,data = OtherTestResearch.check_python_file(os.path.join(root, file))
                            if is_test:
                                new_row = pd.DataFrame({'path': [data[0]],'pytest':[data[1]],'unittest':[data[2]], 'num of tests': [data[3]]})
                                df = pd.concat([df, new_row], ignore_index=True)
                try:
                    df.to_csv(f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/other_test_analysis/py_web_app/'+new_name+'.csv', index=False)
                    print(f'file saved {new_name+".csv"}!')
                except Exception as e:
                    print(f'Error: {e}')
                # clear clone directory
                CommitAnalyzer.clear_directory(path_folder_clone + "/" + new_name)
                CommitAnalyzer.empty_recycle_bin()


    @staticmethod
    def check_python_file(path):
        is_selenium = 0
        is_playwright = 0
        is_puppeteer = 0
        with_pytest = 0
        with_unittest = 0
        num_test = 0
        try:
            with open(path, 'r') as file:
                lines = file.readlines()
            for line in lines:
                if 'from selenium' in line:
                    is_selenium = 1
                elif 'from playwright' in line:
                    is_playwright = 1
                elif 'from pyppeteer' in line:
                    is_puppeteer = 1
                elif 'import pytest' in line:
                    with_pytest = 1
                elif 'import unittest' in line:
                    with_unittest = 1
                elif 'from locust' in line:
                    is_locust = 1
                if line.startswith('def test_'):
                    num_test += 1

            if is_selenium == 0 and is_playwright == 0 and is_puppeteer ==0 and num_test>0:
                return True, [path,with_pytest,with_unittest,num_test]
            else:
                return  False,[]
        except FileNotFoundError:
            print(f"File non trovato: {path}")
        except Exception as e:
            print(f"Errore durante l'apertura del file: {e}")
        return False,[]



    @staticmethod
    def get_missed_indexs():
        repos = OtherTestResearch.fetch_py_repo()
        index =1
        for repo in repos:
            repo_name = repo.name
            original_name = repo_name.replace('/', '\\')
            new_name = repo_name.replace('/', '_')
            csv_path = f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/other_test_analysis/py_web_app/'+new_name+'.csv'
            if not os.path.exists(csv_path):
                print(f"repo {repo_name} non processata indice :{index}")
            index+=1

    @staticmethod
    def run_parallel_analysis():
        project_ranges =[
            [45,100],
            [389,400],
            [448,500],
            [500,550],
            [550,585]
        ]
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = [executor.submit(OtherTestResearch.search_other_kind_of_test_python,start, end) for start, end in project_ranges]
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()  # Recupera il risultato del processo
                    print("Analisi completata per un batch.")
                except Exception as exc:
                    print(f"Si è verificato un errore durante l'analisi: {exc}")

if __name__ == "__main__":
    #py_repos = OtherTestResearch.fetch_py_repo()
    #print(len(py_repos))
    OtherTestResearch.run_parallel_analysis()
    #OtherTestResearch.get_missed_indexs()