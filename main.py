from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='logfile.log', encoding='utf-8', level=logging.INFO)
import sys

print(sys.path)

sys.path.append("Dataset")
from Dataset.DataSet import DataSet
from Dataset.FilterStrategy import Filter
from RepositoryAnalyzer.Analyzer import AnalyzerController

dataset = DataSet()

filtro = Filter(is_fork=False, commits=2000, contributors=10, stargazers=100, languages=['JavaScript'])
risultati_filtrati = dataset.filter_repositories(filtro)

analyzer = AnalyzerController(risultati_filtrati)
analyzer.analyze_repositories()
