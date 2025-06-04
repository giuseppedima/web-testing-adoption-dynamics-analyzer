import csv
import errno
import os
import shutil
import stat
import json
import re
import subprocess
from pathlib import Path
from RepositoryAnalyzer.EncodingDetector import EncodingDetector

from sqlalchemy.orm import aliased

from Dataset.DBconnector import Session, engine
from  Dataset.Repository import Repository
from sqlalchemy import or_, and_

from RepositoryAnalyzer.Analyzer import JavaScriptDependencyFileFinder
from RepositoryAnalyzer.AnalyzerInterface import DependencyFileFinderInterface
from RepositoryAnalyzer.RepositoryCloner import Cloner

class JavascriptDataAnalyzer:
    '''
    @staticmethod
    def fetch_jsts_repo():
        try:
            # Tenta di connetterti al database
            session = Session(bind=engine)
            print("Connection successful!")
            # Esegui il fetch di tutti i record
            # records = session.query(WebRepositoryDAO).all()
            # Stampa i record
            repository_alias = aliased(Repository)
            query = session.query(WebRepositoryDAO).join(
                repository_alias, WebRepositoryDAO.IDrepository == repository_alias.ID
            ).filter(
                and_(
                    #or_(
                    #    WebRepositoryDAO.is_web_javascript == True,
                    #    WebRepositoryDAO.is_web_typescript == True
                    #),
                    or_(
                        # WebRepositoryDAO.is_selenium_tested_java == True,
                        # WebRepositoryDAO.is_selenium_tested_python == True,
                        WebRepositoryDAO.is_selenium_tested_javascript == True,
                        WebRepositoryDAO.is_selenium_tested_typescript == True,
                        # WebRepositoryDAO.is_puppeteer_tested_python == True,
                        WebRepositoryDAO.is_puppeteer_tested_javascript == True,
                        WebRepositoryDAO.is_puppeteer_tested_typescript == True,
                        # WebRepositoryDAO.is_playwright_tested_java == True,
                        # WebRepositoryDAO.is_playwright_tested_python == True,
                        WebRepositoryDAO.is_playwright_tested_javascript == True,
                        WebRepositoryDAO.is_playwright_tested_typescript == True,
                        WebRepositoryDAO.is_cypress_tested_javascript == True,
                        WebRepositoryDAO.is_cypress_tested_typescript == True,
                        # WebRepositoryDAO.is_locust_tested_java == True,
                        # WebRepositoryDAO.is_locust_tested_python == True,
                        WebRepositoryDAO.is_jmeter_tested == True
                    ),
                    repository_alias.languages.like('%JavaScript%')
                    #WebRepositoryDAO.name == 'verdaccio/verdaccio'
                    # Filter based on the languages column in RepositoryDAO
                )
            )
            records = query.all()
            return records

        except Exception as e:
            print(f"Error connecting to the database: {e}")
    '''

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
    def rename_dir(old_name, new_name):
        # Assicurati che il nuovo percorso non esista già
        if not os.path.exists("../clone/" + new_name):
            # Rinomina la directory
            os.rename("../clone/" + old_name,
                      "../clone/" + new_name)
            print(f"The directory has been renamed")
        else:
            print(f"Error: The directory already exists!.")


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
                        JavascriptDataAnalyzer.add_dependency_in_list((JavascriptDataAnalyzer.get_package_name(package_name), version), dependency_list)
                if 'devDependencies' in obj and isinstance(obj['devDependencies'], dict):
                    for package_name, version in obj['devDependencies'].items():
                        JavascriptDataAnalyzer.add_dependency_in_list((JavascriptDataAnalyzer.get_package_name(package_name), version), dependency_list)
                for value in obj.values():
                    process_dependencies(value)
            elif isinstance(obj, list):
                for item in obj:
                    process_dependencies(item)

        process_dependencies(lockfile)

        #print(dependency_list)
        return dependency_list

    @staticmethod
    def handle_remove_readonly(func, path, exc):
        excvalue = exc[1]
        if func in (os.rmdir, os.remove, os.unlink) and excvalue.errno == errno.EACCES:
            os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
            func(path)
        else:
            raise

    @staticmethod
    def clear_directory(directory_path):
        if not os.path.exists(directory_path):
            print(f"Directory {directory_path} does not exist, nothing to clear.")
            return

        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path, ignore_errors=False, onerror=JavascriptDataAnalyzer.handle_remove_readonly)
                else:
                    os.remove(item_path)
            except Exception as e:
                print(f"Error removing {item_path}: {e}")
        print('Folder succesfully cleaned!')

    @staticmethod
    def empty_recycle_bin():
        try:
            # Chiama l'API di Windows per svuotare il cestino
            # ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 1)
            JavascriptDataAnalyzer.clear_directory("/home/sergio/.local/share/Trash/files")
            print("Cestino svuotato con successo.")
        except Exception as e:
            print(f"Errore durante lo svuotamento del cestino: {e}")

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

    def create_test_res_to_csv(data, filename, res_path='/home/sergio/ICST25-E2EMining/js_ts_test_analysis/'):
        # Verifica se il file CSV esiste
        file_exists = os.path.isfile(res_path+filename)
        # Apri il file in modalità append
        with open(res_path+filename, mode='a', newline='') as file:
            writer = csv.writer(file)

            # Se il file non esiste, scrivi l'intestazione
            if not file_exists:
                writer.writerow(['Repository', 'File Path', 'Is JMeter','Is Locust', 'Is Selenium JS', 'Is Selenium TS','Is Playwright JS', 'Is Playwright TS ','Is Puppeteer JS','Is Puppeteer TS','Is Cypress JS','Is Cypress TS','With Jest', 'With Mocha','With Jasmine',
                                 'Number of @Test', 'Number of Lines'])

            # Scrivi i dati
            writer.writerow(data)
    @staticmethod
    def get_numlines_byfile(path):
        try:
            with open(path, 'r') as file:
                lines = file.readlines()
            return len(lines)
        except FileNotFoundError:
            print(f"File non trovato: {path}")
        except Exception as e:
            print(f"Errore durante l'apertura del file: {e}")
        return 0


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
            return  num_test,len(lines)
        except FileNotFoundError:
            print(f"Il file {path} non è stato trovato.")
            return 0,0
        except Exception as e:
            print(f"Si è verificato un errore: {e}")
            return 0,0


    @staticmethod
    def check_javascript_test(repo,path,test_frame):
        is_selenium  = 0
        is_playwright = 0
        is_puppeteer = 0
        with_mocha= 0
        with_jest =0
        with_jasmine= 0
        num_test = 0

        cypress_extensions = ('.cy.js', '.cy.ts', '.cy.jsx', '.cy.tsx')
        if not path.endswith(cypress_extensions):
            if test_frame == 1:
                with_jest = 1
                num_test = JavascriptDataAnalyzer.get_num_test_test(path)
            elif test_frame == 2:
                with_mocha =1
                num_test,num_lines = JavascriptDataAnalyzer.get_num_test_it(path)
                if num_test == 0:  #caso suite() al posti di describe()
                    num_test = JavascriptDataAnalyzer.get_num_test_test(path)
            elif test_frame == 3:
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
                        if num_test == 0 and test_frame == 1: #caso jest-puppeteer
                            num_test,num_lines = JavascriptDataAnalyzer.get_num_test_it(path)
                return [repo.name,path,0,0,is_selenium,0,is_playwright,0,is_puppeteer,0,0,0,with_jest,with_mocha,with_jasmine,num_test,len(lines)]
            except FileNotFoundError:
                print(f"File non trovato: {path}")
            except Exception as e:
                print(f"Errore durante l'apertura del file: {e}")
        else:
            num_test,num_lines = JavascriptDataAnalyzer.get_num_test_it(path)
            is_cypress_js= 1
            return [repo.name, path, 0, 0, is_selenium, 0, is_playwright, 0, is_puppeteer, 0, is_cypress_js, 0, with_jest,
                        with_mocha, with_jasmine, num_test, num_lines]
        return []


    @staticmethod
    def check_typescript_test(repo,path,test_frame):
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
                num_test = JavascriptDataAnalyzer.get_num_test_test(path)
            elif test_frame == 2:
                with_mocha = 1
                num_test, num_lines = JavascriptDataAnalyzer.get_num_test_it(path)
                if num_test == 0:  #caso suite() al posti di describe()
                    num_test = JavascriptDataAnalyzer.get_num_test_test(path)
            elif test_frame == 3:
                with_jasmine = 1
                num_test, num_lines = JavascriptDataAnalyzer.get_num_test_it(path)
            try:
                with open(path, 'r') as file:
                    lines = file.readlines()
                for line in lines:
                    if ('selenium-webdriver' in line):
                        is_selenium = 1
                    elif ('@playwright' in line):
                        is_playwright = 1
                        if (num_test == 0):
                            num_test = JavascriptDataAnalyzer.get_num_test_test(path)
                    elif ('puppeteer' in line):
                        is_puppeteer = 1
                        if num_test == 0 and test_frame == 1:
                            num_test, num_lines = JavascriptDataAnalyzer.get_num_test_it(path)
                return [repo.name, path, 0, 0, 0, is_selenium,0, is_playwright,0, is_puppeteer, 0, 0, with_jest, with_mocha, with_jasmine, num_test, len(lines)]
            except FileNotFoundError:
                print(f"File non trovato: {path}")
            except Exception as e:
                print(f"Errore durante l'apertura del file: {e}")
        else:
            num_test, num_lines = JavascriptDataAnalyzer.get_num_test_it(path)
            is_cypress = 1
            return [repo.name, path, 0, 0, 0, is_selenium,0, is_playwright, 0, is_puppeteer, 0, is_cypress, with_jest,with_mocha, with_jasmine, num_test, num_lines]
        return []
    @staticmethod
    def check_test_js_ts(records):
        for repository_to_analyze in records:
            dependency_file_list = []
            dependencies = []
            JavascriptDataAnalyzer.enable_git_long_paths()
            path_folder_clone = f"/home/sergio/ICST25-E2EMining/clone"
            cloner = Cloner(path_folder_clone)
            cloner.clone_repository(repository_to_analyze.name)
            # Rinomina la directory
            original_name = repository_to_analyze.name.replace('/', '\\')
            new_name = repository_to_analyze.name.replace('/', '_')
            # print(f"Rinominazione dir: {original_name} -> {new_name}")
            JavascriptDataAnalyzer.rename_dir(original_name, new_name)
            cloned_repository = path_folder_clone + "/" + new_name
            dependency_file_list = JavascriptDataAnalyzer.find_dependency_file(cloned_repository)
            #print(dependency_file_list)
            for file in dependency_file_list:
                #print("sto analizzando: {file}")
                dependencies = JavascriptDataAnalyzer.analyze_package_file(file, dependencies)
                test_framework = JavascriptDataAnalyzer.find_test_dep(dependencies)
            # 1 jest 2 mocha 3 jasmine

            tests_path = repository_to_analyze.test_path.split(";")
            for test_path in tests_path[:-1]:
                print(f"test_path: {test_path}")
                number_jmeter_test = 0
                number_locust_test = 0

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

                # print(f"file : {new_path} con estensione {estensione}")
                if os.path.exists(new_path):
                    if (estensione == ".jmx"): #jmeter
                        number_jmeter_test += 1
                        JavascriptDataAnalyzer.create_test_res_to_csv(
                            [repository_to_analyze.name, new_path, 1, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, JavascriptDataAnalyzer.get_numlines_byfile(new_path)],
                            new_name + ".csv")
                    elif (estensione == ".py"): #locust
                        number_locust_test += 1
                        JavascriptDataAnalyzer.create_test_res_to_csv(
                            [repository_to_analyze.name, new_path, 0, 1, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, JavascriptDataAnalyzer.get_numlines_byfile(new_path)],
                            new_name + ".csv")
                    elif (estensione == ".js"): #selenium,playright, puppeteer per javascript
                        data = JavascriptDataAnalyzer.check_javascript_test(repository_to_analyze, new_path,test_framework)
                        JavascriptDataAnalyzer.create_test_res_to_csv(data, new_name + ".csv")
                    elif (estensione == ".ts"): #selenium,playright, puppeteer per typescript
                        data = JavascriptDataAnalyzer.check_typescript_test(repository_to_analyze,new_path,test_framework)
                        JavascriptDataAnalyzer.create_test_res_to_csv(data, new_name+".csv")

                else:
                    print("file non presente!")

            JavascriptDataAnalyzer.clear_directory(f"/home/sergio/ICST25-E2EMining/clone")
            JavascriptDataAnalyzer.empty_recycle_bin()

if __name__ == "__main__":
    print("hi!")