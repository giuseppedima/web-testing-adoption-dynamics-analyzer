# Web Testing Adoption Dynamics Analyzer

This repository contains the source code and methodology developed for the thesis: **"A Software Framework to Investigate End-to-End Web Testing Adoption Dynamics"**.

The project implements a systematic workflow to investigate the motivations behind adoption and migration of web GUI testing frameworks (Selenium, Cypress, Puppeteer, Playwright) in open-source projects.

## 📖 Project Overview

This software was designed to enrich [E2EGit dataset](https://zenodo.org/records/14988988) with qualitative insights on *why* projects choose to adopt or migrate between web testing frameworks.
Starting from a set of manually identified adoption and migration events (provided as input Excel files), the framework automates the retrieval of historical context to reconstruct the decision-making process.

The methodology, described in the thesis, follows a mixed-methods approach:
1.  **Automated Context Extraction**: Retrieving specific commit sequences and issue discussions surrounding the known transition dates.
2.  **Noise Reduction**: Applying a specialized keyword-based taxonomy to filter relevant content.
3.  **Manual Classification**: Classifying the motivations through a custom "Human-in-the-loop" GUI.
4.  **Taxonomic Analysis**: Categorizing the rationale (e.g., Developer Experience & Usability, Performance & Efficiency) to characterize the transition landscape.

## 📂 Project Structure

The codebase is organized into modular components reflecting the research phases:

| Module | Description |
| :--- | :--- |
| **[`01_data_mining`](./01_data_mining)** | **Retrieval & Filtering**: Processes the input Excel files to fetch and filter commits/issues from GitHub/Git. |
| **[`02_manual_labeling`](./02_manual_labeling)** | **Validation Interface**: A Flask Web GUI for the manual review of the filtered candidates. |
| **[`03_db_integration`](./03_db_integration)** | **Data Enrichment**: Integrates the classified qualitative data back into the E2EGit dataset schema. |
| **[`04_statistical_analysis`](./04_statistical_analysis)** | **Characterization**: Generates the empirical statistics and visualizations presented in the results. |
| **[`core`](./core)** | **Shared Logic**: Database models, configuration, and utility functions. |
| **[`resources`](./resources)** | **Data Storage**: Contains the **Input Excel Files** (events), intermediate JSONs, and the SQLite database. |

## ⚠️ Execution Rule

**IMPORTANT:** This project is structured as a Python package.
**All commands must be executed from the ROOT directory** using the `-m` flag.

* ✅ Correct: `python -m module_name.cli ...`
* ❌ Incorrect: `cd module_name && python cli.py`

For more details, refer to each module's help command:

```bash
python -m module_name.cli --help
```

## 🚀 Setup
### 1. (optional) Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```
### 2. Install the required dependencies:
```bash
pip install -r requirements.txt
```
### 3. Configure Environment:
Create a .env file in resources/ (use [`resources/.env.example`](./resources/.env.example) as a template) to configure the DB path and GitHub Token.

## ⚙️ Workflow

To replicate the study, ensure the input files (`creation-adoption-gui.xlsx`, `migration_analysis.xlsx`) are present in the `resources/` folder.

### 1. Data Retrieval
The system reads the input Excel files containing the transition events. 
#### 1.1. Retrieve transition-related commits and 10 preceding commits:
```bash
python -m 01_data_mining.cli --task retrieve --target commit --type adoption
python -m 01_data_mining.cli --task retrieve --target commit --type migration
```
#### 1.2. Retrieve all issues of the repositories involved in transition events:
```bash
python -m 01_data_mining.cli --task retrieve --target issue
```
If you need to download issues only for a specific repository, add the `--repo owner/repo` argument
```bash
python -m 01_data_mining.cli --task retrieve --target issue --repo owner/repo
```

### 2. Data Filtering

#### 2.1. Filter commits by keywords:
```bash
python -m 01_data_mining.cli --task filter --target commit --type adoption
python -m 01_data_mining.cli --task filter --target commit --type migration
```
#### 2.2. Filter issues by time window (10 days before transition) and keywords:
```bash
python -m 01_data_mining.cli --task filter --target issue --type adoption
python -m 01_data_mining.cli --task filter --target issue --type migration
```

### 3. Manual Review
#### 3.1. Convert filtered JSONs to Excel for manual labeling:
```bash
python -m 02_manual_labeling.cli --task convert --target commit --type adoption
python -m 02_manual_labeling.cli --task convert --target commit --type migration
python -m 02_manual_labeling.cli --task convert --target issue --type adoption
python -m 02_manual_labeling.cli --task convert --target issue --type migration
```
#### 3.2. Launch the Flask Web Application:
Load the manual labeling interface to classify the filtered candidates.
```bash
python -m 02_manual_labeling.cli --task server --target commit --type adoption
python -m 02_manual_labeling.cli --task server --target commit --type migration
python -m 02_manual_labeling.cli --task server --target issue --type adoption
python -m 02_manual_labeling.cli --task server --target issue --type migration
```

### 4. Data Refinement
After manual review define the taxonomic labels in the Excel files and create a new Excel file containing transition events linked to their motivations and associated issue number/commit hash. You can find the files we used for the thesis in the [`resources`](./resources) folder.

### 5. Database Integration
Integrate the classified data back into the E2EGit dataset SQLite database.
```bash
python -m 03_db_integration.cli
```

### 6. Statistical Analysis
Generate the statistics and visualizations for the final analysis.
```bash
python -m 04_statistical_analysis.cli
```

## 🎓 Reference
If you use this tool, please cite:

```bibtex
@mastersthesis{dimartino2025software,
  author  = {Giuseppe Di Martino},
  title   = {A Software Framework to Investigate End-to-End Web Testing Adoption Dynamics},
  school  = {University of Naples Federico II},
  year    = {2025},
  type    = {Bachelor's Thesis},
  note    = {B.Sc. Thesis in Computer Science}
}
```
