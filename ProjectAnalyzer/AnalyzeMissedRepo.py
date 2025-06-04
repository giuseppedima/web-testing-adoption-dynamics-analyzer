import csv
import errno
import json
import os
import re
import shutil
import stat
import subprocess
from pathlib import Path

from RepositoryAnalyzer.EncodingDetector import EncodingDetector

from Dataset.Repository import WebRepositoryDAO
from sqlalchemy import or_, and_
from Dataset.DBconnector import Session, engine
from RepositoryAnalyzer.RepositoryCloner import Cloner


class AnalyzeMissedRepo:

    @staticmethod
    def get_missed_repos():

        java_folder = r'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/data/java_test_analysis'
        js_ts_folder = r'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/data/js_ts_test_analysis'
        py_folder = r'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/data/py_test_analysis'
        missed_repo = r'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/data/missed_repo'
        paths = [java_folder, js_ts_folder, py_folder, missed_repo]

        unique_filenames = set()

        # Scorrere i path e salvare i nomi dei file
        for path in paths:
            p = Path(path)
            if p.is_dir():
                # Scorri tutti i file nella directory
                for file in p.iterdir():
                    if file.is_file():
                        if file.name != 'results.csv':
                            unique_filenames.add(file.name)

        # Scorrere il set
        unique_filenames = {filename.replace('.csv', '').replace('_', '/', 1) for filename in unique_filenames}
        print(len(unique_filenames))
        repo_e2e_deps = AnalyzeMissedRepo.get_repo_wid_e2e_deps()
        print(len(repo_e2e_deps))
        print(len(repo_e2e_deps) - len(unique_filenames))
        e2e_repos_names = [repo.name for repo in repo_e2e_deps]
        difference_repo = [repo for repo in repo_e2e_deps if repo.name not in unique_filenames]
        return difference_repo

    @staticmethod
    def get_repo_wid_e2e_deps():
        try:
            session = Session(bind=engine)
            records = session.query(WebRepositoryDAO).filter(
                or_(
                    WebRepositoryDAO.is_cypress_tested_javascript == True,
                    WebRepositoryDAO.is_cypress_tested_typescript == True,
                    WebRepositoryDAO.is_jmeter_tested == True,
                    WebRepositoryDAO.is_locust_tested_java == True,
                    WebRepositoryDAO.is_locust_tested_python == True,
                    WebRepositoryDAO.is_playwright_tested_java == True,
                    WebRepositoryDAO.is_playwright_tested_javascript == True,
                    WebRepositoryDAO.is_playwright_tested_python == True,
                    WebRepositoryDAO.is_playwright_tested_typescript == True,
                    WebRepositoryDAO.is_puppeteer_tested_javascript == True,
                    WebRepositoryDAO.is_puppeteer_tested_python == True,
                    WebRepositoryDAO.is_puppeteer_tested_typescript == True,
                    WebRepositoryDAO.is_selenium_tested_java == True,
                    WebRepositoryDAO.is_selenium_tested_javascript == True,
                    WebRepositoryDAO.is_selenium_tested_python == True,
                    WebRepositoryDAO.is_selenium_tested_typescript == True)
            ).all()
            return records
        except Exception as e:
            print(f'errore : {e}')
    @staticmethod
    def create_reasume_csv_file(data, res_path='/home/sergio/ICST25-E2EMining/missed_repo/result.csv'):
            # Verifica se il file CSV esiste
            file_exists = os.path.isfile(res_path)
            # Apri il file in modalità append
            with open(res_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                # Se il file non esiste, scrivi l'intestazione
                if not file_exists:
                    writer.writerow(
                        [
                            "repository",
                            "selenium_java",
                            "selenium_js",
                            "selenium_ts",
                            "selenium_py",
                            "playwright_java",
                            "playwright_js",
                            "playwright_ts",
                            "playwright_py",
                            "puppeteer_js",
                            "puppeteer_ts",
                            "puppeteer_py",
                            "cypress_js",
                            "cypress_ts",
                            "locust_java",
                            "locust_py",
                            "jmeter",
                            "with_junit",
                            "with_testng",
                            "with_jest",
                            "with_mocha",
                            "with_jasmine",
                            "with_pytest",
                            "with_unittest",
                            "number of test",
                            "number of file"
                        ])
                # Scrivi i dati
                writer.writerow(data)


    @staticmethod
    def calculate_reasume(path):
        # Controlla se il percorso esiste ed è una directory
        if os.path.exists(path) and os.path.isdir(path):
            # Scorre i file e le cartelle nel percorso dato
            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    print(f"Leggendo il file: {file_path}")
                    with open(file_path, mode='r', newline='', encoding='utf-8') as csv_file:
                        reader = csv.reader(csv_file)
                        next(reader)  # Salta la prima riga (l'intestazione)
                        reponame = ""
                        selenium_java=0
                        selenium_js=0
                        selenium_ts=0
                        selenium_py=0
                        playwright_java=0
                        playwright_js=0
                        playwright_ts=0
                        playwright_py=0
                        puppeteer_js=0
                        puppeteer_ts=0
                        puppeteer_py=0
                        cypress_js=0
                        cypress_ts=0
                        locust_java=0
                        locust_py=0
                        jmeter=0
                        with_junit=0
                        with_testng=0
                        with_jest=0
                        with_mocha=0
                        with_jasmine=0
                        with_pytest=0
                        with_unittest=0
                        number_test=0
                        row_count = sum(1 for _ in reader)
                        csv_file.seek(0)
                        reader = csv.reader(csv_file)
                        next(reader)
                        for row in reader:
                            # print(row)
                            # print(row[0])
                            if len(row) != 0:
                                reponame = row[0]
                                selenium_java += int(row[2])
                                selenium_js += int(row[3])
                                selenium_ts += int(row[4])
                                selenium_py += int(row[5])
                                playwright_java += int(row[6])
                                playwright_js += int(row[7])
                                playwright_ts += int(row[8])
                                playwright_py += int(row[9])
                                puppeteer_js += int(row[10])
                                puppeteer_ts += int(row[11])
                                puppeteer_py += int(row[12])
                                cypress_js += int(row[13])
                                cypress_ts += int(row[14])
                                locust_java += int(row[15])
                                locust_py += int(row[16])
                                jmeter += int(row[17])
                                with_junit += int(row[18])
                                with_testng += int(row[19])
                                with_jest += int(row[20])
                                with_mocha += int(row[21])
                                with_jasmine += int(row[22])
                                with_pytest += int(row[23])
                                with_unittest += int(row[24])
                                number_test += int(row[25])

                        AnalyzeMissedRepo.create_reasume_csv_file([
                            os.path.basename(csv_file.name),
                            selenium_java,
                            selenium_js,
                            selenium_ts,
                            selenium_py,
                            playwright_java,
                            playwright_js,
                            playwright_ts,
                            playwright_py,
                            puppeteer_js,
                            puppeteer_ts,
                            puppeteer_py,
                            cypress_js,
                            cypress_ts,
                            locust_java,
                            locust_py,
                            jmeter,
                            with_junit,
                            with_testng,
                            with_jest,
                            with_mocha,
                            with_jasmine,
                            with_pytest,
                            with_unittest,
                            number_test,
                            row_count
                        ])
        else:
            print(f"Il percorso {path} non esiste o non è una directory valida.")





    @staticmethod
    def check_sel_pl_pup_lo(repo, path):
        is_selenium = 0
        is_playwright = 0
        is_puppeteer = 0
        is_locust = 0
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
                return [
                    repo.name,
                    path,
                    0,
                    0,
                    0,
                    is_selenium,
                    0,
                    0,
                    0,
                    is_playwright,
                    0,
                    0,
                    is_puppeteer,
                    0,
                    0,
                    0,
                    is_locust,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    with_pytest,
                    with_unittest,
                    num_test,
                    len(lines)
                ]

        except FileNotFoundError:
            print(f"File non trovato: {path}")
        except Exception as e:
            print(f"Errore durante l'apertura del file: {e}")
        return []

    @staticmethod
    def get_num_test_test(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            test_pattern = re.compile(r"\btest\s*\(\s*['\"]", re.MULTILINE)
            tests = test_pattern.findall(content)

            # Conta il numero di test trovati
            return len(tests)
        except FileNotFoundError:
            print(f"Il file {file_path} non è stato trovato.")
            return 0
        except Exception as e:
            print(f"Si è verificato un errore: {e}")
            return 0

    @staticmethod
    def get_num_test_it(path):
        try:
            with open(path, 'r') as file:
                content = file.read()
                lines = file.readlines()
            test_pattern = re.compile(r"\bit\s*\(", re.MULTILINE)
            # Trova tutte le corrispondenze
            tests = test_pattern.findall(content)
            num_test = len(tests)
            return num_test, len(lines)
        except FileNotFoundError:
            print(f"Il file {path} non è stato trovato.")
            return 0, 0
        except Exception as e:
            print(f"Si è verificato un errore: {e}")
            return 0, 0

    @staticmethod
    def check_javascript_test(repo, path, test_frame):
        is_selenium = 0
        is_playwright = 0
        is_puppeteer = 0
        with_mocha = 0
        with_jest = 0
        with_jasmine = 0
        num_test = 0

        cypress_extensions = ('.cy.js', '.cy.ts', '.cy.jsx', '.cy.tsx')
        if not path.endswith(cypress_extensions):
            if test_frame == 1:
                with_jest = 1
                num_test = AnalyzeMissedRepo.get_num_test_test(path)
            elif test_frame == 2:
                with_mocha = 1
                num_test, num_lines = AnalyzeMissedRepo.get_num_test_it(path)
                if num_test == 0:  # caso suite() al posti di describe()
                    num_test = AnalyzeMissedRepo.get_num_test_test(path)
            elif test_frame == 3:
                with_jasmine = 1
                num_test, num_lines = AnalyzeMissedRepo.get_num_test_it(path)

            try:
                with open(path, 'r') as file:
                    lines = file.readlines()
                for line in lines:
                    if ('selenium-webdriver' in line):
                        is_selenium = 1
                    elif ('@playwright' in line):
                        is_playwright = 1
                        if (num_test == 0):  # caso @playwright/test
                            num_test = AnalyzeMissedRepo.get_num_test_test(path)
                    elif ('puppeteer' in line):
                        is_puppeteer = 1
                        if num_test == 0 and test_frame == 1:  # caso jest-puppeteer
                            num_test, num_lines = AnalyzeMissedRepo.get_num_test_it(path)
                return [
                    repo.name,
                    path,
                    0,
                    is_selenium,
                    0,
                    0,
                    0,
                    is_playwright,
                    0,
                    0,
                    is_puppeteer,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    with_jest,
                    with_mocha,
                    with_jasmine,
                    0,
                    0,
                    num_test,
                    len(lines)
                ]
            except FileNotFoundError:
                print(f"File non trovato: {path}")
            except Exception as e:
                print(f"Errore durante l'apertura del file: {e}")
        else:
            num_test, num_lines = AnalyzeMissedRepo.get_num_test_it(path)
            is_cypress_js = 1

            return [
                repo.name,
                path,
                0,
                is_selenium,
                0,
                0,
                0,
                is_playwright,
                0,
                0,
                is_puppeteer,
                0,
                0,
                is_cypress_js,
                0,
                0,
                0,
                0,
                0,
                0,
                with_jest,
                with_mocha,
                with_jasmine,
                0,
                0,
                num_test,
                num_lines
            ]
        return []

    @staticmethod
    def check_typescript_test(repo, path, test_frame):
        is_selenium = 0
        is_playwright = 0
        is_puppeteer = 0
        with_mocha = 0
        with_jest = 0
        with_jasmine = 0
        num_test = 0
        cypress_extensions = ('.cy.js', '.cy.ts', '.cy.jsx', '.cy.tsx')
        if not path.endswith(cypress_extensions):
            if test_frame == 1:
                with_jest = 1
                num_test = AnalyzeMissedRepo.get_num_test_test(path)
            elif test_frame == 2:
                with_mocha = 1
                num_test, num_lines = AnalyzeMissedRepo.get_num_test_it(path)
                if num_test == 0:  # caso suite() al posti di describe()
                    num_test = AnalyzeMissedRepo.get_num_test_test(path)
            elif test_frame == 3:
                with_jasmine = 1
                num_test, num_lines = AnalyzeMissedRepo.get_num_test_it(path)
            try:
                with open(path, 'r') as file:
                    lines = file.readlines()
                for line in lines:
                    if ('selenium-webdriver' in line):
                        is_selenium = 1
                    elif ('@playwright' in line):
                        is_playwright = 1
                        if (num_test == 0):
                            num_test = AnalyzeMissedRepo.get_num_test_test(path)
                    elif ('puppeteer' in line):
                        is_puppeteer = 1
                        if num_test == 0 and test_frame == 1:
                            num_test, num_lines = AnalyzeMissedRepo.get_num_test_it(path)

                return [
                    repo.name,
                    path,
                    0,
                    0,
                    is_selenium,
                    0,
                    0,
                    0,
                    is_playwright,
                    0,
                    0,
                    is_puppeteer,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    with_jest,
                    with_mocha,
                    with_jasmine,
                    0,
                    0,
                    num_test,
                    len(lines)
                ]
            except FileNotFoundError:
                print(f"File non trovato: {path}")
            except Exception as e:
                print(f"Errore durante l'apertura del file: {e}")
        else:
            num_test, num_lines = AnalyzeMissedRepo.get_num_test_it(path)
            is_cypress = 1

            return [
                repo.name,
                path,
                0,
                0,
                is_selenium,
                0,
                0,
                0,
                is_playwright,
                0,
                0,
                is_puppeteer,
                0,
                0,
                is_cypress,
                0,
                0,
                0,
                0,
                0,
                with_jest,
                with_mocha,
                with_jasmine,
                0,
                0,
                num_test,
                num_lines
            ]

        return []

    @staticmethod
    def check_selenium_playwrite_java_test(repo, path):
        is_selenium = 0
        is_playwright = 0
        with_junit = 0
        with_testng = 0
        num_test = 0
        # Prova a leggere il file
        try:
            with open(path, 'r') as file:
                lines = file.readlines()
            for line in lines:
                if 'import org.openqa.selenium' in line:
                    is_selenium = 1
                    print(f'selenium : {line}')
                elif 'import com.microsoft.playwright' in line:
                    is_playwright = 1
                    print(f'playwright : {line}')
                elif 'import org.junit' in line:
                    with_junit = 1
                elif 'import org.testng' in line:
                    with_testng = 1
                elif '@Test' in line:
                    num_test += 1
            # return [repo.name,path,0,0,is_selenium,is_playwright,with_junit,with_testng,num_test,len(lines)]
            return [
                repo.name,
                path,
                is_selenium,
                0,
                0,
                0,
                is_playwright,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                with_junit,
                with_testng,
                0,
                0,
                0,
                0,
                0,
                num_test,
                len(lines)
            ]
        except FileNotFoundError:
            print(f"File non trovato: {path}")
        except Exception as e:
            print(f"Errore durante l'apertura del file: {e}")
        return []

    @staticmethod
    def write_resrow_csv_file(filename, data, res_path='/home/sergio/ICST25-E2EMining/missed_repo/'):
        file_exists = os.path.isfile(res_path + filename)
        headers = [
            "repository",
            "file_path",
            "selenium_java",
            "selenium_js",
            "selenium_ts",
            "selenium_py",
            "playwright_java",
            "playwright_js",
            "playwright_ts",
            "playwright_py",
            "puppeteer_js",
            "puppeteer_ts",
            "puppeteer_py",
            "cypress_js",
            "cypress_ts",
            "locust_java",
            "locust_py",
            "jmeter",
            "with_junit",
            "with_testng",
            "with_jest",
            "with_mocha",
            "with_jasmine",
            "with_pytest",
            "with_unittest",
            "number of test",
            "number of file"
        ]
        with open(res_path + filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(headers)
            writer.writerow(data)
    @staticmethod
    def read_missed_repo():
        res = []
        # Aprire il file in modalità lettura
        with open('/home/sergio/Scaricati/icst25_not_examined_repo.txt', 'r') as file:
            # Leggere il file riga per riga
            for riga in file:
                # Stampare la riga (o fare altre operazioni)
                res.append(riga.strip())  # .strip() rimuove spazi o caratteri di nuova linea extra
        return res

    @staticmethod
    def getRepoByName(name):
        try:
            # Tenta di connetterti al database
            session = Session(bind=engine)
            print("Connection successful!")

            # Esegui il fetch dei record filtrati
            query = session.query(WebRepositoryDAO).filter(
                and_(
                    WebRepositoryDAO.name == name,  # Corrected filter condition
                    or_(
                        WebRepositoryDAO.is_selenium_tested_java == True,
                        WebRepositoryDAO.is_selenium_tested_python == True,
                        WebRepositoryDAO.is_selenium_tested_javascript == True,
                        WebRepositoryDAO.is_selenium_tested_typescript == True,
                        WebRepositoryDAO.is_puppeteer_tested_python == True,
                        WebRepositoryDAO.is_puppeteer_tested_javascript == True,
                        WebRepositoryDAO.is_puppeteer_tested_typescript == True,
                        WebRepositoryDAO.is_playwright_tested_java == True,
                        WebRepositoryDAO.is_playwright_tested_python == True,
                        WebRepositoryDAO.is_playwright_tested_javascript == True,
                        WebRepositoryDAO.is_playwright_tested_typescript == True,
                        WebRepositoryDAO.is_cypress_tested_javascript == True,
                        WebRepositoryDAO.is_cypress_tested_typescript == True,
                        WebRepositoryDAO.is_locust_tested_java == True,
                        WebRepositoryDAO.is_locust_tested_python == True,
                        WebRepositoryDAO.is_jmeter_tested == True
                    )
                )
            )
            records = query.all()
            return records[0]

        except Exception as e:
            print(f"Error connecting to the database: {e}")

        finally:
            session.close()  # Ensure session is closed

    @staticmethod
    def rename_dir(old_name, new_name):
        # Assicurati che il nuovo percorso non esista già
        if not os.path.exists("/home/sergio/ICST25-E2EMining/clone/" + new_name):
            # Rinomina la directory
            os.rename("/home/sergio/ICST25-E2EMining/clone/" + old_name,
                      "/home/sergio/ICST25-E2EMining/clone/" + new_name)
            print(f"La directory è stata rinominata")
        else:
            print(f"Errore: La directory di destinazione esiste già.")

    @staticmethod
    def clear_directory(directory_path):
        if not os.path.exists(directory_path):
            print(f"Directory {directory_path} does not exist, nothing to clear.")
            return

        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path, ignore_errors=False, onerror=AnalyzeMissedRepo.handle_remove_readonly)
                else:
                    os.remove(item_path)
            except Exception as e:
                print(f"Error removing {item_path}: {e}")
        print('Folder succesfully cleaned!')

    @staticmethod
    def handle_remove_readonly(func, path, exc):
        excvalue = exc[1]
        if func in (os.rmdir, os.remove, os.unlink) and excvalue.errno == errno.EACCES:
            os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
            func(path)
        else:
            raise

    @staticmethod
    def empty_recycle_bin():
        try:
            # Chiama l'API di Windows per svuotare il cestino
            # ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 1)
            AnalyzeMissedRepo.clear_directory("/home/sergio/.local/share/Trash/files")
            print("Cestino svuotato con successo.")
        except Exception as e:
            print(f"Errore durante lo svuotamento del cestino: {e}")
    @staticmethod
    def add_dependency_in_list(dependency, dependency_list):
        for inserted_dependency in dependency_list:
            if dependency[0] == inserted_dependency[0]:
                # Se il primo elemento di dependency è uguale al primo elemento di un'altra dipendenza,
                # non aggiungere nulla e interrompi il ciclo
                break
        else:
            # Se il ciclo è terminato senza interruzioni, aggiungi la dipendenza alla lista
            dependency_list.append(dependency)

    @staticmethod
    def get_package_name(package_name):
        # Rimuove il carattere '@' e prende solo la parte del nome del pacchetto prima del carattere '/'
        if package_name.startswith('@types/'):
            # Mantieni la parte "@types/" per i pacchetti che iniziano con "@types/"
            cleaned_package_name = package_name
        else:
            # Controlla se '@' è presente nel nome del pacchetto
            if '@' in package_name:
                # Rimuovi la parte "@..." e prendi ciò che c'è dopo
                cleaned_package_name = package_name.split('@', 1)[1]
                cleaned_package_name = cleaned_package_name.split('/', 1)[0]
            else:
                # Se '@' non è presente, il nome del pacchetto non è modificato
                cleaned_package_name = package_name

        return cleaned_package_name

    @staticmethod
    def analyze_package_file(dependency_file, dependency_list):  # fai bene questa cosa
        try:
            encoding = EncodingDetector.detect_encoding(dependency_file)
            with open(dependency_file, 'r', encoding=encoding,errors='replace') as file:
                lockfile = json.load(file)
        except UnicodeDecodeError as e:
            print(f"Errore di codifica durante la lettura del file: {e}")
            print(e)
            return dependency_list
        except json.JSONDecodeError as e:
            print(f"Errore nel parsing del file JSON: {e}")
            print(e)
            return dependency_list

        def process_dependencies(obj):
            if isinstance(obj, dict):
                if 'dependencies' in obj and isinstance(obj['dependencies'], dict):
                    for package_name, version in obj['dependencies'].items():
                        AnalyzeMissedRepo.add_dependency_in_list((AnalyzeMissedRepo.get_package_name(package_name), version), dependency_list)
                if 'devDependencies' in obj and isinstance(obj['devDependencies'], dict):
                    for package_name, version in obj['devDependencies'].items():
                        AnalyzeMissedRepo.add_dependency_in_list((AnalyzeMissedRepo.get_package_name(package_name), version), dependency_list)
                for value in obj.values():
                    process_dependencies(value)
            elif isinstance(obj, list):
                for item in obj:
                    process_dependencies(item)

        process_dependencies(lockfile)

        #print(dependency_list)
        return dependency_list

    @staticmethod
    def find_dependency_file(repository):
        dependency_files_list = []
        print("vedo questo ->" + str(repository))
        for root, dirs, files in os.walk(repository):
            if 'package.json' in files:
                json_file = os.path.join(root, 'package.json')
                dependency_files_list.append(json_file)
                # analyzer = DependencyFinderInterface.factory_analyzer(json_file)
                # dependencies = analyzer.find_dependency(json_file, dependencies)
            if 'package-lock.json' in files:
                json_file = os.path.join(root, 'package-lock.json')
                dependency_files_list.append(json_file)
                # analyzer = DependencyFinderInterface.factory_analyzer(json_file)
                # dependencies = analyzer.find_dependency(json_file, dependencies)
        return dependency_files_list

    @staticmethod
    def find_test_dep(repository_dependencies):
        for dependency in repository_dependencies:
            if dependency[0] == "@types/jest" or dependency[0] == 'jest':
                return 1
            elif dependency[0] == "@types/mocha" or dependency[0] == 'mocha':
                return 2
            elif dependency[0] == "@types/jasmine" or dependency[0] == 'jasmine':
                return  3
        return 0

    @staticmethod
    def check_test(repo):
        is_selenium_tested_java = repo.is_selenium_tested_java
        is_selenium_tested_py = repo.is_selenium_tested_python
        is_selenium_tested_js = repo.is_selenium_tested_javascript
        is_selenium_tested_ts = repo.is_selenium_tested_typescript
        is_puppeteer_tested_py = repo.is_puppeteer_tested_python
        is_puppeteer_tested_js = repo.is_puppeteer_tested_javascript
        is_puppeteer_tested_ts = repo.is_puppeteer_tested_typescript
        is_playwright_tested_java = repo.is_playwright_tested_java
        is_playwright_tested_py = repo.is_playwright_tested_python
        is_playwright_tested_js = repo.is_playwright_tested_javascript
        is_playwright_tested_ts = repo.is_playwright_tested_typescript
        is_cypress_tested_js = repo.is_cypress_tested_javascript
        is_cypress_tested_ts = repo.is_cypress_tested_typescript
        is_locust_tested_java = repo.is_locust_tested_java
        is_locust_tested_py = repo.is_locust_tested_python
        is_jmeter_tested = repo.is_jmeter_tested
        path_folder_clone = f"/home/sergio/ICST25-E2EMining/clone"
        cloner = Cloner(path_folder_clone)
        cloner.clone_repository(repo.name)
        # Rinomina la directory
        original_name = repo.name.replace('/', '\\')
        new_name = repo.name.replace('/', '_')
        # print(f"Rinominazione dir: {original_name} -> {new_name}")
        AnalyzeMissedRepo.rename_dir(original_name, new_name)
        tests_path = repo.test_path.split(";")
        cloned_repository = path_folder_clone + "/" + new_name

        dependency_file_list = AnalyzeMissedRepo.find_dependency_file(cloned_repository)
        # Initialize 'dependencies' before using it in the loop
        dependencies = []  # or {} if dependencies is expected to be a dictionary
        for file in dependency_file_list:
            # print("sto analizzando: {file}")
            dependencies = AnalyzeMissedRepo.analyze_package_file(file, dependencies)
            test_framework = AnalyzeMissedRepo.find_test_dep(dependencies)
        for test_path in tests_path[:-1]:
            print(f"test_path: {test_path}")
            # Sostituisci il percorso Windows con il percorso Unix-like
            if (test_path.strip().startswith('C:\\rep\\')):
                file_path = test_path.replace('C:\\rep\\', '/home/sergio/ICST25-E2EMining/clone/')
            elif (test_path.strip().startswith('C:\\re\\')):
                file_path = test_path.replace('C:\\re\\', '/home/sergio/ICST25-E2EMining/clone/')
            else:
                print(f"altro caso {test_path}")

            # Rimpiazza il nome del repository nel percorso e pulisci eventuali spazi
            file_path = file_path.replace(original_name, new_name, 1).strip()

            # Dividi il percorso in parti per sostituire correttamente i backslash
            initial_index = file_path.index(new_name)
            initial_part = file_path[:initial_index + len(new_name)]
            remaining_part = file_path[len(initial_part):].replace('\\', '/').strip()

            # Costruisci il nuovo percorso completo
            new_path = (initial_part + remaining_part).strip()

            # Ottieni l'estensione del file
            estensione = os.path.splitext(new_path)[1]
            print(f'file : {new_path} con estensione : {estensione}')
            if os.path.exists(new_path):
                if estensione == ".jmx": #jmeter
                    data = [repo.name,new_path,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        1,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0
                    ]
                    AnalyzeMissedRepo.write_resrow_csv_file(new_name+".csv",data)
                elif estensione == ".py":
                    data = AnalyzeMissedRepo.check_sel_pl_pup_lo(repo,new_path)
                    AnalyzeMissedRepo.write_resrow_csv_file(new_name+".csv",data)
                elif estensione == ".ts":
                    data = AnalyzeMissedRepo.check_typescript_test(repo, new_path, test_framework)
                    AnalyzeMissedRepo.write_resrow_csv_file(new_name + ".csv", data)
                elif estensione == ".js":
                    data = AnalyzeMissedRepo.check_javascript_test(repo, new_path, test_framework)
                    AnalyzeMissedRepo.write_resrow_csv_file(new_name+".csv",data)
                elif estensione == ".java":
                    data = AnalyzeMissedRepo.check_selenium_playwrite_java_test(repo,new_path)
                    AnalyzeMissedRepo.write_resrow_csv_file(new_name+".csv",data)
            else:
                print(f"{new_path} file non trovato!")

        AnalyzeMissedRepo.clear_directory(f"/home/sergio/ICST25-E2EMining/clone")
        AnalyzeMissedRepo.empty_recycle_bin()





repos = AnalyzeMissedRepo.get_missed_repos()
print(len(repos))
#repos = AnalyzeMissedRepo.read_missed_repo()
#for name in repos[85:86]:
    #repo = AnalyzeMissedRepo.getRepoByName(name)
for repo in repos[2:3]:
    print(repo.name)
    AnalyzeMissedRepo.check_test(repo)


#AnalyzeMissedRepo.calculate_reasume(r'/home/sergio/ICST25-E2EMining/missed_repo/')


