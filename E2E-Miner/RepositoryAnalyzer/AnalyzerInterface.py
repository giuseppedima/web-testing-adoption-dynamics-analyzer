from abc import ABC, abstractmethod

class Analyzer(ABC):
    @abstractmethod
    def analyze_all_repository(self):
        pass


class DependencyFileFinderInterface(ABC):
    @abstractmethod
    def find_dependency_file(self, repository):
        pass

    @staticmethod
    def factory_finder(language):
        if language == 'Java':
            from RepositoryAnalyzer.Analyzer import MavenOrGradleDependencyFileFinder
            return MavenOrGradleDependencyFileFinder()
        elif language == 'Python':
            from RepositoryAnalyzer.Analyzer import txtDependencyFileFinder
            return txtDependencyFileFinder()
        elif language == 'JavaScript':
            from RepositoryAnalyzer.Analyzer import JavaScriptDependencyFileFinder
            return JavaScriptDependencyFileFinder()
        elif language == 'TypeScript':
            from RepositoryAnalyzer.Analyzer import JavaScriptDependencyFileFinder
            return JavaScriptDependencyFileFinder()
        else:
            raise ValueError("Linguaggio non ancora implementato")


class WebAnalyzerInterface(ABC):

    @abstractmethod
    def find_web_dependency(self, dependency_list):
        pass
