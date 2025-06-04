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
from Dataset.Repository import WebRepositoryDAO
from  Dataset.Repository import Repository
from sqlalchemy import or_, and_
from RepositoryAnalyzer.RepositoryCloner import Cloner

class PythonDataAnalyzer:
    @staticmethod
    def fetch_py_repo():
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
                        WebRepositoryDAO.is_selenium_tested_python == True,
                        #WebRepositoryDAO.is_selenium_tested_javascript == True,
                        #WebRepositoryDAO.is_selenium_tested_typescript == True,
                        WebRepositoryDAO.is_puppeteer_tested_python == True,
                        #WebRepositoryDAO.is_puppeteer_tested_javascript == True,
                        #WebRepositoryDAO.is_puppeteer_tested_typescript == True,
                        # WebRepositoryDAO.is_playwright_tested_java == True,
                        WebRepositoryDAO.is_playwright_tested_python == True,
                        #WebRepositoryDAO.is_playwright_tested_javascript == True,
                        #WebRepositoryDAO.is_playwright_tested_typescript == True,
                        #WebRepositoryDAO.is_cypress_tested_javascript == True,
                        #WebRepositoryDAO.is_cypress_tested_typescript == True,
                        # WebRepositoryDAO.is_locust_tested_java == True,
                        WebRepositoryDAO.is_locust_tested_python == True,
                        WebRepositoryDAO.is_jmeter_tested == True
                    ),
                    repository_alias.languages.like('%Python%')
                    #WebRepositoryDAO.name == 'verdaccio/verdaccio'
                    # Filter based on the languages column in RepositoryDAO
                )
            )
            records = query.all()
            return records

        except Exception as e:
            print(f"Error connecting to the database: {e}")

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
        if not os.path.exists("/home/sergio/ICST25-E2EMining/clone/" + new_name):
            # Rinomina la directory
            os.rename("/home/sergio/ICST25-E2EMining/clone/" + old_name,
                      "/home/sergio/ICST25-E2EMining/clone/" + new_name)
            print(f"La directory è stata rinominata")
        else:
            print(f"Errore: La directory di destinazione esiste già.")


    @staticmethod
    def find_dependency_file(self, repository):
        dependency_files_list = []
        print("vedo questo ->" + str(repository))
        for root, dirs, files in os.walk(repository):
            for file in files:
                if file.endswith('.txt') and file.startswith('requirements'):
                    txtfile = os.path.join(root, file)
                    dependency_files_list.append(txtfile)
                    # analyzer = DependencyFinderInterface.factory_analyzer(txtfile)
                    # dependencies = analyzer.find_dependency(txtfile, dependencies)
            # if 'requirements.txt' in files:
            #    txtfile = os.path.join(root, 'requirements.txt')
            #    analyzer = DependencyFinderInterface.factory_analyzer(txtfile)
            #    dependencies = analyzer.find_dependency(txtfile, dependencies)
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
    def analyze_package_file(self, dependency_file, dependency_list):
        print("reading... " + dependency_file)
        encoding = EncodingDetector.detect_encoding(dependency_file)
        with open(dependency_file, 'r', encoding=encoding) as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):  # Ignora commenti e linee vuote
                    if '==' in line:
                        dependency, version = line.split('==', 1)
                    elif '>=' in line:
                        dependency, version = line.split('>=', 1)
                    elif '<=' in line:
                        dependency, version = line.split('<=', 1)
                    else:
                        dependency = line
                        version = ''  # Assegna una stringa vuota alla versione
                    self.add_dependency_in_list((dependency.strip(), version.strip()), dependency_list)
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
                    shutil.rmtree(item_path, ignore_errors=False, onerror=PythonDataAnalyzer.handle_remove_readonly)
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
            PythonDataAnalyzer.clear_directory("/home/sergio/.local/share/Trash/files")
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

    def create_test_res_to_csv(data, filename, res_path='/home/sergio/ICST25-E2EMining/py_test_analysis/'):
        # Verifica se il file CSV esiste
        file_exists = os.path.isfile(res_path+filename)
        # Apri il file in modalità append
        with open(res_path+filename, mode='a', newline='') as file:
            writer = csv.writer(file)

            # Se il file non esiste, scrivi l'intestazione
            if not file_exists:
                writer.writerow(['Repository',
                                 'File Path',
                                 'Is JMeter',
                                 'Is Locust',
                                 'Is Selenium',
                                 'Is Playwright',
                                 'Is Puppeteer',
                                 'With Pytest',
                                 'With Unnitest',
                                 'Number of @Test',
                                 'Number of Lines'])

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
    def check_sel_pl_pup_lo(repo,path):
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
                    with_pytest =1
                elif 'import unittest' in line:
                    with_unittest =1
                elif 'from locust' in line:
                    is_locust = 1
                if line.startswith('def test_'):
                    num_test += 1
            return [repo.name,
                    path,
                    0,
                    is_locust,
                    is_selenium,
                    is_playwright,
                    is_puppeteer,
                    with_pytest,
                    with_unittest,
                    num_test,
                    len(lines)]
        except FileNotFoundError:
            print(f"File non trovato: {path}")
        except Exception as e:
            print(f"Errore durante l'apertura del file: {e}")
        return  []


    @staticmethod
    def check_test_py(records):
        for repository_to_analyze in records:
            dependency_file_list = []
            dependencies = []
            PythonDataAnalyzer.enable_git_long_paths()
            path_folder_clone = f"/home/sergio/ICST25-E2EMining/clone"
            cloner = Cloner(path_folder_clone)
            cloner.clone_repository(repository_to_analyze.name)
            # Rinomina la directory
            original_name = repository_to_analyze.name.replace('/', '\\')
            new_name = repository_to_analyze.name.replace('/', '_')
            # print(f"Rinominazione dir: {original_name} -> {new_name}")
            PythonDataAnalyzer.rename_dir(original_name, new_name)
            tests_path = repository_to_analyze.test_path.split(";")
            for test_path in tests_path[:-1]:
                print(f"test_path: {test_path}")
                number_jmeter_test = 0
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
                        PythonDataAnalyzer.create_test_res_to_csv(
                            [repository_to_analyze.name, new_path,1,0,0,0,0,0,0,0,PythonDataAnalyzer.get_numlines_byfile(new_path)],
                            new_name + ".csv")
                    elif (estensione == ".py"):
                        data = PythonDataAnalyzer.check_sel_pl_pup_lo(repository_to_analyze,new_path)
                        PythonDataAnalyzer.create_test_res_to_csv(data, new_name+".csv")
                else:
                    print("file non presente!")


            PythonDataAnalyzer.clear_directory(f"/home/sergio/ICST25-E2EMining/clone")
            PythonDataAnalyzer.empty_recycle_bin()


records = PythonDataAnalyzer.fetch_py_repo()
print(len(records))
#obj = records[660:]
#for reco in obj:
#    print(reco.name)
PythonDataAnalyzer.check_test_py(records)
