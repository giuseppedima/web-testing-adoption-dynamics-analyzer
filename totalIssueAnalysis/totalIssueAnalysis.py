'''
import csv
'''
import re
'''
from itertools import islice

import pandas as pd
'''
import requests
import json
import  os
'''
import ast
import matplotlib.pyplot as plt
from matplotlib_venn import venn2
'''

from Dataset.DBconnector import Session, engine
from Dataset.Repository import GUITestingRepoDetails

import concurrent

from pathlib import Path
from environment import (
    GITHUB_TOKEN,
    PATH_TO_ISSUES_DOWNLOAD
)

class TotalIssue:
    '''
    flaky_slow_labels = [
        'flaky-e2e',
        'slow-e2e',
        'metric: stale flaky e2e test report',
        'metric: flaky e2e test'
    ]

    labels_e2e = ['Scope : Test [E2E]',
                  'cypress passed',
                  'cypress failed',
                  'cypress test pending',
                  'cypress',
                  'automation-test-ui',
                  'automation-test-needed',
                  'automation-test-added',
                  'component/e2e',
                  'webdriver',
                  'e2e-test-case',
                  'e2e',
                  'run-e2e',
                  'run e2e',
                  'flaky-e2e',
                  'e2e-tests',
                  'e2e-next',
                  'slow-e2e',
                  'e2e-failure',
                  'e2e-success',
                  'run e2e extended test suite',
                  'e2e changes',
                  'selenium',
                  'selenium issue',
                  'selenium4',
                  'kind/cypress',
                  'feature-selenium-grid',
                  'feature-visual-regression-testing',
                  'visual-regression-testing',
                  'test type: blocks-e2e',
                  'test type: core-e2e',
                  'metric: stale flaky e2e test report',
                  'metric: flaky e2e test'
                  ]
    users_ga = [
                'github-actions[bot]',
                'jenkins-bot',
                'jenkins',
                'jenkins-bot',
                'jenkins-ci',
                'ci-bot',
                'travis-ci',
                'travis-bot',
                'circleci-bot',
                'circleci',
                'travis',
                '[bot]'
    ]

    open = 74298
    open_e2e = 313
    closed= 1346749
    closed_e2e= 5840
    open_ga = 69
    open_ga_e2e= 41
    closed_ga = 6924
    closed_ga_e2e= 5840
    in_closed_ga = 572
    in_closed_ga_e2e = 84
    take_closed_ga = 6352
    take_closed_ga_e2e = 52
    '''

    # Impostazioni della richiesta
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    
    '''
    @staticmethod
    def get_all_issues(state,repo_name):
        issues_url = f"https://api.github.com/repos/{repo_name}/issues"
        all_issues = []
        page = 1
        while True:
            print(f'page:{page}')
            params = {
                "state": state,  # Stato delle issue
                "per_page": 100,  # Numero di issue per pagina (max 100)
                "page": page  # Numero della pagina
            }
            response = requests.get(issues_url, headers=TotalIssue.headers, params=params)

            if response.status_code == 200:
                issues = response.json()
                if not issues:  # Se non ci sono più issue, interrompi il ciclo
                    break
                all_issues.extend(issues)  # Aggiungi le issue trovate alla lista
                page += 1  # Passa alla pagina successiva
            else:
                print(f"Errore {response.status_code}: {response.json()['message']}")
                break

        return all_issues
        '''

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
    '''
    @staticmethod
    def get_all_issues(state,repo_name):

        url = "https://api.github.com/graphql"
        token = TotalIssue.token.split(" ")[1]  # Remove 'Bearer '
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        owner, repo = repo_name.split('/')
        issues = []
        has_next_page = True
        after = None

        while has_next_page:
            query = """
            query($owner: String!, $repo: String!, $state: [IssueState!], $after: String) {
              repository(owner: $owner, name: $repo) {
                issues(first: 100, states: $state, after: $after) {
                  pageInfo {
                    hasNextPage
                    endCursor
                  }
                  nodes {
                    id
                    number
                    title
                    body
                    state
                    stateReason
                    createdAt
                    closedAt
                    author { login }
                    labels(first: 20) { nodes { name } }
                    timelineItems(last: 1, itemTypes: [CLOSED_EVENT]) {
                      nodes {
                        ... on ClosedEvent {
                          actor {
                            login
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
            """
            variables = {
                "owner": owner,
                "repo": repo,
                "state": [state.upper()],
                "after": after
            }
            response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)
            data = response.json()
            if 'errors' in data:
                raise Exception(f"Error fetching issues for {repo_name}: {data['errors']}")
            
            repo_data = data['data']['repository']['issues']
            for issue in repo_data['nodes']:
                # Post-process to match REST API output
                # Map 'author' to 'user', 'stateReason' to 'state_reason', 'labels' to flat list
                if 'author' in issue:
                    issue['user'] = {'login': issue['author']['login']} if issue['author'] else None
                    del issue['author']
                if 'stateReason' in issue:
                    issue['state_reason'] = issue['stateReason']
                    del issue['stateReason']
                if 'labels' in issue and 'nodes' in issue['labels']:
                    # REST API returns a list of dicts with 'name' key
                    issue['labels'] = [{'name': l['name']} for l in issue['labels']['nodes']]
                # Map closed_by from timelineItems
                closed_by_login = None
                timeline = issue.get('timelineItems', {}).get('nodes', [])
                if timeline and timeline[0] and 'actor' in timeline[0] and timeline[0]['actor']:
                    closed_by_login = {'login': timeline[0]['actor']['login']}
                issue['closed_by'] = closed_by_login
                if 'timelineItems' in issue:
                    del issue['timelineItems']
                if 'createdAt' in issue:
                    issue['created_at'] = issue['createdAt']
                    del issue['createdAt']
                if 'closedAt' in issue:
                    issue['closed_at'] = issue['closedAt']
                    del issue['closedAt']
                issues.append(issue)
            has_next_page = repo_data['pageInfo']['hasNextPage']
            after = repo_data['pageInfo']['endCursor']
        return issues
    '''

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
        
        #github_actions_issues = TotalIssue.check_github_actions_issues(open_issues,closed_issues)
        #return len(open_issues),len(closed_issues),len(github_actions_issues['open']),len(github_actions_issues['closed'])
    '''
    @staticmethod
    def check_github_actions_issues(open_issues, closed_issues):
        # Carica le issue dal file JSON
        #with open(json_file_path, 'r') as json_file:
        #    all_issues = json.load(json_file)

        github_actions_issues = {
            "open": [],
            "closed": []
        }

        # Scorri le issue aperte e verifica se l'autore è "github-actions[bot]"
        for issue in open_issues:
            if issue is not None and issue.get('user', {}).get('login') == 'github-actions[bot]':
                github_actions_issues['open'].append(issue)

        # Scorri le issue chiuse e verifica se l'autore è "github-actions[bot]"
        for issue in closed_issues:
            if issue is not None and issue.get('user', {}).get('login') == 'github-actions[bot]':
                github_actions_issues['closed'].append(issue)

        return github_actions_issues
    '''
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
        #output_file = f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/totalIssueAnalysis/total_issues_analysis_2.xlsx'
        #df_res = pd.read_excel(output_file)
        #df = pd.read_excel(f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ2/rq2_data.xlsx')
        missed_repo = TotalIssue.get_repo_with_number_of_test_lower_than_n(30)
        for repo in missed_repo[start:end]:
            repo_name = repo.repository_name
            num_of_test= repo.number_of_tests
            print(f' sto processando {repo_name} con num_of_test:{num_of_test}')
            save_file_issue = num_of_test>0
            #open_issues,closed_issues,action_open_issue,action_closed_issues=
            TotalIssue.get_number_of_open_closed_issues(repo_name,save_file_issue)
            #print(f'open-issues:{open_issues} - closed-issues:{closed_issues} act-open: {action_open_issue} act-close :{action_closed_issues}')
            #new_row = {
            #    'repo': repo_name,
            #    'open' : open_issues,
            #    'closed': closed_issues,
            #    'act-open':action_open_issue,
            #    'act-closed': action_closed_issues
            #}
            #print(new_row)
            #new_row_df = pd.DataFrame([new_row])
            #df_res = pd.concat([df_res, new_row_df], ignore_index=True)
            #df_res.to_excel(output_file,index=False)

    '''
    @staticmethod
    def save_rq2_new_total_issues():
        rq2_data = pd.read_excel(f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ2/rq2_data_updated.xlsx')
        total_1 = pd.read_excel(f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/totalIssueAnalysis/total_issues_analysis_1.xlsx')
        total_2 = pd.read_excel(f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/totalIssueAnalysis/total_issues_analysis_2.xlsx')
        flag_found = 0
        for index,row in rq2_data.iterrows():
            repo_name = row.iloc[0]
            total_issue = row.iloc[11]
            total_issue_ga = row.iloc[12]
            if pd.isna(total_issue):
                for index_1,row_1 in total_1.iterrows():
                    repo_name1= row_1.iloc[0]
                    if repo_name1==repo_name:
                        open_issue = row_1.iloc[1]
                        closed_issue= row_1.iloc[2]
                        open_ga = row_1.iloc[3]
                        closed_ga = row_1.iloc[4]
                        #print(f'1 {repo_name} - {open_issue}-  {closed_issue}')
                        if open_issue>0 or closed_issue > 0:
                            flag_found=1
                            rq2_data.at[index,'totalIssue'] = open_issue+closed_issue
                            rq2_data.at[index,'totalIssue_noGA'] = (open_issue+closed_issue)-(open_ga+closed_ga)
                            break
                if flag_found ==0:
                    for index_2,row_2 in total_2.iterrows():
                        repo_name2 = row_2.iloc[0]
                        if repo_name2 == repo_name:
                            open_issue = row_2.iloc[1]
                            closed_issue = row_2.iloc[2]
                            open_ga = row_2.iloc[3]
                            closed_ga = row_2.iloc[4]
                            #print(f'2 {repo_name} - {open_issue}-  {closed_issue}')
                            if open_issue > 0 or closed_issue > 0:
                                rq2_data.at[index, 'totalIssue'] = open_issue + closed_issue
                                rq2_data.at[index, 'totalIssue_noGA'] = (open_issue + closed_issue) - (open_ga + closed_ga)
                                flag_found =1
                                break
                if flag_found == 0:
                    print(f'{repo_name} con indice {index} non trovata!')
                flag_found=0
        # Salva il DataFrame aggiornato
        rq2_data.to_excel('/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ2/rq2_data_updated.xlsx',index=False)



    @staticmethod
    def is_automated(issue,flag):
        if flag == 0:
            user = issue.get('user', {}).get('login')
        else:
            user=issue
        for user_ga in TotalIssue.users_ga:
            if user == user_ga or user_ga in user:
                return True
        return False

    @staticmethod
    def get_ga_issues(open_issues):
        # Scorri le issue aperte e verifica se l'autore è "github-actions[bot]"
        list = []
        count=0
        for issue in open_issues:
            if issue is not None:
                if TotalIssue.is_automated(issue,0):
                    list.append(issue)
        return list

    @staticmethod
    def find_users_by_issues(issues):
        list = set()
        for issue in issues:
            if issue is not None: #and issue.get('user', {}).get('login') == 'github-actions[bot]':
                #count+=1
                list.add(issue.get('user',{}).get('login'))
        return list


    @staticmethod
    def count_ga_closed_issues(closed_issues):
        inactivity_closed_ga_issues = []
        taken_by_other_closed_ga_issues =[]
        for issue in closed_issues:
            # Verifica che l'issue sia stata chiusa da github-actions[bot]
            if issue is not None:
                closed_by = issue.get('closed_by',{})
                if closed_by is not None:
                    closed_by_user =closed_by.get('login')
                    if TotalIssue.is_automated(closed_by_user, 1):
                        inactivity_closed_ga_issues.append(issue)
                    else:
                        taken_by_other_closed_ga_issues.append(issue)
                else:
                    taken_by_other_closed_ga_issues.append(issue)
        return inactivity_closed_ga_issues, taken_by_other_closed_ga_issues

    @staticmethod
    def return_num_e2e_labels_into_issues_list(issues):
        matched_issues = set()  # Set per evitare conteggi doppi
        for issue in issues:
            if issue is not None:
                labels = issue.get('labels', [])
                for label in labels:
                    label_name = label.get('name')  # Extract the 'name' from each label
                    if label_name:  # Ensure the name exists
                        for e2e_label in TotalIssue.labels_e2e:
                            if label_name==e2e_label or e2e_label in label_name:
                                matched_issues.add(issue['id'])
                                break

        return len(matched_issues)

    @staticmethod
    def gets_e2e_flaky_slow_labels(issue):
        e2e = []
        flaky_slow = []
        if issue is not None:
            labels = issue.get('labels',[])
            for label in labels:
                label_name = label.get('name')  # Extract the 'name' from each label
                if label_name:  # Ensure the name exists
                    for e2e_label in TotalIssue.labels_e2e:
                        if label_name == e2e_label or e2e_label in label_name:
                            e2e.append(label_name)
                            if e2e_label in TotalIssue.flaky_slow_labels:
                                flaky_slow.append(label_name)
        return e2e,flaky_slow



    @staticmethod
    def list_all_users():
        results = []
        directory_path = '/home/sergio/Scaricati/RQ2/RQ2/issues_analysis'
        df = pd.read_excel('/home/sergio/Scaricati/RQ2/RQ2/githubactions_issues_analysis.xlsx')
        repos = df['repo'].unique()
        for name in repos:  # You can adjust this to process more repositories
            # print(name)
            if os.path.exists(directory_path + '/' + name + '_all_issues.json'):
                file_path = os.path.join(directory_path, name + '_all_issues.json')
                with open(file_path, 'r', encoding='utf-8') as json_file:
                    try:
                        data = json.load(json_file)

                        open_issues = data['open']
                        closed_issues = data['closed']
                        users = TotalIssue.find_users_by_issues(open_issues+closed_issues)

                        results.append([name,users])

                    except json.JSONDecodeError as e:
                        print(f"Errore nel parsing del file {name}: {e}")

        df_res = pd.DataFrame(results,columns=['repo', 'users'])
        df_res.to_excel(f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/totalIssueAnalysis/issues_users.xlsx',
            index=False)



    @staticmethod
    def filter_no_ga_issues(all_issues,ga_issues):
        list = []
        for issue in all_issues:
            id = issue['id']
            found = 0
            for ga_issue in ga_issues:
                id_ga = ga_issue['id']
                if id_ga == id:
                    found=1
            if found == 0:
                list.append(issue)
        return list

    @staticmethod
    def analyze_flaky_slow_issue(issues):
        matched_issues = set()  # Set per evitare conteggi doppi
        for issue in issues:
            if issue is not None:
                labels = issue.get('labels', [])
                for label in labels:
                    label_name = label.get('name')  # Extract the 'name' from each label
                    if label_name:  # Ensure the name exists
                        for e2e_label in TotalIssue.flaky_slow_labels:
                            if label_name == e2e_label or e2e_label in label_name:
                                matched_issues.add(issue['id'])
                                break
        return matched_issues

    @staticmethod
    def flaky_slow_analysis():
        results = []
        directory_path = '/home/sergio/Scaricati/RQ2/RQ2/issues_analysis'
        df = pd.read_excel('/home/sergio/Scaricati/RQ2/RQ2/githubactions_issues_analysis.xlsx')
        repos = df['repo'].unique()
        for name in repos:  # You can adjust this to process more repositories
            #print(name)
            if os.path.exists(directory_path+'/'+name+'_all_issues.json'):
                file_path = os.path.join(directory_path, name+'_all_issues.json')
                with open(file_path, 'r', encoding='utf-8') as json_file:
                    try:
                        data = json.load(json_file)

                        open_issues=  data['open']
                        open_ga = TotalIssue.get_ga_issues(open_issues)

                        flaky_slow_issues_open = TotalIssue.analyze_flaky_slow_issue(open_issues)
                        flaky_slow_issue_open_ga = TotalIssue.analyze_flaky_slow_issue(open_ga)

                        closed_issues = data['closed']
                        closed_ga = TotalIssue.get_ga_issues(closed_issues)

                        flaky_slow_issues_closed = TotalIssue.analyze_flaky_slow_issue(closed_issues)
                        flaky_slow_issues_closed_ga = TotalIssue.analyze_flaky_slow_issue(closed_ga)

                        closed_not_ga = TotalIssue.filter_no_ga_issues(data['closed'],closed_ga)
                        inactivity_closed_ga_issues, taken_by_other_closed_ga_issues = TotalIssue.count_ga_closed_issues(closed_ga)
                        inactivity_closed_not_ga_issues, taken_by_other__not_ga_closed_issues = TotalIssue.count_ga_closed_issues(closed_not_ga)

                        flaky_slow_issues_closed_ga_in = TotalIssue.analyze_flaky_slow_issue(inactivity_closed_ga_issues)
                        flaky_slow_issues_closed_not_ga_in = TotalIssue.analyze_flaky_slow_issue(inactivity_closed_not_ga_issues)
                        flaky_slow_issues_closed_ga_taken = TotalIssue.analyze_flaky_slow_issue(taken_by_other_closed_ga_issues)
                        flaky_slow_issues_closed_not_ga_taken = TotalIssue.analyze_flaky_slow_issue(taken_by_other__not_ga_closed_issues)

                        results.append([
                            name,
                            len(open_issues),
                            len(open_ga),
                            len(flaky_slow_issues_open),
                            len(flaky_slow_issue_open_ga),
                            len(closed_issues),
                            len(closed_ga),
                            len(flaky_slow_issues_closed),
                            len(flaky_slow_issues_closed_ga),
                            len(inactivity_closed_ga_issues),
                            len(inactivity_closed_not_ga_issues),
                            len(flaky_slow_issues_closed_ga_in),
                            len(flaky_slow_issues_closed_not_ga_in),
                            len(taken_by_other_closed_ga_issues),
                            len(taken_by_other__not_ga_closed_issues),
                            len(flaky_slow_issues_closed_ga_taken),
                            len(flaky_slow_issues_closed_not_ga_taken)
                        ])

                    except json.JSONDecodeError as e:
                        print(f"Errore nel parsing del file {name}: {e}")
        df_res = pd.DataFrame(results,
                              columns=['nane',
                                       'open_issues',
                                        'open_ga',
                                        'flaky_slow_issues_open',
                                        'flaky_slow_issue_open_ga',
                                        'closed_issues',
                                        'closed_ga',
                                        'flaky_slow_issues_closed',
                                        'flaky_slow_issues_closed_ga',
                                        'inactivity_closed_ga_issues',
                                        'inactivity_closed_not_ga_issues',
                                        'flaky_slow_issues_closed_ga_in',
                                        'flaky_slow_issues_closed_not_ga_in',
                                        'taken_by_other_closed_ga_issues',
                                        'taken_by_other__not_ga_closed_issues',
                                        'flaky_slow_issues_closed_ga_taken',
                                        'flaky_slow_issues_closed_not_ga_taken'])
        df_res.to_excel(
            f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/totalIssueAnalysis/flaky_slow_issues_analysis.xlsx',
            index=False)

    @staticmethod
    def load_json_files_from_directory():
        results = []
        directory_path = '/home/sergio/Scaricati/RQ2/RQ2/issues_analysis'
        df = pd.read_excel('/home/sergio/Scaricati/RQ2/RQ2/githubactions_issues_analysis.xlsx')
        repos = df['repo'].unique()
        for name in repos:  # You can adjust this to process more repositories
            #print(name)
            if os.path.exists(directory_path+'/'+name+'_all_issues.json'):
                file_path = os.path.join(directory_path, name+'_all_issues.json')
                with open(file_path, 'r', encoding='utf-8') as json_file:
                    try:
                        data = json.load(json_file)

                        open_issues = data['open']
                        num_open_issues_e2e = TotalIssue.return_num_e2e_labels_into_issues_list(open_issues)

                        closed_issues = data['closed']
                        num_closed_issues_e2e =TotalIssue.return_num_e2e_labels_into_issues_list(closed_issues)

                        open_ga = TotalIssue.get_ga_issues(data['open'])
                        num_open_ga_e2e = TotalIssue.return_num_e2e_labels_into_issues_list(open_ga)

                        closed_ga = TotalIssue.get_ga_issues(data['closed'])
                        num_closed_ga_e2e =TotalIssue.return_num_e2e_labels_into_issues_list(closed_ga)

                        closed_not_ga = TotalIssue.filter_no_ga_issues(data['closed'],closed_ga)
                        num_closed_not_ga_e2e = TotalIssue.return_num_e2e_labels_into_issues_list(closed_not_ga)

                        inactivity_closed_not_ga_issues, taken_by_other__not_ga_closed_issues = TotalIssue.count_ga_closed_issues(closed_not_ga)
                        num_inactvity_not_ga_e2e = TotalIssue.return_num_e2e_labels_into_issues_list(inactivity_closed_not_ga_issues)
                        num_taken_by_other_not_ga_e2e = TotalIssue.return_num_e2e_labels_into_issues_list(taken_by_other__not_ga_closed_issues)

                        inactivity_closed_ga_issues, taken_by_other_closed_ga_issues = TotalIssue.count_ga_closed_issues(closed_ga)
                        num_inactvity_e2e = TotalIssue.return_num_e2e_labels_into_issues_list(inactivity_closed_ga_issues)
                        num_taken_by_other_e2e = TotalIssue.return_num_e2e_labels_into_issues_list(taken_by_other_closed_ga_issues)



                        results.append([
                                name,
                                len(closed_issues),
                                num_closed_issues_e2e,
                                len(closed_ga),
                                num_closed_ga_e2e,
                                len(closed_not_ga),
                                num_closed_not_ga_e2e,
                                len(inactivity_closed_ga_issues),
                                num_inactvity_e2e,
                                len(taken_by_other_closed_ga_issues),
                                num_taken_by_other_e2e,
                                len(inactivity_closed_not_ga_issues),
                                num_inactvity_not_ga_e2e,
                                len(taken_by_other__not_ga_closed_issues),
                                num_taken_by_other_not_ga_e2e
                        ])


                    except json.JSONDecodeError as e:
                        print(f"Errore nel parsing del file {name}: {e}")


        #df_res = pd.DataFrame(results,columns=['repo','open','open_e2e','closed','closed_e2e','open_GA','open_GA_e2e','closed_GA','closed_GA_e2e','inactivity_closed_GA','inactivity_closed_GA_e2e','taken_closed_GA','taken_closed_GA_e2e'])
        #df_res.to_excel(f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/totalIssueAnalysis/githubactions_issues_analysis_IST_allCI_new.xlsx',index=False)

        df_res = pd.DataFrame(results,columns=['nane','closed','closed_e2e','closed_GA','closed_GA_e2e','closed_not_GA','closed_not_GA_e2e','inactivity_closed_GA','inactivity_closed_GA_e2e','taken_closed_GA','taken_closed_GA_e2e','inactivity_closed_not_GA','inactivity_closed_not_GA_e2e','taken_closed_not_GA','taken_closed_not_GA_e2e'])
        df_res.to_excel(f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/totalIssueAnalysis/githubactions_closed_issues_analysis_IST_allCI_new.xlsx',index=False)

    @staticmethod
    def missed_repo(directory_path):
        df_repos = pd.read_csv(f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ1/repo_to_analyze.csv')
        for index,row in df_repos.iterrows():
            name = row.iloc[0]
            if not (os.path.exists(directory_path + '/' + name + '_all_issues.json')):
                print(f'sto analizzando {name}')
                TotalIssue.get_number_of_open_closed_issues(name.replace('_','/',1),1)



    @staticmethod
    def fill_total_issue_perf():
        file_path ='/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/ICSME/RQ2/rq2_data.xlsx'
        df = pd.read_excel(file_path)
        for index,row in df.iterrows():
            repo_name = row["repoName"]
            if pd.isna(df.at[index,"totalIssue"]):
                open,closed,open_ga,closed_ga=TotalIssue.get_number_of_open_closed_issues(repo_name,False)
                df.at[index,"totalIssue"] = open+closed
                df.at[index,"totalIssue_noGA"] = open_ga+closed_ga
                df.to_excel(file_path, index=False, engine="openpyxl")
                print(f"{repo_name} - added!")



    @staticmethod
    def get_list_labels(issues):
        label_names = set()  # Use a set to avoid duplicates
        for issue in issues:
            if issue is not None:
                labels = issue.get('labels', [])
                for label in labels:
                    label_name = label.get('name')  # Extract the 'name' from each label
                    if label_name:  # Ensure the name exists
                        label_names.add(label_name)  # Add to the set (no duplicates)
        return list(label_names)  # Convert the set back to a list before returning


    @staticmethod
    def get_all_labels_from_issues():
        results_labels = []
        directory_path = '/home/sergio/Scaricati/RQ2/RQ2/issues_analysis'
        df = pd.read_excel('/home/sergio/Scaricati/RQ2/RQ2/githubactions_issues_analysis.xlsx')
        repos = df['repo'].unique()
        total_issues= 0
        for name in repos:  # You can adjust this to process more repositories
            if os.path.exists(os.path.join(directory_path, f'{name}_all_issues.json')):
                file_path = os.path.join(directory_path, f'{name}_all_issues.json')

                with open(file_path, 'r', encoding='utf-8') as json_file:
                    data = json.load(json_file)
                    open_issues = data['open']
                    closed_issues = data['closed']
                    total_issues+=len(open_issues)
                    total_issues+=len(closed_issues)
                    
                    labels = TotalIssue.get_list_labels(open_issues + closed_issues)

                    # Remove duplicates by converting to a set and then back to a list
                    unique_labels = list(set(labels))
                    results_labels.append([name, unique_labels])
                    
        print(f'total issues : {total_issues}')
        #df_result = pd.DataFrame(results_labels, columns=['repo', 'labels'])
        #df_result.to_excel('issue_labels.xlsx', index=False)


    @staticmethod
    def venn_open_issue_label():

        # Dati
        only_e2e = 272  # Open E2E issues che non sono GA-generated
        only_ga = 38  # Open GA issues che non sono E2E
        both_e2e_ga = 41  # Open issues che sono sia E2E che GA-generated
        total_open_issues = 74298  # Totale open issues

        # Crea il diagramma di Venn
        venn_data = {
            '10': only_e2e,  # Solo E2E
            '01': only_ga,  # Solo GA
            '11': both_e2e_ga,  # Entrambi E2E e GA
        }

        # Crea la figura per il grafico
        plt.figure(figsize=(8, 6))

        # Diagramma di Venn per E2E e GA
        venn = venn2(subsets=venn_data, set_labels=('E2E Testing', 'GitHub Actions'))

        # Personalizza l'aspetto dei cerchi
        venn.get_label_by_id('10').set_fontsize(12)
        venn.get_label_by_id('01').set_fontsize(12)
        venn.get_label_by_id('11').set_fontsize(12)

        # Impostiamo il colore dell'insieme di tutte le open issues (aggiungendo un cerchio esterno)
        # Aggiungiamo l'insieme 'open' come contorno
        plt.text(0.5, 0.5, f'Total Open Issues\n{total_open_issues}', horizontalalignment='center',
                 verticalalignment='center', fontsize=12,
                 bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=1'))

        # Titolo del grafico
        plt.title('Open Issues: E2E Testing vs. GitHub Actions (con Totale Open Issues)')

        # Mostra il diagramma
        plt.show()


    @staticmethod
    def issues_analysis(repo,issues,type):
        res = []
        for issue in issues:
            if issue is not None:
                repository = repo
                id = issue['id']
                type = type
                title= issue.get('title')
                body = issue.get('body')
                labels = TotalIssue.get_list_labels([issue])
                is_ga = TotalIssue.is_automated(issue,0)
                is_web_gui, is_flaky_slow = TotalIssue.gets_e2e_flaky_slow_labels(issue)
                status = ''
                if type =='closed':
                    closed_by = issue.get('closed_by', {})
                    if closed_by is not None:
                        closed_by_user =closed_by.get('login')
                        if TotalIssue.is_automated(closed_by_user, 1):
                            status = 'inactivity'
                        else:
                            status ='taken'
                res.append([
                    repository,
                    id,
                    type,
                    title,
                    body,
                    labels,
                    is_ga,
                    is_web_gui,
                    is_flaky_slow,
                    status
                ])
            else:
                print('Issue None')
        return res


    @staticmethod
    def replace_illegal_chars(s):
        if isinstance(s, str):
            return re.sub(r'[^\x20-\x7E]', '?', s)
        return s

    @staticmethod
    def ceate_all_issue_analisys_life():
        results = []
        directory_path = '/home/sergio/Scaricati/RQ2/RQ2/issues_analysis'
        df = pd.read_excel('/home/sergio/Scaricati/RQ2/RQ2/githubactions_issues_analysis.xlsx')
        repos = df['repo'].unique()
        for name in repos:  # You can adjust this to process more repositories
            # print(name)
            if os.path.exists(directory_path + '/' + name + '_all_issues.json'):
                file_path = os.path.join(directory_path, name + '_all_issues.json')
                with open(file_path, 'r', encoding='utf-8') as json_file:
                    try:
                        data = json.load(json_file)
                        open_issues = data['open']
                        closed_issues = data['closed']
                        results+=TotalIssue.issues_analysis(name, open_issues,'open')
                        results+= TotalIssue.issues_analysis(name, closed_issues,'closed')
                    except json.JSONDecodeError as e:
                        print(f"Errore nel parsing del file {name}: {e}")


        df_res = pd.DataFrame(results, columns=['repository', 'id', 'type', 'title', 'body',
                                                        'labels', 'is_ga', 'is_web_gui',
                                                        'is_flaky_slow', 'status'])

        # Salva il DataFrame come file JSON array
        df_res.to_json(
            '/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/totalIssueAnalysis/all_issues_deep_analysis_part.json',
            orient='records',  # Ogni riga è un oggetto JSON
            force_ascii=False  # Per mantenere eventuali caratteri speciali
        )

    '''

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
    TotalIssue.run_parallel_analysis()