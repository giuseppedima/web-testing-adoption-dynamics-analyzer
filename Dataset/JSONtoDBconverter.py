import json

from Dataset.Repository import Repository
#FILE SCARICATO DAL DATASET DEL GRUPPO SEART, SPECIFICA IL NOME QUI
json_file = "results.json" #SCARICATO DAL SITO: https://seart-ghs.si.usi.ch/

try:
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

except FileNotFoundError:
    raise FileNotFoundError("you inserted a non-existent file in the DataSet object")

for item in data['items']:
    languages = item["languages"]
    language_names = [language for language in languages.keys()]
    metrics_str = json.dumps(item['metrics'])

    repository = Repository(
        item.get('name', ''),
        item.get('isFork', False),
        item.get('commits', 0),
        item.get('branches', 0),
        item.get('releases', 0),
        item.get('forks', 0),
        item.get('mainLanguage', ''),
        item.get('defaultBranch', ''),
        item.get('license', ''),
        item.get('homepage', ''),
        item.get('watchers', 0),
        item.get('stargazers', 0),
        item.get('contributors', 0),
        item.get('size', 0),
        item.get('createdAt', ''),
        item.get('pushedAt', ''),
        item.get('updatedAt', ''),
        item.get('totalIssues', 0),
        item.get('openIssues', 0),
        item.get('totalPullRequests', 0),
        item.get('openPullRequests', 0),
        item.get('blankLines', 0),
        item.get('codeLines', 0),
        item.get('commentLines', 0),
        metrics_str,
        item.get('lastCommit', ''),
        item.get('lastCommitSHA', ''),
        item.get('hasWiki', False),
        item.get('isArchived', False),
        item.get('isDisabled', False),
        item.get('isLocked', False),
        language_names,
        item.get('labels', []),
        item.get('topics', [])
    )

    repository.add_repository_to_db()
