<!---
TODO: update readme
-->
1. Download the dataset
```bash
wget https://zenodo.org/records/14988988/files/E2EGit.db -O resources/E2EGit.db
```
2. Create a .env file following the example in .env.example
```bash
cp resources/.env.example resources/.env
```
3. (optional, but recommended) Create a virtual environment
```bash
python3 -m venv .venv
```
and activate it, for example on linux
```bash
source .venv/bin/activate
```
When you are done, you can deactivate it with
```bash
deactivate
```
4. Install the dependencies
```bash
pip install -r requirements.txt
```
5. If you want to download issues run totalIssueAnalysis
```bash
python3 -u -m totalIssueAnalysis.totalIssueAnalysis >totalIssueAnalysis/log.log 2>&1
```
If you want to extract commits run
```bash
python3 -u -m CommitAnalyzer.adoptionCommitAnalyzer >CommitAnalyzer/adoptionCommitAnalyzer.log 2>&1
python3 -u -m CommitAnalyzer.migrationCommitAnalyzer >CommitAnalyzer/migrationCommitAnalyzer.log 2>&1
```
If you want to filter commits run
```bash
python3 -u -m CommitFilterer.commitFilterer >CommitFilterer/log.log 2>&1
```
If you want to filter issues run
```bash
python3 -u -m IssueFilterer.adoptionIssueFilterer >IssueFilterer/adoptionIssueFilterer.log 2>&1
python3 -u -m IssueFilterer.migrationIssueFilterer >IssueFilterer/migrationIssueFilterer.log 2>&1
```