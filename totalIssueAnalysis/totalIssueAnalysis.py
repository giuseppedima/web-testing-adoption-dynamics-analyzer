import csv
import requests
import json


from Dataset.DBconnector import Session, engine
from Dataset.Repository import GUITestingRepoDetails

import concurrent

from pathlib import Path
from environment import (
    GITHUB_TOKEN,
    PATH_TO_ISSUES_DOWNLOAD
)

class TotalIssue:

    # Impostazioni della richiesta
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    @staticmethod
    def get_all_issues(state, repo_name):
        import re
        
        issues_url = f"https://api.github.com/repos/{repo_name}/issues"
        all_issues = []
        next_url = None
        #page = 1  # Keep for logging purposes
        
        while True:
            #print(f'page:{page}')
            
            if next_url:
                # Use the complete URL from the Link header
                response = requests.get(next_url, headers=TotalIssue.headers)
            else:
                # First request
                params = {
                    "state": state,  # Stato delle issue
                    "per_page": 100,  # Numero di issue per pagina (max 100)
                }
                response = requests.get(issues_url, headers=TotalIssue.headers, params=params)
            
            if response.status_code == 200:
                issues = response.json()
                if not issues:  # Se non ci sono più issue, interrompi il ciclo
                    break
                all_issues.extend(issues)  # Aggiungi le issue trovate alla lista
                
                # Extract next URL from Link header
                link_header = response.headers.get('Link', '')
                
                if 'rel="next"' not in link_header:
                    break
                    
                # Extract the complete next URL
                next_match = re.search(r'<([^>]+)>;\s*rel="next"', link_header)
                if next_match:
                    next_url = next_match.group(1)
                    #page += 1  # Increment for logging
                else:
                    break
            else:
                print(f"Errore {response.status_code}: {response.text}")
                raise Exception(f"Error fetching issues for {repo_name}: {response.status_code} - {response.text}")

        return all_issues

    @staticmethod
    def get_number_of_open_closed_issues(repo_name,save_flag):
        out_file_name = Path(PATH_TO_ISSUES_DOWNLOAD) / f"{repo_name.replace('/', '_', 1)}_all_issues.json"

        if out_file_name.exists():
            print(f"File '{out_file_name}' already exists. Skipping download.")
            return

        # Ottenere tutte le issue aperte e chiuse
        open_issues = TotalIssue.get_all_issues("open",repo_name)
        closed_issues = TotalIssue.get_all_issues("closed",repo_name)

        # Unire le issue aperte e chiuse
        all_issues = {
            "open": open_issues,
            "closed": closed_issues
        }
        
        with open(out_file_name,'w') as json_file:
            json.dump(all_issues, json_file, indent=4)  # Indentazione per migliorare la leggibilità
            print(f"{len(open_issues)} issue aperte e {len(closed_issues)} issue chiuse salvate in '{out_file_name}'.")

    @staticmethod
    def get_repo_with_number_of_test_lower_than_n(n):
        try:
            session = Session(bind=engine)
            print("Connection successful!")
            records = session.query(GUITestingRepoDetails).filter(
                GUITestingRepoDetails.number_of_tests <= n
            )
            return records.all()
        except Exception as e:
            print(f"Error connecting to the database: {e}")
        finally:
            session.close()  # Ensure the session is closed after use

    @staticmethod
    def calculate_number_of_issue(start, end):

        missed_repo = TotalIssue.get_repo_with_number_of_test_lower_than_n(30)
        for repo in missed_repo[start:end]:
            repo_name = repo.repository_name
            num_of_test= repo.number_of_tests
            print(f' sto processando {repo_name} con num_of_test:{num_of_test}')
            save_file_issue = num_of_test>0
            TotalIssue.get_number_of_open_closed_issues(repo_name,save_file_issue)

    @staticmethod
    def export_issues_summary_to_csv():

        csv_file = Path(PATH_TO_ISSUES_DOWNLOAD).parent / "issues_summary_repos_lower_than_30.csv"
        if not csv_file.exists():
            with open(csv_file, 'w', newline='', encoding='utf-8') as csv_out:
                writer = csv.writer(csv_out)
                writer.writerow(['repo_name', 'open_issues', 'closed_issues', 'total_issues'])

        for file_path in Path(PATH_TO_ISSUES_DOWNLOAD).glob("*_all_issues.json"):
            with open(file_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
                
                repo_name = file_path.stem.replace('_all_issues', '')
                open_issues = len(data['open'])
                closed_issues = len(data['closed'])

                with open(csv_file, 'a', newline='', encoding='utf-8') as csv_out:
                    writer = csv.writer(csv_out)
                    writer.writerow([repo_name, open_issues, closed_issues, open_issues + closed_issues])


    @staticmethod
    def run_parallel_analysis():
        project_ranges =[
            [0,50],
            [50,100],
            [100,150],
            [150,200],
            [200,250],
            [250,300],
        ]
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = [executor.submit(TotalIssue.calculate_number_of_issue, start, end) for start, end in project_ranges]
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()  # Recupera il risultato del processo
                    print("Analisi completata per un batch.")
                except Exception as exc:
                    print(f"Si è verificato un errore durante l'analisi: {exc}")

if __name__ == "__main__":
    # TotalIssue.run_parallel_analysis()
    TotalIssue.export_issues_summary_to_csv()