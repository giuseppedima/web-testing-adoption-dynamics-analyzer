from pathlib import Path
import pandas as pd
import json
from environment import PATH_TO_ISSUES_DOWNLOAD
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 16, 'svg.fonttype': 'none'})  # Increase global font size and make the text selectable

class CommitStatisticsGenerator:
    @staticmethod
    def get_all_commits_count():
        previous_adoption_commits = 0
        adoption_commits = 0
        adoption = Path(__file__).resolve().parent.parent / 'resources' / 'adoption_commits.json'
        with open(adoption, "r", encoding="utf-8") as f:
            data = json.load(f)
            for repo in data:
                previous_adoption_commits += len(data[repo]['previous_commits'])
            adoption_commits = len(data)


        previous_migration_commits = 0
        migration_commits = 0
        migration = Path(__file__).resolve().parent.parent / 'resources' / 'migration_commits.json'
        with open(migration, "r", encoding="utf-8") as f:
            data = json.load(f)
            for repo in data:
                for migration in data[repo]:
                    previous_migration_commits += len(migration['previous_commits'])
                    migration_commits += 1

        return previous_adoption_commits, adoption_commits, previous_migration_commits, migration_commits

    @staticmethod
    def get_commits_after_filtering_count():
        adoption =  Path(__file__).resolve().parent.parent / 'resources' / 'adoption_commits_filtered.xlsx'
        df = pd.read_excel(adoption)

        migration =  Path(__file__).resolve().parent.parent / 'resources' / 'migration_commits_filtered.xlsx'
        df_migration = pd.read_excel(migration)

        return len(df) - 1, len(df_migration) - 1
    
    @staticmethod
    def get_commits_after_labeling_count():
        adoption =  Path(__file__).resolve().parent.parent / 'resources' / 'adoption_commits_filtered.xlsx'
        df = pd.read_excel(adoption)
        df = df[df.iloc[:, 5].astype(str).str.lower() == 'useful']

        migration =  Path(__file__).resolve().parent.parent / 'resources' / 'migration_commits_filtered.xlsx'
        df_migration = pd.read_excel(migration)
        df_migration = df_migration[df_migration.iloc[:, 6].astype(str).str.lower() == 'useful']

        return len(df), len(df_migration)


    @staticmethod
    def generate_side_by_side_pie_charts():
        # previous_adoption_commits, adoption_commits, previous_migration_commits, migration_commits = CommitStatisticsGenerator.get_all_commits_count()
        # values1 = [adoption_commits+previous_adoption_commits, migration_commits+previous_migration_commits]
        values1 = [5032, 1716]

        # adoption_commits_after_filtering, migration_commits_after_filtering = CommitStatisticsGenerator.get_commits_after_filtering_count()
        # values2 = [adoption_commits_after_filtering, migration_commits_after_filtering]
        values2 = [587, 337]

        # adoption_commits_after_labeling, migration_commits_after_labeling = CommitStatisticsGenerator.get_commits_after_labeling_count()
        # values3 = [adoption_commits_after_labeling, migration_commits_after_labeling]
        values3 = [9, 1]

        colors = ['#1f77b4', '#ff7f0e']

        fig, axes = plt.subplots(1, 3, figsize=(10, 6))

        wedges1, _, _ = axes[0].pie(
            values1,
            labels=None,
            colors=colors,
            autopct=lambda p: '{:.0f}'.format(p * sum(values1) / 100) if p > 0 else '',
            startangle=90,
            counterclock=False
        )
        axes[0].set_title("Before Filtering")

        wedges2, _, _ = axes[1].pie(
            values2,
            labels=None,
            colors=colors,
            autopct=lambda p: '{:.0f}'.format(p * sum(values2) / 100) if p > 0 else '',
            startangle=90,
            counterclock=False
        )
        axes[1].set_title("After Filtering")

        wedges3, _, _ = axes[2].pie(
            values3,
            labels=None,
            colors=colors,
            autopct=lambda p: '{:.0f}'.format(p * sum(values3) / 100) if p > 0 else '',
            startangle=90,
            counterclock=False
        )
        axes[2].set_title("After Labeling")

        # Legenda unica
        fig.legend(
            [wedges1[0], wedges1[1]],
            ['Adoption Commits', 'Migration Commits'],
            loc='center',
            ncol=2,
            bbox_to_anchor=(0.5, 0.2)
        )

        plt.tight_layout()
        plt.savefig(Path(__file__).parent / 'commits_statistics.svg', bbox_inches='tight')


if __name__ == "__main__":
    previous_adoption_commits, adoption_commits, previous_migration_commits, migration_commits = CommitStatisticsGenerator.get_all_commits_count()
    print("Total adoption commits: %d" % adoption_commits)
    print("Additional adoption commits count: %d" % previous_adoption_commits)
    print("Total migration commits count: %d" % migration_commits)
    print("Additional migration commits count: %d" % previous_migration_commits)
    adoption_commits_after_filtering, migration_commits_after_filtering = CommitStatisticsGenerator.get_commits_after_filtering_count()
    print("Adoption commits after filtering: %d" % adoption_commits_after_filtering)
    print("Migration commits after filtering: %d" % migration_commits_after_filtering)
    adoption_commits_after_labeling, migration_commits_after_labeling = CommitStatisticsGenerator.get_commits_after_labeling_count()
    print("Adoption commits after labeling: %d" % adoption_commits_after_labeling)
    print("Migration commits after labeling: %d" % migration_commits_after_labeling)
    CommitStatisticsGenerator.generate_side_by_side_pie_charts()