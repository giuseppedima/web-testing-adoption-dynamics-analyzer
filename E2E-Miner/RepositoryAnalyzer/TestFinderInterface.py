from abc import ABC, abstractmethod
import os

from RepositoryAnalyzer.EncodingDetector import EncodingDetector


class TestDependencyFinderInterface(ABC):

    @abstractmethod
    def has_test_dependency(self, dependencies, repository, webrepository, repo_path):
        pass


class SeleniumTestDependencyFinder(TestDependencyFinderInterface, ABC):

    def has_test_dependency(self, dependencies, repository, webrepository, repo_path):
        dependency_founded = False
        if 'Java' in repository.languages or repository.main_language == 'Java':
            if SeleniumTestDependencyFinderJava().find_dependency(dependencies, webrepository, repo_path):
                dependency_founded = True
        if 'Python' in repository.languages or repository.main_language == 'Python':
            if SeleniumTestDependencyFinderPython().find_dependency(dependencies, webrepository, repo_path):
                dependency_founded = True
        if 'JavaScript' in repository.languages or repository.main_language == 'JavaScript':
            if SeleniumTestDependencyFinderJavaScript().find_dependency(dependencies, webrepository, repo_path):
                dependency_founded = True
        if 'TypeScript' in repository.languages or repository.main_language == 'TypeScript':
            if SeleniumTestDependencyFinderTypeScript().find_dependency(dependencies, webrepository, repo_path):
                dependency_founded = True
        return dependency_founded


class ToolFinderForLanguage(ABC):

    @abstractmethod
    def find_dependency(self, dependency_list, webrepository, repo_path):
        pass


class SeleniumTestDependencyFinderJava(ToolFinderForLanguage, ABC):
    def find_dependency(self, dependency_list, webrepository, repo_path):
        for dependency in dependency_list:
            if dependency[0] == 'org.seleniumhq.selenium':
                path_list = self.find_import_selenium(repo_path)
                if len(path_list) > 0:
                    webrepository.set_is_selenium_tested_java(True)
                    webrepository.add_path_in_list(path_list)
                print("usa selenium")
                return True
        return False

    def find_import_selenium(self, directory):
        files_with_selenium_import = []

        for root, dirs, files in os.walk(directory):
            for file_name in files:
                if file_name.endswith('.java'):
                    file_path = os.path.join(root, file_name)
                    encoding = EncodingDetector.detect_encoding(file_path)
                    try:
                        with open(file_path, 'r', encoding=encoding) as file:
                            lines = file.readlines()
                            for line in lines:
                                if 'import org.openqa.selenium' in line:
                                    files_with_selenium_import.append(file_path)
                                    break
                    except (UnicodeDecodeError, IOError) as e:
                        print(f"Ignorato {file_path} a causa di un errore: {e}")
        return files_with_selenium_import


class SeleniumTestDependencyFinderPython(ToolFinderForLanguage, ABC):

    def find_dependency(self, dependency_list, webrepository, repo_path):
        for dependency in dependency_list:
            if dependency[0] == 'selenium':
                path_list = self.find_import_selenium(repo_path)
                if len(path_list) > 0:
                    webrepository.add_path_in_list(path_list)
                    webrepository.set_is_selenium_tested_python(True)
                print("usa selenium")
                return True
        return False

    def find_import_selenium(self, directory):
        files_with_selenium_import = []

        for root, dirs, files in os.walk(directory):
            for file_name in files:
                if file_name.endswith('.py'):
                    file_path = os.path.join(root, file_name)
                    encoding = EncodingDetector.detect_encoding(file_path)
                    try:
                        with open(file_path, 'r', encoding=encoding) as file:
                            lines = file.readlines()
                            for line in lines:
                                if 'from selenium import' in line:
                                    files_with_selenium_import.append(file_path)
                                    break
                    except (UnicodeDecodeError, IOError) as e:
                        print(f"Ignorato {file_path} a causa di un errore: {e}")
        return files_with_selenium_import


class SeleniumTestDependencyFinderJavaScript(ToolFinderForLanguage, ABC):

    def find_dependency(self, dependency_list, webrepository, repo_path):
        for dependency in dependency_list:
            if dependency[0] == 'selenium' or dependency[0] == 'selenium-webdriver':
                path_list = self.find_import_selenium(repo_path)
                if len(path_list) > 0:
                    webrepository.set_is_selenium_tested_javascript(True)
                    webrepository.add_path_in_list(path_list)
                print("usa selenium")
                return True
        return False

    def find_import_selenium(self, directory):
        files_with_selenium_import = []

        for root, dirs, files in os.walk(directory):
            for file_name in files:
                if file_name.endswith('.js'):
                    file_path = os.path.join(root, file_name)
                    encoding = EncodingDetector.detect_encoding(file_path)
                    try:
                        with open(file_path, 'r', encoding=encoding) as file:
                            lines = file.readlines()
                            for line in lines:
                                if 'require(\'selenium-webdriver\')' in line or 'import selenium' in line:
                                    files_with_selenium_import.append(file_path)
                                    break
                    except (UnicodeDecodeError, IOError) as e:
                        print(f"Ignorato {file_path} a causa di un errore: {e}")
        return files_with_selenium_import


class SeleniumTestDependencyFinderTypeScript(ToolFinderForLanguage, ABC):

    def find_dependency(self, dependency_list, webrepository, repo_path):
        for dependency in dependency_list:
            if dependency[0] == '@types/selenium' or dependency[0] == '@types/selenium-webdriver':
                path_list = self.find_import_selenium(repo_path)
                if len(path_list) > 0:
                    webrepository.add_path_in_list(path_list)
                    webrepository.set_is_selenium_tested_typescript(True)
                    print("usa selenium")
                return True
        return False

    def find_import_selenium(self, directory):
        files_with_selenium_import = []

        for root, dirs, files in os.walk(directory):
            for file_name in files:
                if file_name.endswith('.ts'):
                    file_path = os.path.join(root, file_name)
                    encoding = EncodingDetector.detect_encoding(file_path)
                    try:
                        with open(file_path, 'r', encoding=encoding) as file:
                            lines = file.readlines()
                            for line in lines:
                                if 'from "selenium-webdriver"' in line:
                                    files_with_selenium_import.append(file_path)
                                    break
                    except (UnicodeDecodeError, IOError) as e:
                        print(f"Ignorato {file_path} a causa di un errore: {e}")
        return files_with_selenium_import


class PlayWrightTestDependencyFinder(TestDependencyFinderInterface, ABC):

    def has_test_dependency(self, dependencies, repository, webrepository, repo_path):
        dependency_founded = False
        if 'Java' in repository.languages or repository.main_language == 'Java':
            if PlayWrightTestDependencyFinderJava().find_dependency(dependencies, webrepository, repo_path):
                dependency_founded = True
        if 'Python' in repository.languages or repository.main_language == 'Python':
            if PlayWrightTestDependencyFinderPython().find_dependency(dependencies, webrepository, repo_path):
                dependency_founded = True
        if 'JavaScript' in repository.languages or repository.main_language == 'JavaScript':
            if PlayWrightTestDependencyFinderJavaScript().find_dependency(dependencies, webrepository, repo_path):
                dependency_founded = True
        if 'TypeScript' in repository.languages or repository.main_language == 'TypeScript':
            if PlayWrightTestDependencyFinderTypeScript().find_dependency(dependencies, webrepository, repo_path):
                dependency_founded = True
        return dependency_founded


class PlayWrightTestDependencyFinderJava(ToolFinderForLanguage, ABC):
    def find_dependency(self, dependency_list, webrepository, repo_path):
        for dependency in dependency_list:
            if dependency[0] == 'com.microsoft.playwright':
                path_list = self.find_import_playwright(repo_path)
                if len(path_list) > 0:
                    webrepository.add_path_in_list(path_list)
                    webrepository.set_is_playwright_tested_java(True)
                print("usa playwright")
                return True
        return False

    def find_import_playwright(self, directory):
        files_with_playwright_import = []

        for root, dirs, files in os.walk(directory):
            for file_name in files:
                if file_name.endswith('.java'):
                    file_path = os.path.join(root, file_name)
                    encoding = EncodingDetector.detect_encoding(file_path)
                    try:
                        with open(file_path, 'r', encoding=encoding) as file:
                            lines = file.readlines()
                            for line in lines:
                                # Verifica se la riga contiene un'importazione di Selenium
                                if 'import com.microsoft.playwright' in line:
                                    files_with_playwright_import.append(file_path)
                                    break
                    except (UnicodeDecodeError, IOError) as e:
                        print(f"Ignorato {file_path} a causa di un errore: {e}")
        return files_with_playwright_import


class PlayWrightTestDependencyFinderPython(ToolFinderForLanguage, ABC):
    def find_dependency(self, dependency_list, webrepository, repo_path):
        for dependency in dependency_list:
            if dependency[0] == 'playwright' or dependency[0] == 'pytest-playwright':
                path_list = self.find_import_playwright(repo_path)
                if len(path_list) > 0:
                    webrepository.set_is_playwright_tested_python(True)
                    webrepository.add_path_in_list(path_list)
                print("usa playwright")
                return True
        return False

    def find_import_playwright(self, directory):
        files_with_playwright_import = []

        for root, dirs, files in os.walk(directory):
            for file_name in files:
                if file_name.endswith('.py'):
                    file_path = os.path.join(root, file_name)
                    encoding = EncodingDetector.detect_encoding(file_path)
                    try:
                        with open(file_path, 'r', encoding=encoding) as file:
                            lines = file.readlines()
                            for line in lines:
                                if 'from playwright.async_api import' in line or 'from playwright.sync_api import' in line:
                                    files_with_playwright_import.append(file_path)
                                    break
                    except (UnicodeDecodeError, IOError) as e:
                        print(f"Ignorato {file_path} a causa di un errore: {e}")
        return files_with_playwright_import


class PlayWrightTestDependencyFinderJavaScript(ToolFinderForLanguage, ABC):
    def find_dependency(self, dependency_list, webrepository, repo_path):
        for dependency in dependency_list:
            if dependency[0] == 'playwright':
                print("usa playwright")
                path_list = self.find_import_playwright(repo_path)
                if len(path_list) > 0:
                    webrepository.add_path_in_list(path_list)
                    webrepository.set_is_playwright_tested_javascript(True)
                return True

    def find_import_playwright(self, directory):
        files_with_playwright_import = []

        for root, dirs, files in os.walk(directory):
            for file_name in files:
                if file_name.endswith('.js'):
                    file_path = os.path.join(root, file_name)
                    encoding = EncodingDetector.detect_encoding(file_path)
                    try:
                        with open(file_path, 'r', encoding=encoding) as file:
                            lines = file.readlines()
                            for line in lines:
                                if 'from \'@playwright/test\'' in line:
                                    files_with_playwright_import.append(file_path)
                                    break
                    except (UnicodeDecodeError, IOError) as e:
                        print(f"Ignorato {file_path} a causa di un errore: {e}")
        return files_with_playwright_import


class PlayWrightTestDependencyFinderTypeScript(ToolFinderForLanguage, ABC):
    def find_dependency(self, dependency_list, webrepository, repo_path):
        for dependency in dependency_list:
            if dependency[0] == 'playwright':
                print("usa playwright")
                path_list = self.find_import_playwright(repo_path)
                if len(path_list) > 0:
                    webrepository.add_path_in_list(path_list)
                    webrepository.set_is_playwright_tested_typescript(True)
                return True

    def find_import_playwright(self, directory):
        files_with_playwright_import = []

        for root, dirs, files in os.walk(directory):
            for file_name in files:
                if file_name.endswith('.ts'):
                    file_path = os.path.join(root, file_name)
                    encoding = EncodingDetector.detect_encoding(file_path)
                    try:
                        with open(file_path, 'r', encoding=encoding) as file:
                            lines = file.readlines()
                            for line in lines:
                                if 'from \'@playwright/test\'' in line:
                                    files_with_playwright_import.append(file_path)
                                    break
                    except (UnicodeDecodeError, IOError) as e:
                        print(f"Ignorato {file_path} a causa di un errore: {e}")
        return files_with_playwright_import


class PuppeteerTestDependencyFinder(TestDependencyFinderInterface, ABC):

    def has_test_dependency(self, dependencies, repository, webrepository, repo_path):
        dependency_founded = False
        if 'Python' in repository.languages or repository.main_language == 'Python':
            if PuppeteerTestDependencyFinderPython().find_dependency(dependencies, webrepository, repo_path):
                dependency_founded = True
        if 'JavaScript' in repository.languages or repository.main_language == 'JavaScript':
            if PuppeteerTestDependencyFinderJavaScript().find_dependency(dependencies, webrepository, repo_path):
                dependency_founded = True
        if 'TypeScript' in repository.languages or repository.main_language == 'TypeScript':
            if PuppeteerTestDependencyFinderTypeScript().find_dependency(dependencies, webrepository, repo_path):
                dependency_founded = True
        return dependency_founded

class PuppeteerTestDependencyFinderPython(ToolFinderForLanguage, ABC):
    def find_dependency(self, dependency_list, webrepository, repo_path):
        for dependency in dependency_list:
            if dependency[0] == 'pyppeteer':
                path_list = self.find_import_puppeteer(repo_path)
                if len(path_list) > 0:
                    webrepository.add_path_in_list(path_list)
                    webrepository.set_is_puppeteer_tested_python(True)
                print("usa puppeteer")
                return True
        return False

    def find_import_puppeteer(self, directory):
        files_with_puppeteer_import = []

        for root, dirs, files in os.walk(directory):
            for file_name in files:
                if file_name.endswith('.py'):
                    file_path = os.path.join(root, file_name)
                    encoding = EncodingDetector.detect_encoding(file_path)
                    try:
                        with open(file_path, 'r', encoding=encoding) as file:
                            lines = file.readlines()
                            for line in lines:
                                if 'from pyppeteer import' in line:
                                    files_with_puppeteer_import.append(file_path)
                                    break
                    except (UnicodeDecodeError, IOError) as e:
                        # Ignora il file in caso di errore di decodifica o di I/O
                        print(f"Ignorato {file_path} a causa di un errore: {e}")
        return files_with_puppeteer_import


class PuppeteerTestDependencyFinderJavaScript(ToolFinderForLanguage, ABC):
    def find_dependency(self, dependency_list, webrepository, repo_path):
        for dependency in dependency_list:
            if dependency[0] == 'puppeteer':
                path_list = self.find_import_puppeteer(repo_path)
                if len(path_list) > 0:
                    webrepository.add_path_in_list(path_list)
                    webrepository.set_is_puppeteer_tested_javascript(True)
                print("usa puppeteer")
                return True
        return False

    def find_import_puppeteer(self, directory):
        files_with_puppeteer_import = []

        for root, dirs, files in os.walk(directory):
            for file_name in files:
                if file_name.endswith('.js'):
                    file_path = os.path.join(root, file_name)
                    encoding = EncodingDetector.detect_encoding(file_path)
                    try:
                        with open(file_path, 'r', encoding=encoding) as file:
                            lines = file.readlines()
                            for line in lines:
                                if 'require(\'puppeteer\')' in line:
                                    files_with_puppeteer_import.append(file_path)
                                    break
                    except (UnicodeDecodeError, IOError) as e:
                        print(f"Ignorato {file_path} a causa di un errore: {e}")
        return files_with_puppeteer_import


class PuppeteerTestDependencyFinderTypeScript(ToolFinderForLanguage, ABC):
    def find_dependency(self, dependency_list, webrepository, repo_path):
        for dependency in dependency_list:
            if dependency[0] == '@types/puppeteer':
                path_list = self.find_import_puppeteer(repo_path)
                if len(path_list) > 0:
                    webrepository.set_is_puppeteer_tested_typescript(True)
                    webrepository.add_path_in_list(path_list)
                print("usa puppeteer")
                return True
        return False

    def find_import_puppeteer(self, directory):
        files_with_puppeteer_import = []

        for root, dirs, files in os.walk(directory):
            for file_name in files:
                if file_name.endswith('.ts'):
                    file_path = os.path.join(root, file_name)
                    encoding = EncodingDetector.detect_encoding(file_path)
                    try:
                        with open(file_path, 'r', encoding=encoding) as file:
                            lines = file.readlines()
                            for line in lines:
                                if 'from \'puppeteer\'' in line:
                                    files_with_puppeteer_import.append(file_path)
                                    break
                    except (UnicodeDecodeError, IOError) as e:
                        print(f"Ignorato {file_path} a causa di un errore: {e}")
        return files_with_puppeteer_import


class CypressTestDependencyFinder(TestDependencyFinderInterface, ABC):
    def has_test_dependency(self, dependencies, repository, webrepository, repo_path):
        dependency_founded = False
        if 'JavaScript' in repository.languages or repository.main_language == 'JavaScript':
            if CypressTestDependencyFinderJavaScript().find_dependency(dependencies, webrepository, repo_path):
                dependency_founded = True
        if 'TypeScript' in repository.languages or repository.main_language == 'TypeScript':
            if CypressTestDependencyFinderTypeScript().find_dependency(dependencies, webrepository, repo_path):
                dependency_founded = True
        return dependency_founded


class CypressTestDependencyFinderJavaScript(ToolFinderForLanguage, ABC):
    def find_dependency(self, dependencies, webrepository, repo_path):
        for dependency in dependencies:
            if dependency[0] == 'cypress':
                path_list = self.find_import_cypress(repo_path)
                if len(path_list) > 0:
                    webrepository.add_path_in_list(path_list)
                    webrepository.set_is_cypress_tested_javascript(True)
                print("usa cypress")
                return True
        return False

    def find_import_cypress(self, directory):
        files_with_cypress_import = []

        # Attraversa ricorsivamente tutte le sottodirectory
        for root, dirs, files in os.walk(directory):
            for file_name in files:
                if file_name.endswith('.cy.js'):
                    file_path = os.path.join(root, file_name)
                    files_with_cypress_import.append(file_path)
        return files_with_cypress_import


class CypressTestDependencyFinderTypeScript(ToolFinderForLanguage, ABC):
    def find_dependency(self, dependencies, webrepository, repo_path):
        for dependency in dependencies:
            if dependency[0] == 'cypress':
                path_list = self.find_import_cypress(repo_path)
                if len(path_list) > 0:
                    webrepository.add_path_in_list(path_list)
                    webrepository.set_is_cypress_tested_typescript(True)
                print("usa cypress")
                return True
        return False

    def find_import_cypress(self, directory):
        files_with_cypress_import = []

        for root, dirs, files in os.walk(directory):
            for file_name in files:
                if file_name.endswith('.cy.ts'):
                    file_path = os.path.join(root, file_name)
                    files_with_cypress_import.append(file_path)
        return files_with_cypress_import


class LocustTestDependencyFinder(TestDependencyFinderInterface, ABC):
    def has_test_dependency(self, dependencies, repository, webrepository, repo_path):
        dependency_founded = False
        if 'Java' in repository.languages or repository.main_language == 'Java':
            if LocustTestDependencyFinderJava().find_dependency(dependencies, webrepository, repo_path):
                dependency_founded = True
        if 'Python' in repository.languages or repository.main_language == 'Python':
            if LocustTestDependencyFinderPython().find_dependency(dependencies, webrepository, repo_path):
                dependency_founded = True
        return dependency_founded


class LocustTestDependencyFinderJava(ToolFinderForLanguage, ABC):

    def find_dependency(self, dependency_list, webrepository, repo_path):
        for dependency in dependency_list:
            if dependency[0] == 'com.github.myzhan' and dependency[1] == 'locust4j':
                path_list = self.find_import_locust(repo_path)
                if len(path_list) > 0:
                    webrepository.add_path_in_list(path_list)
                    webrepository.set_is_locust_tested_java(True)
                print("usa locust")
                return True
        return False

    def find_import_locust(self, directory):
        files_with_locust_import = []

        for root, dirs, files in os.walk(directory):
            for file_name in files:
                if file_name.endswith('.java'):
                    file_path = os.path.join(root, file_name)
                    encoding = EncodingDetector.detect_encoding(file_path)
                    try:
                        with open(file_path, 'r', encoding=encoding) as file:
                            lines = file.readlines()
                            for line in lines:
                                if 'import com.github.myzhan.locust4j' in line:
                                    files_with_locust_import.append(file_path)
                                    break
                    except (UnicodeDecodeError, IOError) as e:
                        print(f"Ignorato {file_path} a causa di un errore: {e}")
        return files_with_locust_import


class LocustTestDependencyFinderPython(ToolFinderForLanguage, ABC):

    def find_dependency(self, dependency_list, webrepository, repo_path):
        for dependency in dependency_list:
            if dependency[0] == 'locust' or dependency[0] == 'locustio':
                webrepository.set_is_locust_tested_python(True)
                path_list = self.find_import_locust(repo_path)
                if len(path_list) > 0:
                    webrepository.add_path_in_list(path_list)
                print("usa locust")
                return True
        return False

    def find_import_locust(self, directory):
        files_with_locust_import = []

        for root, dirs, files in os.walk(directory):
            for file_name in files:
                if file_name.endswith('.py'):
                    file_path = os.path.join(root, file_name)
                    encoding = EncodingDetector.detect_encoding(file_path)
                    try:
                        with open(file_path, 'r', encoding=encoding) as file:
                            lines = file.readlines()
                            for line in lines:
                                if 'from locust import' in line:
                                    files_with_locust_import.append(file_path)
                                    break
                    except (UnicodeDecodeError, IOError) as e:
                        print(f"Ignorato {file_path} a causa di un errore: {e}")
        return files_with_locust_import


class JMeterTestDependencyFinder(TestDependencyFinderInterface, ABC):
    def has_test_dependency(self, dependencies, repository, webrepository, repo_path):
        ret = False
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                if file.endswith('.jmx'):
                    webrepository.set_is_jmeter_tested(True)
                    ret = True
                    webrepository.test_path.append(os.path.join(root, file))
                    print("Usa JMeter")

        return ret
