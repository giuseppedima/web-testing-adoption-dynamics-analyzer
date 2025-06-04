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

