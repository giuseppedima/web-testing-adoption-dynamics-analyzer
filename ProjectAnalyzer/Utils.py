import csv
import os
import numpy as np

class Utils:
    @staticmethod
    def get_repos_name_by_path(path):
        repos = []
        for name_file in os.listdir(path):
            if(name_file == 'result.csv'):
                percorso_file = os.path.join(path,name_file)
                with open(percorso_file, mode='r', newline='',encoding='utf-8') as file_csv:
                    reader = csv.reader(file_csv)
                    next(reader)
                    for row in reader:
                        repos.append(row[0])
        return repos





py_repos = Utils.get_repos_name_by_path(r'/home/sergio/ICST25-E2EMining/py_test_analysis/')
js_ts_repos = Utils.get_repos_name_by_path(r'/home/sergio/ICST25-E2EMining/js_ts_test_analysis/')
java_repos = Utils.get_repos_name_by_path(r'/home/sergio/ICST25-E2EMining/java_test_analysis')

intersezione_py_js_ts = np.intersect1d(py_repos,js_ts_repos)
print("INTER- PY-JS")
print(len(intersezione_py_js_ts))
print(intersezione_py_js_ts)

intersezione_py_java = np.intersect1d(py_repos,java_repos)
print("INTER- PY-JAVA")
print(len(intersezione_py_java))
print(intersezione_py_java)

intersezione_js_java = np.intersect1d(java_repos,js_ts_repos)
print("INTER- JS-JAVA")
print(len(intersezione_js_java))
print(intersezione_js_java)