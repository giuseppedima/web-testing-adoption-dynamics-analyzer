import csv
import errno
import os
import shutil
import stat
import subprocess
from pathlib import Path
from Dataset.DBconnector import Session, engine
from Dataset.Repository import WebRepositoryDAO
from sqlalchemy import or_, and_
from RepositoryAnalyzer.RepositoryCloner import Cloner


class FetchDataUtils:

    @staticmethod
    def run_radon(command):
        """Esegue un comando Radon e restituisce l'output."""
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout

    @staticmethod
    def analyze_radon_project(project_dir, output_dir, project_name):
        """Esegue l'analisi Radon sul progetto."""
        if not os.path.exists(project_dir):
            # os.makedirs(output_dir)
            print('progetto non esiste')
        else:
            print('progetto trovato')

        # Complessità Ciclomatica (CC)
        print("Analisi della Complessità Ciclomatica (CC):")
        print(f"radon cc {project_dir} -s")
        cc_output = FetchDataUtils.run_radon(f"radon cc {project_dir} -s")

        # Indice di Manutenibilità (MI)
        print("Analisi dell'Indice di Manutenibilità (MI):")
        mi_output = FetchDataUtils.run_radon(f"radon mi {project_dir}")

        # Metriche Grezze (Raw Metrics)
        print("Analisi delle Metriche Grezze (Raw Metrics):")
        raw_output = FetchDataUtils.run_radon(f"radon raw {project_dir}")

        output_path_cc = os.path.join(output_dir, f"{project_name}-cc.txt")
        output_path_mi = os.path.join(output_dir, f"{project_name}-mi.txt")
        output_path_raw = os.path.join(output_dir, f"{project_name}-raw.txt")

        # Salva i risultati su files
        with open(output_path_cc, "w") as file:
            file.write(cc_output)
        with open(output_path_mi, "w") as file:
            file.write(mi_output)
        with open(output_path_raw, "w") as file:
            file.write(raw_output)

        print(f"Risultati salvati in {output_dir}")

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
            return records

        except Exception as e:
            print(f"Error connecting to the database: {e}")

        finally:
            session.close()  # Ensure session is closed

    @staticmethod
    def fetch_webrepo():
        try:
            # Tenta di connetterti al database
            session = Session(bind=engine)
            print("Connection successful!")
            # Esegui il fetch di tutti i record
            # records = session.query(WebRepositoryDAO).all()
            # Stampa i record
            query = session.query(WebRepositoryDAO).filter(
                and_(
                    WebRepositoryDAO.is_web_python == True,
                    #   or_(
                    #     WebRepositoryDAO.is_web_javascript == True,
                    #     WebRepositoryDAO.is_web_typescript == True
                    #   ),
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
                and_(
                    WebRepositoryDAO.is_web_java == True,
                    #   or_(
                    #     WebRepositoryDAO.is_web_javascript == True,
                    #     WebRepositoryDAO.is_web_typescript == True
                    #   ),
                    or_(
                        WebRepositoryDAO.is_selenium_tested_java == True,
                        # WebRepositoryDAO.is_selenium_tested_python == True,
                        # WebRepositoryDAO.is_selenium_tested_javascript == True,
                        # WebRepositoryDAO.is_selenium_tested_typescript == True,
                        # WebRepositoryDAO.is_puppeteer_tested_python == True,
                        # WebRepositoryDAO.is_puppeteer_tested_javascript == True,
                        # WebRepositoryDAO.is_puppeteer_tested_typescript == True,
                        WebRepositoryDAO.is_playwright_tested_java == True,
                        # WebRepositoryDAO.is_playwright_tested_python == True,
                        # WebRepositoryDAO.is_playwright_tested_javascript == True,
                        # WebRepositoryDAO.is_playwright_tested_typescript == True,
                        # WebRepositoryDAO.is_cypress_tested_javascript == True,
                        # WebRepositoryDAO.is_cypress_tested_typescript == True,
                        WebRepositoryDAO.is_locust_tested_java == True,
                        WebRepositoryDAO.is_locust_tested_python == True,
                        WebRepositoryDAO.is_jmeter_tested == True
                    ),
                        WebRepositoryDAO.name == "nuxeo/nuxeo"
                )
            )
            records = query.all()
            return records

        except Exception as e:
            print(f"Error connecting to the database: {e}")

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
                    shutil.rmtree(item_path, ignore_errors=False, onerror=FetchDataUtils.handle_remove_readonly)
                else:
                    os.remove(item_path)
            except Exception as e:
                print(f"Error removing {item_path}: {e}")
        print('Folder succesfully cleaned!')

    @staticmethod
    def create_directory(directory_path):
        try:
            # Crea la directory e tutte le sue directory genitore
            os.makedirs(directory_path, exist_ok=True)
            print(f"Directory '{directory_path}' creata con successo.")
        except Exception as e:
            print(f"Errore durante la creazione della directory: {e}")

    @staticmethod
    def run_java_command(repo_name, out_path):
        command = [
            'java', '-jar',
            r'C:\Users\sergi\IdeaProjects\ck\target\ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar',
            os.path.join(r"C:\Users\sergi\Desktop\ICST25-E2EMining\clone", repo_name),
            'true', '0', 'false',
            out_path
        ]

        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            print("Output:")
            print(result.stdout)
            print("Errori:")
            print(result.stderr)
            print("Codice di ritorno:", result.returncode)
        except subprocess.CalledProcessError as e:
            print(f"Il comando è fallito con codice di ritorno {e.returncode}")
            print("Output:")
            print(e.stdout)
            print("Errori:")
            print(e.stderr)

    @staticmethod
    def run_cloc_csv(input_dir: str, output_file: str):
        """
        Esegue il comando cloc e salva l'output in formato CSV in un file utilizzando l'opzione -out.

        Args:
        - input_dir (str): La directory di input per cloc.
        - output_file (str): Il percorso del file di output CSV.
        """
        # Costruisci il comando cloc per ottenere l'output in formato CSV e specifica il file di output
        # command = ['cloc', '--include-ext=js,ts', '--csv', f'--out={output_file}', input_dir]
        command = ['cloc', '--csv', f'--out={output_file}', input_dir]

        try:
            # Esegui il comando cloc
            subprocess.run(command, check=True)
            print(f"Output salvato in {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Errore durante l'esecuzione di cloc: {e}")


    @staticmethod
    def empty_recycle_bin():
        try:
            # Chiama l'API di Windows per svuotare il cestino
            # ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 1)
            FetchDataUtils.clear_directory("/home/sergio/.local/share/Trash/files")
            print("Cestino svuotato con successo.")
        except Exception as e:
            print(f"Errore durante lo svuotamento del cestino: {e}")


    @staticmethod
    def rename_dir(old_name, new_name):
        # Assicurati che il nuovo percorso non esista già
        if not os.path.exists("/home/sergio/ICST25-E2EMining/clone/"+new_name):
            # Rinomina la directory
            os.rename("/home/sergio/ICST25-E2EMining/clone/" + old_name, "/home/sergio/ICST25-E2EMining/clone/" + new_name)
            print(f"La directory è stata rinominata")
        else:
            print(f"Errore: La directory di destinazione esiste già.")

    @staticmethod
    def check_test(repositories: []):
        path_folder_clone = f"/home/sergio/ICST25-E2EMining/clone"
        cloner = Cloner(path_folder_clone)

        for repo in repositories:
            cloner.clone_repository(repo.name)
            # Rinomina la directory
            original_name = repo.name.replace('/', '\\')
            new_name = repo.name.replace('/', '_')

            #print(f"Rinominazione dir: {original_name} -> {new_name}")
            FetchDataUtils.rename_dir(original_name, new_name)

            tests_path = repo.test_path.split(";")

            for test_path in tests_path[:-1]:
                print(f"test_path: {test_path}")
                number_jmeter_test = 0
                number_locust_test = 0

                # Sostituisci il percorso Windows con il percorso Unix-like
                if(test_path.strip().startswith('C:\\rep\\')):
                    file_path = test_path.replace('C:\\rep\\', '/home/sergio/ICST25-E2EMining/clone/')
                elif(test_path.strip().startswith('C:\\re\\')):
                    file_path = test_path.replace('C:\\re\\', '/home/sergio/ICST25-E2EMining/clone/')
                else:
                    print(f"altro caso {test_path}")
                #print('before')
                #print(file_path)

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

                #print(f"file : {new_path} con estensione {estensione}")
                if os.path.exists(new_path):
                    if(estensione == ".jmx"):
                        number_jmeter_test+=1
                        FetchDataUtils.create_test_res_to_csv([repo.name,new_path,1,0,0,0,0,0,0,FetchDataUtils.get_numlines_byfile(new_path)],new_name+".csv")
                    elif(estensione == ".py"):
                       number_locust_test+=1
                       FetchDataUtils.create_test_res_to_csv(
                           [repo.name, new_path,0, 1, 0, 0, 0, 0, 0, FetchDataUtils.get_numlines_byfile(new_path)],
                           new_name + ".csv")
                    elif(estensione == ".java"):
                        data = FetchDataUtils.check_selenium_playwrite_test(repo,new_path)
                        FetchDataUtils.create_test_res_to_csv(data,new_name + ".csv")
                else:
                    print("file non presente!")
            # Pulizia delle directory (facoltativa)
            FetchDataUtils.clear_directory(path_folder_clone)
            FetchDataUtils.empty_recycle_bin()



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
    def create_test_res_to_csv(data, filename, res_path='/home/sergio/ICST25-E2EMining/java_test_analysis/'):
        # Verifica se il file CSV esiste
        file_exists = os.path.isfile(res_path+filename)
        # Apri il file in modalità append
        with open(res_path+filename, mode='a', newline='') as file:
            writer = csv.writer(file)

            # Se il file non esiste, scrivi l'intestazione
            if not file_exists:
                writer.writerow(['Repository', 'File Path','Is JMeter','Is Locust', 'Is Selenium', 'Is Playwright', 'With JUnit', 'With TestNG',
                                 'Number of @Test', 'Number of Lines'])

            # Scrivi i dati
            writer.writerow(data)


    @staticmethod
    def check_selenium_playwrite_test(repo, path):
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
                    with_junit =1
                elif 'import org.testng' in line:
                    with_testng =1
                elif '@Test' in line:
                    num_test+=1
            return [repo.name,path,0,0,is_selenium,is_playwright,with_junit,with_testng,num_test,len(lines)]
        except FileNotFoundError:
            print(f"File non trovato: {path}")
        except Exception as e:
            print(f"Errore durante l'apertura del file: {e}")
        return  []


    @staticmethod
    def analyze_project(repositories: []):
        black_list = ['DeBankDeFi/DeBankChain', 'laboratoria/bootcamp', 'invoiceninja/invoiceninja']
        path_folder_clone = f"/home/sergio/ICST25-E2EMining/clone"
        # path_folder_metrics = f"/home/sergio/ICST25-E2EMining/metrics"
        # path_folder_metrics = f"/home/sergio/ICST25-E2EMining/metrics/all-project"
        path_folder_metrics = f"/home/sergio/ICST25-E2EMining/py-radon-metrics"
        cloner = Cloner(path_folder_clone)
        for repo in repositories:
            if repo.name not in black_list:
                name_new_folder = repo.name.replace('/', '-')

                # out_path = os.path.join(path_folder_metrics,name_new_folder)
                cloner.clone_repository(repo.name)
                # ANALISI

                # JAVA CK
                # FetchDataUtils.run_java_command(repo.name,out_path)

                # CLOC
                # FetchDataUtils.run_cloc_csv(os.path.join(path_folder_clone,repo.name.replace('/','\\')),out_path)

                # RADON PYTHON
                '''
                FetchDataUtils.analyze_radon_project(
                    #"/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories",
                    os.path.join(path_folder_clone, repo.name.replace('/', '\\\\')),
                    "/home/sergio/ICST25-E2EMining/py-radon-metrics",
                    repo.name.replace('/','\\'))
                '''

                FetchDataUtils.clear_directory(path_folder_clone)
                FetchDataUtils.empty_recycle_bin()

    '''    
    @staticmethod
    def enable_git_long_paths():
        try:
            # Enable long paths in Git
            subprocess.run(['git', 'config', '--system', 'core.longpaths', 'true'], check=True)
            print("Enabled long paths in Git.")
        except subprocess.CalledProcessError as e:
            print(f"Error enabling long paths in Git: {e}")
            exit(1)
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


records = FetchDataUtils.fetch_java_webrepo()
# records = FetchDataUtils.getRepoByName("googlecloudplatform/bank-of-anthos")
print(len(records))
# path_folder_clone = f"/home/sergio/ICST25-E2EMining/clone"
FetchDataUtils.enable_git_long_paths()
FetchDataUtils.check_test(records)
