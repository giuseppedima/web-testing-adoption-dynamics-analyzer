<!---
### E2E-Miner

E2E-Miner is a tool for researchers that automates the mining of Repository Software.

## Tool Description

This miner uses a DataSet with git Repositories informations, it finds all the dependencies and reports the usage of web framework and testing tool E2E.

The AnalyzerController class is responsible for managing all phases of the analysis: it use threads to analyze multiple repositories at once. 
The Cloner Class downloads the Repository. 
DependencyFileFinder finds all the dependency file with the use of abstract classes so you can add other languages to analyze. 
For each file, there is another abstract class that finds dependencies. 
The .txt files contains all the framework web declaration, you can remove and add additional frameworks. 
At the end, there is a list of classes whose task is to research testing E2E tools.

## How to Run the Project

Download a file JSON from this site: https://seart-ghs.si.usi.ch/ . the file JSON will contains all information about more than 1,000,000 Repositories, and activate JSONtoDBconverter.py script, specifying the path to the file.
Il will create a RepositoryDataset.db with all informations in.

After that, you have to define the characteristic of Repositories to analyze in main.py and then run the scripts.

To see the DataSet with all you information install DB browser for SQLite (https://sqlitebrowser.org/).
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