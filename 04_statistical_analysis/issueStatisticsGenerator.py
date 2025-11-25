from pathlib import Path
import pandas as pd
import json
from core.config import PATH_TO_ISSUES_DOWNLOAD, RESOURCES_DIR, ROOT_DIR

import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 16, 'svg.fonttype': 'none'})  # Increase global font size and make the text selectable
import numpy as np
import matplotlib.patches as patches

class IssueStatisticsGenerator:
    @staticmethod
    def get_all_repositories_count():
        adoption = RESOURCES_DIR / 'creation-adoption-gui.xlsx'
        df = pd.read_excel(adoption)
        repos = [str(repo).lower() for repo in df.iloc[1:, 2].tolist()]
        
        
        migration = RESOURCES_DIR / 'migration_analysis.xlsx'
        df = pd.read_excel(migration)
        repos.extend([str(repo).lower() for repo in df.iloc[1:, 0].tolist()])

        return len(set(repos))

    @staticmethod
    def get_issues_count():
        open_issues = 0
        closed_issues = 0
        for file_path in (Path(PATH_TO_ISSUES_DOWNLOAD) / 'all_issues').glob("*_all_issues.json"):
            with open(file_path, "r", encoding="utf-8") as f:
                issues = json.load(f)
                open_issues += len(issues.get('open', []))
                closed_issues += len(issues.get('closed', []))
        return open_issues, closed_issues

    @staticmethod
    def get_issues_after_filtering_count():
        adoption =  RESOURCES_DIR / 'adoption_issues_filtered.xlsx'
        df = pd.read_excel(adoption)

        migration =  RESOURCES_DIR / 'migration_issues_filtered.xlsx'
        df_migration = pd.read_excel(migration)

        return len(df) - 1, len(df_migration) - 1
    
    @staticmethod
    def get_issues_after_labeling_count():
        adoption =  RESOURCES_DIR / 'adoption_issues_filtered.xlsx'
        df = pd.read_excel(adoption)
        df = df[df.iloc[:, 11].astype(str).str.lower() == 'useful']

        migration =  RESOURCES_DIR / 'migration_issues_filtered.xlsx'
        df_migration = pd.read_excel(migration)
        df_migration = df_migration[df_migration.iloc[:, 12].astype(str).str.lower() == 'useful']

        return len(df), len(df_migration)
    
    @staticmethod
    def generate_bar_chart_issues():

        # Calculate the required values
        total_issues = sum(IssueStatisticsGenerator.get_issues_count())
        adoption_issues_after_filtering, migration_issues_after_filtering = IssueStatisticsGenerator.get_issues_after_filtering_count()
        adoption_issues_after_labeling, migration_issues_after_labeling = IssueStatisticsGenerator.get_issues_after_labeling_count()

        labels = [
            "Total Issues",
            "Filtered Issues (Adoption)",
            "Filtered Issues (Migration)",
            "Useful Issues (Adoption)",
            "Useful Issues (Migration)"
        ]
        values = [
            total_issues,
            adoption_issues_after_filtering,
            migration_issues_after_filtering,
            adoption_issues_after_labeling,
            migration_issues_after_labeling
        ]

        fig5, ax5 = plt.subplots(figsize=(10, 6))
        bars = ax5.bar(labels, values, color=["gray", '#1f77b4', '#ff7f0e', '#1f77b4', '#ff7f0e'], width=0.6)

        ax5.set_ylabel("Number of issues")
        ax5.set_yscale('log')  # Use logarithmic scale
        ax5.set_ylim(top=10**7)  # Set upper limit to avoid collision with top border

        ax5.set_xticks(range(len(labels)))
        ax5.set_xticklabels(labels, rotation=30, ha='right')
        # ax5.set_title("Issues statistics (log scale)")
        # Add values above bars - adjust position for specific bars
        for i, bar in enumerate(bars):
            height = bar.get_height()
            if i == 0:  # Total Issues - centered above
                xytext = (0, 3)
                ha = 'center'
            elif i in [1, 3]:  # Adoption - top left
                xytext = (-bar.get_width() / 2 - 5, 3)
                ha = 'right'
            else:  # Migration - top right
                xytext = (bar.get_width() / 2 + 5, 3)
                ha = 'left'
            
            ax5.annotate('{:,}'.format(int(height)),
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=xytext,
                        textcoords="offset points",
                        ha=ha, va='bottom')
        plt.tight_layout()
        plt.savefig(ROOT_DIR / '04_statistical_analysis' / 'issues_statistics.svg')

    @staticmethod
    def create_filtering_funnel():

        values = [
            3369401, # IssueStatisticsGenerator.get_issues_count()[0] + IssueStatisticsGenerator.get_issues_count()[1],
            9290, # IssueStatisticsGenerator.get_issues_after_filtering_count()[0],
            4487, # IssueStatisticsGenerator.get_issues_after_filtering_count()[1],
            40,  # IssueStatisticsGenerator.get_issues_after_labeling_count()[0],
            25   # IssueStatisticsGenerator.get_issues_after_labeling_count()[1]
        ]

        stages = [
            'Total Issues',
            'Filter\n(Adoption)',
            'Filter\n(Migration)',
            'Manual Classification\n(Adoption)',
            'Manual Classification\n(Migration)'
        ]
        colors = ['gray', '#1f77b4', '#ff7f0e', '#1f77b4', '#ff7f0e']

        fig, ax = plt.subplots(figsize=(10, 6)) 

        max_width = 4  # Rettangoli più corti
        log_values = np.log10(np.array(values) + 1)
        max_log = np.log10(max(values) + 1)
        widths = (log_values / max_log) * max_width

        y_positions = [8, 6, 6, 4, 4]
        x_positions = [0, -1.5, 1.5, -1.5, 1.5]  # Più vicini

        for i, (stage, value, width, color, x_pos, y_pos) in enumerate(
            zip(stages, values, widths, colors, x_positions, y_positions)):

            rect = patches.Rectangle((x_pos - width/2, y_pos - 0.4), width, 0.8, 
                                linewidth=2, edgecolor='black', 
                                facecolor=color, alpha=0.7)
            ax.add_patch(rect)

            ax.text(x_pos, y_pos-0.25, f'{value:,}', 
                    fontsize=11, fontweight='bold', va='center', ha='center')

            ax.text(x_pos, y_pos+0.13, stage, fontsize=10, ha='center', va='center', 
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))

        # Linee di collegamento
        ax.plot([0, -1.5], [y_positions[0]-0.4, y_positions[1]+0.4], 'k--', alpha=0.5, linewidth=1)
        ax.plot([0, 1.5], [y_positions[0]-0.4, y_positions[2]+0.4], 'k--', alpha=0.5, linewidth=1)
        ax.plot([-1.5, -1.5], [y_positions[1]-0.4, y_positions[3]+0.4], 'k--', alpha=0.5, linewidth=1)
        ax.plot([1.5, 1.5], [y_positions[2]-0.4, y_positions[4]+0.4], 'k--', alpha=0.5, linewidth=1)

        ax.set_xlim(-2.9, 2.9)
        ax.set_ylim(3.5, 8.5)
        ax.set_aspect('equal')
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

        plt.savefig(ROOT_DIR / '04_statistical_analysis' / 'filtering_funnel.svg', bbox_inches='tight', pad_inches=0.05)



if __name__ == "__main__":
    open_issues, closed_issues = IssueStatisticsGenerator.get_issues_count()
    total_issues = open_issues + closed_issues
    print("Issues count: %d" % total_issues)
    print("Open issues count: %d" % open_issues)
    print("Closed issues count: %d" % closed_issues)
    adoption_issues_after_filtering, migration_issues_after_filtering = IssueStatisticsGenerator.get_issues_after_filtering_count()
    print("Adoption issues after filtering: %d" % adoption_issues_after_filtering)
    print("Migration issues after filtering: %d" % migration_issues_after_filtering)
    adoption_issues_after_labeling, migration_issues_after_labeling = IssueStatisticsGenerator.get_issues_after_labeling_count()
    print("Adoption issues after labeling: %d" % adoption_issues_after_labeling)
    print("Migration issues after labeling: %d" % migration_issues_after_labeling)
    IssueStatisticsGenerator.generate_bar_chart_issues()
    IssueStatisticsGenerator.create_filtering_funnel()
