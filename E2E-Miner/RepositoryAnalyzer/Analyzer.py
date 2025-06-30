import errno
import json
import os
import queue
import shutil
import stat
import subprocess
import threading
import re
import time
from abc import ABC, abstractmethod
import logging
from RepositoryAnalyzer.EncodingDetector import EncodingDetector

logger = logging.getLogger(__name__)
logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.INFO)

from Dataset.Repository import NonTrivialRepo,NonTrivialRepoDao
from RepositoryAnalyzer.AnalyzerInterface import Analyzer, DependencyFileFinderInterface, WebAnalyzerInterface
from RepositoryAnalyzer.RepositoryCloner import Cloner

from RepositoryAnalyzer.TestFinderInterface import SeleniumTestDependencyFinder, \
    PlayWrightTestDependencyFinder, PuppeteerTestDependencyFinder, CypressTestDependencyFinder, \
    LocustTestDependencyFinder, JMeterTestDependencyFinder


def handle_remove_readonly(func, path, exc):
    excvalue = exc[1]
    if func in (os.rmdir, os.remove, os.unlink) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
        func(path)
    else:
        raise


class AnalyzerController(Analyzer, ABC):
    def __init__(self, repository, max_threads=20, output_folder=r"C:\rep"):
        self.repository = repository
        self.max_threads = max_threads
        self.output_folder = output_folder
        self.repositories_queue = self.create_repositories_queue(repository)
        self.lock = threading.Lock()
        self.language_to_analyze = ['Java', 'Python', 'JavaScript', 'TypeScript']


        self.test_dependency = [SeleniumTestDependencyFinder(), PlayWrightTestDependencyFinder(),
                                PuppeteerTestDependencyFinder(), CypressTestDependencyFinder(),
                                LocustTestDependencyFinder(), JMeterTestDependencyFinder()]


    def create_repositories_queue(self, repositories):
        q = queue.Queue()
        c = 0
        for item in repositories:
            q.put(item)
            c += 1
        print("coda lunga " + str(c))
        return q

    def analyze_all_repository(self):
        while True:
            with self.lock:
                if self.repositories_queue.empty():
                    break
                repository_to_analyze = self.repositories_queue.get()
                logging.info("ho preso dalla coda " + repository_to_analyze.name)

            print(repository_to_analyze.name)

            print(f"analyzing {repository_to_analyze.name}...")

            cloner = Cloner(self.output_folder)
            cloned_repository = cloner.clone_repository(repository_to_analyze.name)
            if cloned_repository == '':
                logging.info("non sono riuscito a scaricare " + repository_to_analyze.name)
                self.repositories_queue.task_done()
                print("repository non clonata")
            else:
                dependency_file_list = []
                dependencies = []
                for language in self.language_to_analyze:
                    if language in repository_to_analyze.languages or language == repository_to_analyze.main_language:
                        dependency_file_list += DependencyFileFinderInterface.factory_finder(
                            language).find_dependency_file(cloned_repository)
                print(dependency_file_list)
                for file in dependency_file_list:
                    dependencies = DependencyFinderInterface.factory_analyzer(file).find_dependency(file, dependencies)

                print("dipendenze per " + repository_to_analyze.name)
                print(dependencies)

                NonTrivialRepo = NonTrivialRepo(repository_to_analyze.ID, repository_to_analyze.name)

                # if WebAnalyzer.is_web_repository(repository_to_analyze, dependencies):
                for language in self.language_to_analyze:
                    web_list = WebDependencyListCreator(language).trasport_file_dependencies_in_list()
                    web_dependencies = WebAnalyzer().find_web_dependencies(web_list, dependencies)
                    if len(web_dependencies) > 0:
                        WebFlags().change_flag(language, NonTrivialRepo)
                        NonTrivialRepo.web_dependencies += web_dependencies

                if WebFlags().check_flag(NonTrivialRepo):
                    print(repository_to_analyze.name + "è web")

                for dependency in self.test_dependency:
                    if dependency.has_test_dependency(dependencies, repository_to_analyze, NonTrivialRepo,
                                                      cloned_repository):
                        print("trovata una dipendenza test")

                with self.lock:
                    NonTrivialRepoDAO(NonTrivialRepo).add_web_repository_to_db()

                with self.lock:
                    repository_to_analyze.update_processed_repository()

                #SE NON SONO STATI RITROVATI TOOL DI TEST E2E ELIMINA LE CARTELLE
                if not WebFlags().check_test_flag(NonTrivialRepo):
                    shutil.rmtree(cloned_repository, ignore_errors=False, onerror=handle_remove_readonly)

                self.repositories_queue.task_done()

    def analyze_repositories(self):  # analyze_repositories_with_thread

        # Definisci il comando da eseguire per disattivare core.protectNTFS
        command = ["git", "config", "--global", "core.protectNTFS", "false"]

        # Esegui il comando
        subprocess.run(command)

        threads = []
        for i in range(self.max_threads):
            print("sto creando il thread numero " + str(i))
            thread = threading.Thread(target=self.analyze_all_repository, )
            thread.start()
            threads.append(thread)
            time.sleep(1)

        for thread in threads:
            print("nel secondo for")
            thread.join()


class WebDependencyListCreator:
    def __init__(self, language):
        if language == 'Java':
            self.txt_file_with_dependencies = r"C:\Users\carmi\PycharmProjects\DataMiningRepositorySoftware\RepositoryAnalyzer\WebJavaDependency.txt"
        elif language == 'Python':
            self.txt_file_with_dependencies = r"C:\Users\carmi\PycharmProjects\DataMiningRepositorySoftware\RepositoryAnalyzer\WebPythonDependency.txt"
        elif language == 'JavaScript':
            self.txt_file_with_dependencies = r"C:\Users\carmi\PycharmProjects\DataMiningRepositorySoftware\RepositoryAnalyzer\WebJSDependency.txt"
        elif language == 'TypeScript':
            self.txt_file_with_dependencies = r"C:\Users\carmi\PycharmProjects\DataMiningRepositorySoftware\RepositoryAnalyzer\WebTSDependency.txt"

    def trasport_file_dependencies_in_list(self):
        list_web = []
        with open(self.txt_file_with_dependencies, 'r', encoding='utf-8') as file:
            # Leggo ogni riga del file, rimuovo il carattere di nuova riga e le metto in una lista
            lines = [line.strip() for line in file.readlines()]

        # Aggiungo ogni riga (senza il carattere di nuova riga) alla lista
        for line in lines:
            list_web.append(line.lower())

        print(list_web)
        return list_web


class WebFlags:
    def change_flag(self, language, NonTrivialRepo):
        if language == 'Java':
            NonTrivialRepo.set_is_web_java(True)
        if language == 'Python':
            NonTrivialRepo.set_is_web_python(True)
        if language == 'JavaScript':
            NonTrivialRepo.set_is_web_javascript(True)
        if language == 'TypeScript':
            NonTrivialRepo.set_is_web_typescript(True)

    def check_flag(self, NonTrivialRepo):
        if NonTrivialRepo.is_web_java or NonTrivialRepo.is_web_python or NonTrivialRepo.is_web_javascript:
            return True
        return False

    def check_test_flag(self, NonTrivialRepo):
        if (NonTrivialRepo.is_selenium_tested_java or NonTrivialRepo.is_selenium_tested_typescript or
                NonTrivialRepo.is_selenium_tested_python or NonTrivialRepo.is_selenium_tested_javascript or
                NonTrivialRepo.is_playwright_tested_java or NonTrivialRepo.is_playwright_tested_python or
                NonTrivialRepo.is_playwright_tested_javascript or NonTrivialRepo.is_playwright_tested_typescript or
                NonTrivialRepo.is_puppeteer_tested_python or NonTrivialRepo.is_puppeteer_tested_javascript or
                NonTrivialRepo.is_puppeteer_tested_typescript or NonTrivialRepo.is_cypress_tested_javascript or
                NonTrivialRepo.is_cypress_tested_typescript or NonTrivialRepo.is_locust_tested_java or
                NonTrivialRepo.is_locust_tested_python or NonTrivialRepo.is_jmeter_tested):
            return True
        return False


class WebAnalyzer:

    def find_web_dependencies(self, web_dependencies_list, repository_dependencies):

        founded_dependencies = []
        for web_dependency in web_dependencies_list:
            for dependency in repository_dependencies:
                if dependency[0] == web_dependency:
                    founded_dependencies.append(dependency[0])

        return founded_dependencies

    def has_web_dependencies(self, web_dependencies_list, repository_dependencies):
        for web_dependency in web_dependencies_list:
            for dependency in repository_dependencies:
                if dependency[0] == web_dependency:
                    return True
        return False


class DependencyFinderInterface(ABC):
    @abstractmethod
    def find_dependency(self, dependency_file, dependency_list):
        pass

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

    # cambia i nomi ai finder delle dipendenze, per esempio JavaScriptDependencyFinder in realtà cerca le dipendenze sui package, che stanno anche in TypeScript

    @staticmethod
    def factory_analyzer(dependency_file):
        if 'pom.xml' in dependency_file:
            return PomDependencyFinder()
        elif 'build.gradle' in dependency_file:
            return GradleDependencyFinder()
        elif 'requirements' in dependency_file:
            return RequirementstxtDependencyFinder()
        elif 'package.json' in dependency_file or 'package-lock.json' in dependency_file:
            return JavaScriptDependencyFinder()


class JavaScriptDependencyFileFinder(DependencyFileFinderInterface, ABC):
    def find_dependency_file(self, repository):
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


class txtDependencyFileFinder(DependencyFileFinderInterface, ABC):
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


class MavenOrGradleDependencyFileFinder(DependencyFileFinderInterface, ABC):

    def find_dependency_file(self, repository):
        dependency_files_list = []
        print("vedo questo ->" + str(repository))
        for root, dirs, files in os.walk(repository):
            if 'build.gradle' in files:
                gradle_file = os.path.join(root, 'build.gradle')
                dependency_files_list.append(gradle_file)
                # analyzer = DependencyFinderInterface.factory_analyzer(gradle_file)
                # dependencies = analyzer.find_dependency(gradle_file, dependencies)
                # break  # Interrompi la ricerca se viene trovato build.gradle

            elif 'pom.xml' in files:
                pom_file = os.path.join(root, 'pom.xml')
                dependency_files_list.append(pom_file)
                # analyzer = DependencyFinderInterface.factory_analyzer(pom_file)
                # dependencies = analyzer.find_dependency(pom_file, dependencies)
                # break  # Interrompi la ricerca se viene trovato pom.xml

        return dependency_files_list


class JavaScriptDependencyFinder(DependencyFinderInterface, ABC):

    def find_dependency(self, dependency_file, dependency_list):
        #if 'package.json' in dependency_file or 'package-lock.json' in dependency_file:
        return self.analyze_package_file(dependency_file, dependency_list)
        # elif 'package-lock.json' in dependency_file:
        #    return self.analyze_packagelock_file(dependency_file, dependency_list)

    def analyze_package_file(self, dependency_file, dependency_list):  # fai bene questa cosa
        try:
            #encoding = EncodingDetector.detect_encoding(dependency_file)
            #with open(dependency_file, 'r', encoding=encoding) as file:
            #lockfile = json.load(file)
            lockfile = json.loads(dependency_file)
        except json.JSONDecodeError as e:
            print("File malformato -> ")
            print(e)
            return dependency_list

        def process_dependencies(obj):
            if isinstance(obj, dict):
                if 'dependencies' in obj and isinstance(obj['dependencies'], dict):
                    for package_name, version in obj['dependencies'].items():
                        self.add_dependency_in_list((self.get_package_name(package_name), version), dependency_list)
                if 'devDependencies' in obj and isinstance(obj['devDependencies'], dict):
                    for package_name, version in obj['devDependencies'].items():
                        self.add_dependency_in_list((self.get_package_name(package_name), version), dependency_list)
                for value in obj.values():
                    process_dependencies(value)
            elif isinstance(obj, list):
                for item in obj:
                    process_dependencies(item)

        process_dependencies(lockfile)

        #print(dependency_list)
        return dependency_list

    def get_package_name(self, package_name):
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


class RequirementstxtDependencyFinder(DependencyFinderInterface, ABC):

    def find_dependency(self, dependency_file, dependency_list):
        #print("reading... " + dependency_file)
        #encoding = EncodingDetector.detect_encoding(dependency_file)
        #with open(dependency_file, 'r', encoding=encoding) as file:
        #lines = file.readlines()
        lines = dependency_file.splitlines()
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


class PomDependencyFinder(DependencyFinderInterface, ABC):

    def find_dependency(self, pom_file, dependency_list):
        #logging.info("sto analizzando " + pom_file)
        #print("vedo il file pom di " + pom_file)
        from lxml import etree
        try:
            #root = etree.parse(pom_file).getroot()
            #tree = etree.ElementTree(root)
            if isinstance(pom_file, str):
                pom_file = pom_file.encode('utf-8')  # Converte la stringa in bytes

            root = etree.fromstring(pom_file)
            tree = etree.ElementTree(root)
            depend = tree.xpath("//*[local-name()='dependency']")

            for dep in depend:
                infoDict = {}
                for child in dep.getchildren():
                    tag = child.tag
                    if isinstance(tag, str) and '}' in tag:
                        tag = tag.split('}')[1]
                    text = child.text
                    infoDict[tag] = text

                self.add_dependency_in_list(
                    (infoDict.get('groupId'), infoDict.get('artifactId'), infoDict.get('version')), dependency_list)

            return dependency_list

        except Exception as e:
            #logging.warning("eccezione nel file " + pom_file + ": " + str(e))
            print("eccezione nel file : " + str(e))
            return dependency_list


class GradleDependencyFinder(DependencyFinderInterface, ABC):

    def find_dependency(self, gradle_file, dependency_list):
        #print("vedo il file gradle di " + gradle_file)
        #logging.info("vedo il file gradle di " + gradle_file)
        #encoding = EncodingDetector.detect_encoding(gradle_file)
        try:
            #with open(gradle_file, 'r', encoding=encoding) as file:
                # Cerca le dipendenze nel file Gradle
            #gradle_content = file.read()
            gradle_content = gradle_file
            pattern = re.compile(r"(['\"])(.*?):(.*?):(.*?)\1")
            matches = pattern.findall(gradle_content)
            #print("reading " + gradle_file + "...")
            for match in matches:
                group_id, artifact_id, version = match[1:]
                self.add_dependency_in_list((group_id, artifact_id, version), dependency_list)
        except (UnicodeDecodeError, IOError) as e:
            # Ignora il file in caso di errore di decodifica o di I/O
            print(f"Ignorato {gradle_file} a causa di un errore: {e}")

        return dependency_list


