from Dataset.DBconnector import Base, engine
from Dataset.Repository import RepositoryModel, NonTrivialRepo, GUITestingTestDetails, PerformanceTestingTestDetails, GUITestingRepoDetails
from Dataset.Commit import CommitModel
from Dataset.Issue import IssueModel
from Dataset.Transition import TransitionModel
from Dataset.Taxonomy import TaxonomyModel
from sqlalchemy.orm import sessionmaker

import pandas as pd

from pathlib import Path

from datetime import datetime

class ExcelToDBConverter():
    session = None
    path_to_extension = Path(__file__).resolve().parent.parent / 'resources' / 'extension'

    def __init__(self):
        # Ensure the database tables are created
        Base.metadata.create_all(engine)
        # Create a new session
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def insert_taxonomy_data(self):
        df = pd.read_excel(self.path_to_extension / 'taxonomy.xlsx')

        for _, row in df.iterrows():
            taxonomy = TaxonomyModel(category=row['category'], description=row['description'])
            self.session.add(taxonomy)
        self.session.commit()

    def insert_commits(self, file_name):
        df = pd.read_excel(self.path_to_extension / file_name)

        for _, row in df.iterrows():
            if row['label'] == 'useful':
                # Ensure repository_name matches case-insensitively with existing repositories
                repo = self.session.query(RepositoryModel).filter(
                    RepositoryModel.name.ilike(row['repo'])
                ).first()
                if repo:
                    commit = CommitModel(
                        hash=row['hash'],
                        repository_name=repo.name,  # Use the actual name from DB
                        date=pd.to_datetime(row['date'], utc=True), # Ensure date is timezone-aware
                        message=row['message'],
                        transition_id=row.get('transition_id', None)
                    )
                    self.session.add(commit)
                else:
                    print(f"Repository {row['repo']} not found in the database. Skipping commit {row['hash']}.")
        self.session.commit()
    
    def insert_issues(self, file_name):
        df = pd.read_excel(self.path_to_extension / file_name)

        for _, row in df.iterrows():
            if 'label' not in row or row['label'] == 'useful':
                # Ensure repository_name matches case-insensitively with existing repositories
                repo = self.session.query(RepositoryModel).filter(
                    RepositoryModel.name.ilike(row['repo'])
                ).first()
                if repo:
                    # Check if the issue already exists to avoid duplicates
                    existing_issue = self.session.query(IssueModel).filter_by(number=row['number'], repository_name=repo.name).first()
                    if existing_issue:
                        print(f"Issue {row['number']} already exists in the database. Skipping.")
                    else:
                        issue = IssueModel(
                            number=row['number'],
                            repository_name=repo.name,
                            title=row['title'],
                            body=row['body'],
                            created_at=pd.to_datetime(row['created_at'], utc=True),
                            updated_at=pd.to_datetime(row['updated_at'], utc=True),
                            closed_at=pd.to_datetime(row['closed_at'], utc=True) if pd.notna(row['closed_at']) else None,
                            transition_id=row.get('transition_id', None)
                        )
                        self.session.add(issue)
                else:
                    print(f"Repository {row['repo']} not found in the database. Skipping issue {row['number']}.")
        self.session.commit()
    
    def insert_transitions(self, sheet_name):
        df = pd.read_excel(self.path_to_extension / 'transitions.xlsx', sheet_name, dtype={'commits': str, 'issues': str})

        for _, row in df.iterrows():
            # Ensure repository_name matches case-insensitively with existing repositories
            repo = self.session.query(RepositoryModel).filter(
                RepositoryModel.name.ilike(row['repo'])
            ).first()
            if repo:
                transition = TransitionModel(
                    repository_name=repo.name,
                    source_framework=row['source_framework'] if 'source_framework' in row else None,
                    target_framework=row['target_framework'],
                    summary=row['summary'],
                )
                self.session.add(transition)

                for category in row['categories'].split(','):
                    taxonomy = self.session.query(TaxonomyModel).filter(
                        TaxonomyModel.category.ilike(category.strip())
                    ).first()
                    if taxonomy:
                        transition.taxonomies.append(taxonomy)
                    else:
                        print(f"Taxonomy {category.strip()} not found in the database. Skipping.")
                
                if pd.notna(row['commits']):
                    for commit_hash in row['commits'].split(','):
                        commit = self.session.query(CommitModel).filter_by(
                            hash=commit_hash.strip(),
                            repository_name=repo.name
                        ).first()
                        if commit:
                            transition.commits.append(commit)
                        else:
                            print(f"Commit {commit_hash.strip()} not found in the database. Skipping.")
                    
                if pd.notna(row['issues']):
                    for issue_number in row['issues'].split(','):
                        issue = self.session.query(IssueModel).filter_by(
                            number=int(issue_number.strip()),
                            repository_name=repo.name
                        ).first()
                        if issue:
                            transition.issues.append(issue)
                        else:
                            print(f"Issue {issue_number.strip()} not found in the database. Skipping.")
            else:
                print(f"Repository {row['repo']} not found in the database. Skipping transition.")
        self.session.commit()


if __name__ == "__main__":
    converter = ExcelToDBConverter()


    converter.insert_taxonomy_data()
    print("Taxonomy data inserted successfully.")
    
    converter.insert_commits("adoption_commits_filtered.xlsx")
    converter.insert_commits("migration_commits_filtered.xlsx")
    print("commits inserted successfully.")

    converter.insert_issues("adoption_issues_filtered.xlsx")
    converter.insert_issues("migration_issues_filtered.xlsx")
    converter.insert_issues("issues_missed_in_filter.xlsx")
    print("issues inserted successfully.")

    converter.insert_transitions("adoption")
    converter.insert_transitions("migration")
    print("Transitions inserted successfully.")


