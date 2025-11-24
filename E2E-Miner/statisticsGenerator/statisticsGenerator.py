from pathlib import Path
import pandas as pd
import json

import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 16, 'svg.fonttype': 'none'})  # Increase global font size and make the text selectable
import numpy as np
import matplotlib.patches as patches
import networkx as nx

from Dataset.DBconnector import engine
from sqlalchemy.orm import sessionmaker

import plotly.graph_objects as go

class StatisticsGenerator:
    @staticmethod
    def get_all_repositories_count():
        adoption = Path(__file__).resolve().parent.parent / 'resources' / 'creation-adoption-gui.xlsx'
        df = pd.read_excel(adoption)
        repos = [str(repo).lower() for repo in df.iloc[1:, 2].tolist()]
        
        
        migration = Path(__file__).resolve().parent.parent / 'resources' / 'migration_analysis.xlsx'
        df = pd.read_excel(migration)
        repos.extend([str(repo).lower() for repo in df.iloc[1:, 0].tolist()])

        return len(set(repos))

    @staticmethod
    def adoption_counts_by_framework():
        Session = sessionmaker(bind=engine)
        session = Session()
        results = session.execute("""
            SELECT target_framework, count(*) from transition WHERE source_framework IS NULL GROUP BY target_framework
        """).fetchall()
        session.close()
        
        #create horizontal bar chart showing the counts for each framework
        frameworks = [row[0] for row in results]
        counts = [row[1] for row in results]
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.barh(frameworks, counts, color='skyblue')
        ax.set_xlabel("Number of adoptions")
        for bar in bars:
            width = bar.get_width()
            ax.annotate('{}'.format(width),
                        xy=(width, bar.get_y() + bar.get_height() / 2),
                        xytext=(3, 0),  # 3 points horizontal offset
                        textcoords="offset points",
                        ha='left', va='center')
        plt.tight_layout()
        plt.savefig(Path(__file__).parent / 'adoption_by_framework.svg', bbox_inches='tight')

        # Save the figure
        plt.tight_layout()
        plt.savefig(Path(__file__).parent / 'migration_flows.svg', bbox_inches='tight')

    @staticmethod
    def migration_directed_graph():
        import math
        Session = sessionmaker(bind=engine)
        session = Session()
        results = session.execute("""
            SELECT source_framework, target_framework, count(*) as count
            FROM transition
            WHERE source_framework IS NOT NULL
            GROUP BY source_framework, target_framework
        """).fetchall()
        session.close()

        G = nx.DiGraph()
        for src, tgt, cnt in results:
            G.add_edge(src, tgt, weight=cnt)

        # Nodi centrali
        manual_pos = {
            'playwright': (-0.4, 0),
            'cypress': (0.4, 0),
        }
        # Nodi attorno (ordine circolare)
        circle_nodes = [
            'nightmare',
            'postman',
            'protractor',
            'puppeteer',
            'react testing library',
            'selenium',
            'testcafe',
            'uvu'
        ]
        radius = 1
        label_angles = {}
        for i, node in enumerate(circle_nodes):
            angle = 2 * math.pi * i / len(circle_nodes)
            manual_pos[node] = (radius * math.cos(angle), radius * math.sin(angle))
            label_angles[node] = angle

        # Eventuali altri nodi non previsti
        for node in G.nodes:
            if node not in manual_pos:
                manual_pos[node] = (radius * 1.2, 0)

        plt.figure(figsize=(14, 10))
        edge_weights = [G[u][v]['weight'] for u, v in G.edges()]
        nx.draw_networkx_nodes(G, manual_pos, node_size=6000, node_color='skyblue')

        # Etichette nodi (tutte orizzontali e centrate nei nodi, con \n al posto dello spazio)
        for node, (x, y) in manual_pos.items():
            label = node.replace(' ', '\n')
            plt.text(
                x, y, label, fontsize=14, ha='center', va='center',
                color='black', zorder=10
            )

        # Disegna archi con frecce ben visibili e curvati per chiarezza direzione
        nx.draw_networkx_edges(
            G, manual_pos, arrowstyle='->', arrowsize=24,
            width=[max(w/5, 2) for w in edge_weights], edge_color='black',
            connectionstyle='arc3',
            min_source_margin=40,   # aumenta il margine per nodi grandi
            min_target_margin=40
        )
        nx.draw_networkx_edge_labels(
            G, manual_pos, edge_labels={(u, v): G[u][v]['weight'] for u, v in G.edges()},
            font_size=12, label_pos=0.6, rotate=True, bbox=dict(facecolor='white', edgecolor='none', pad=0.5)
        )

        plt.axis('off')
        plt.tight_layout()
        plt.savefig(Path(__file__).parent / "migration_directed_graph.svg", bbox_inches='tight')
        plt.close()
        print("Directed graph saved to migration_directed_graph.svg")

    @staticmethod
    def migration_sankey_diagram():
        
        Session = sessionmaker(bind=engine)
        session = Session()
        results = session.execute("""
            SELECT source_framework, target_framework, count(*) as count
            FROM transition
            WHERE source_framework IS NOT NULL
            GROUP BY source_framework, target_framework
        """).fetchall()
        session.close()

        # Prepara i dati per il Sankey
        sources = []
        targets = []
        values = []
        
        # Create distinct sets for source and target frameworks
        source_frameworks = set()
        target_frameworks = set()
        for src, tgt, cnt in results:
            source_frameworks.add(src)
            target_frameworks.add(tgt)
        
        # Create separate nodes: first all sources, then all targets
        # Frameworks appearing as both source and target will have two different nodes
        framework_list = []
        framework_to_idx = {}
        
        # Add first all the source frameworks
        num_sources = 0
        for fw in sorted(source_frameworks):
            idx = len(framework_list)
            framework_list.append(fw)
            framework_to_idx[('source', fw)] = idx
            num_sources += 1
        
        # Then add all the target frameworks
        for fw in sorted(target_frameworks):
            idx = len(framework_list)
            framework_list.append(fw)
            framework_to_idx[('target', fw)] = idx
        
        # Populate the lists for the Sankey diagram
        for src, tgt, cnt in results:
            sources.append(framework_to_idx[('source', src)])
            targets.append(framework_to_idx[('target', tgt)])
            values.append(cnt)
        
        # Compute node labels with outgoing and incoming counts for sources and targets
        outgoing = {}
        incoming = {}
        for src, tgt, cnt in results:
            outgoing[src] = outgoing.get(src, 0) + cnt
            incoming[tgt] = incoming.get(tgt, 0) + cnt
        
        # Create node labels with counts
        node_labels = []
        for i, label in enumerate(framework_list):
            if i < num_sources:  # Source node
                count = outgoing.get(label, 0)
                node_labels.append(f"{label}\n({count})")
            else:  # Target node
                count = incoming.get(label, 0)
                node_labels.append(f"{label}\n({count})")
        
        # Create the Sankey diagram
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=node_labels,
                color="skyblue"
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                color="rgba(135, 206, 250, 0.4)"
            )
        )])
        
        fig.update_layout(
            font=dict(family="DejaVu Sans", size=16), # same font as matplotlib figures
            height=600,
            width=600,
            margin=dict(l=20, r=20, t=40, b=20),
            annotations=[
                dict(
                    x=0,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    text='<b>Sources</b>',
                    showarrow=False,
                    font=dict(family="DejaVu Sans", size=16)
                ),
                dict(
                    x=1,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    text='<b>Targets</b>',
                    showarrow=False,
                    font=dict(family="DejaVu Sans", size=16)
                )
            ]
        )
        
        # Save as SVG
        svg_path = Path(__file__).parent / "migration_sankey_diagram.svg"
        fig.write_image(str(svg_path))
        print(f"Sankey diagram saved to {svg_path}")

    @staticmethod
    def motivation_category_distribution():
        Session = sessionmaker(bind=engine)
        session = Session()

        results = session.execute("""
            SELECT category, count(*) as transitions_count FROM taxonomy LEFT JOIN taxonomy_transition on taxonomy.id = taxonomy_transition.taxonomy_id GROUP by taxonomy_transition.taxonomy_id
        """).fetchall()
        session.close()
        sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
        categories = [row[0].replace(' ', '\n') for row in sorted_results]
        counts = [row[1] for row in sorted_results]
        fig, ax = plt.subplots(figsize=(10,8))
        wedges, texts, autotexts = ax.pie(counts, labels=categories, autopct='%1.1f%%', startangle=90, counterclock=False, pctdistance=0.7, labeldistance=1.3)
        
        # Center align all text
        for text in texts:
            text.set_horizontalalignment('center')
        for autotext in autotexts:
            autotext.set_horizontalalignment('center')
        
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.tight_layout()
        plt.savefig(Path(__file__).parent / 'motivation_category_distribution.svg', bbox_inches='tight')  
        plt.close()

    @staticmethod
    def grouped_bar_chart_motivation_category():
        Session = sessionmaker(bind=engine)
        session = Session()
        results = session.execute("""
            SELECT 
                taxonomy.category, 
                COALESCE(adoption.transition_count, 0) AS adoption_cnt,
                COALESCE(migration.transition_count, 0) AS migration_cnt
            FROM taxonomy
            LEFT JOIN (
                SELECT taxonomy_id, COUNT(*) AS transition_count
                FROM taxonomy_transition
                JOIN transition ON transition.id = taxonomy_transition.transition_id
                WHERE transition.source_framework IS NULL
                GROUP BY taxonomy_id
            ) adoption ON taxonomy.id = adoption.taxonomy_id
            LEFT JOIN (
                SELECT taxonomy_id, COUNT(*) AS transition_count
                FROM taxonomy_transition
                JOIN transition ON transition.id = taxonomy_transition.transition_id
                WHERE transition.source_framework IS NOT NULL
                GROUP BY taxonomy_id
            ) migration ON taxonomy.id = migration.taxonomy_id
        """).fetchall()
        session.close()
        categories = [row[0].replace('&', '&\n') for row in reversed(results)]
        adoption_counts = [row[1] for row in reversed(results)]
        migration_counts = [row[2] for row in reversed(results)]

        y = np.arange(len(categories))
        height = 0.35 # the height of the bars

        fig, ax = plt.subplots(figsize=(10, 8))

        bars1 = ax.barh(y + height/2, adoption_counts, height, label='Adoption', color='#1f77b4')
        bars2 = ax.barh(y - height/2, migration_counts, height, label='Migration', color='#ff7f0e')

        ax.set_ylabel('Motivation Category')
        ax.set_xlabel('Number of Transitions')
        ax.set_yticks(y)
        ax.set_yticklabels(categories, rotation=0, ha='right')
        ax.set_ylim(-0.5, len(categories) - 0.5)
        ax.set_xlim(right=10)  # Set right limit to avoid collision with right border
        ax.legend()

        # Annotazioni a destra delle barre
        for bar in bars1 + bars2:
            width = bar.get_width()
            if width > 0:
                ax.annotate('{}'.format(width),
                            xy=(width, bar.get_y() + bar.get_height() / 2),
                            xytext=(3, 0),
                            textcoords="offset points",
                            ha='left', va='center')

        plt.tight_layout()
        plt.savefig(Path(__file__).parent / 'adoption_vs_migration_motivation_distribution.svg', bbox_inches='tight')
        plt.close()

    @staticmethod
    def playwright_migration_sources():
        Session = sessionmaker(bind=engine)
        session = Session()
        results = session.execute("""
            SELECT source_framework, count(*) as count
            FROM transition
            WHERE target_framework = 'playwright' AND source_framework IS NOT NULL
            GROUP BY source_framework
            ORDER BY count DESC
        """).fetchall()
        session.close()
        sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
        sources = [row[0].replace(' ', '\n') for row in sorted_results]
        counts = [row[1] for row in sorted_results]
        fig, ax = plt.subplots(figsize=(8,8))
        wedges, texts, autotexts = ax.pie(counts, labels=sources, autopct='%1.1f%%', startangle=90, counterclock=False, pctdistance=0.7, labeldistance=1.2)
        
        # Center align all text
        for text in texts:
            text.set_horizontalalignment('center')
        for autotext in autotexts:
            autotext.set_horizontalalignment('center')
        
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.tight_layout()
        plt.savefig(Path(__file__).parent / 'playwright_migration_sources.svg', bbox_inches='tight')
        plt.close()


    @staticmethod
    def generate_side_by_side_pie_charts():
        Session = sessionmaker(bind=engine)
        session = Session()
        adoption_frameworks = session.execute("""
            SELECT target_framework, count(*) as count
            FROM transition
            WHERE source_framework IS NULL
            GROUP BY target_framework
            ORDER BY count DESC
        """).fetchall()
        migration_frameworks = session.execute("""
            SELECT target_framework, count(*) as count
            FROM transition
            WHERE source_framework IS NOT NULL
            GROUP BY target_framework
            ORDER BY count DESC
        """).fetchall()
        session.close()

        # Prepare data for adoption
        adoption_frameworks_clean = [row[0] for row in adoption_frameworks]
        adoption_counts = [row[1] for row in adoption_frameworks]
        adoption_total = sum(adoption_counts)
        
        # Prepare data for migration
        migration_frameworks_clean = [row[0] for row in migration_frameworks]
        migration_counts = [row[1] for row in migration_frameworks]
        migration_total = sum(migration_counts)

        # Create side by side pie charts
        fig, axes = plt.subplots(1, 2, figsize=(10, 6))

        # Adoption pie chart
        wedges1, texts1 = axes[0].pie(
            adoption_counts,
            labels=None,
            startangle=90,
            counterclock=False
        )
        axes[0].set_title("Adoption Distribution", fontsize=18)
        
        # Custom labels for adoption
        for i, (wedge, count, framework) in enumerate(zip(wedges1, adoption_counts, adoption_frameworks_clean)):
            angle = (wedge.theta2 + wedge.theta1) / 2
            x = np.cos(np.deg2rad(angle))
            y = np.sin(np.deg2rad(angle))

            framework_label = framework.replace(' ', '\n')
            percent = count / adoption_total * 100
            
            if framework_label == 'selenium':
                # Label fuori dal cerchio (solo nome)
                axes[0].text(x * 1.6, y * 1.05, framework_label, ha='center', va='center', fontsize=14)
                # Numeri dentro il cerchio
                label = f"{count}/{adoption_total}\n{percent:.1f}%"
                axes[0].text(x * 0.7, y * 0.7, label, ha='center', va='center', fontsize=14)
            elif framework_label == 'puppeteer':
                # Label fuori dal cerchio (solo nome)
                axes[0].text(x * 1.1, y * 1.1, framework_label, ha='center', va='center', fontsize=14)
                # Numeri dentro il cerchio
                label = f"{count}/{adoption_total}\n{percent:.1f}%"
                axes[0].text(x * 0.86, y * 0.86, label, ha='center', va='center', fontsize=14)
            else:
                label = f"{framework_label}\n{count}/{adoption_total}\n{percent:.1f}%"
                axes[0].text(x * 0.6, y * 0.6, label, ha='center', va='center', fontsize=14)

        # Migration pie chart
        wedges2, texts2 = axes[1].pie(
            migration_counts,
            labels=None,
            startangle=90,
            counterclock=False
        )
        axes[1].set_title("Migration Distribution", fontsize=18)
        
        # Custom labels for migration
        for i, (wedge, count, framework) in enumerate(zip(wedges2, migration_counts, migration_frameworks_clean)):
            angle = (wedge.theta2 + wedge.theta1) / 2
            x = np.cos(np.deg2rad(angle)) * 0.6
            y = np.sin(np.deg2rad(angle)) * 0.6
            percent = count / migration_total * 100
            framework_label = framework.replace(' ', '\n')
            label = f"{framework_label}\n{count}/{migration_total}\n{percent:.1f}%"
            axes[1].text(x, y, label, ha='center', va='center', fontsize=14)

        # Equal aspect ratio ensures that pie is drawn as a circle
        axes[0].axis('equal')
        axes[1].axis('equal')

        plt.tight_layout()
        plt.savefig(Path(__file__).parent / 'adoption_vs_migration_distribution.svg', bbox_inches='tight')
        plt.close()
        print("Side by side pie charts saved to adoption_vs_migration_distribution.svg")

    @staticmethod
    def target_framework_by_language():
        Session = sessionmaker(bind=engine)
        session = Session()
        results = session.execute("""
            SELECT 
                repository.main_language, 
                transition.target_framework, 
                count(*) as count
            FROM transition
            JOIN repository ON transition.repository_name = repository.name
            WHERE repository.main_language IS NOT NULL
            GROUP BY repository.main_language, transition.target_framework
            ORDER BY repository.main_language, count DESC
        """).fetchall()
        session.close()

        # Prepare data structure
        data_dict = {}
        for lang, framework, count in results:
            if lang not in data_dict:
                data_dict[lang] = {}
            data_dict[lang][framework] = count

        # Get all unique frameworks and languages
        all_frameworks = sorted(set(framework for _, framework, _ in results))
        all_languages = sorted(data_dict.keys())

        # Sort languages by total number of transitions (ascending for horizontal bars)
        language_totals = [(lang, sum(data_dict[lang].values())) for lang in all_languages]
        language_totals.sort(key=lambda x: x[1], reverse=False)
        
        # Use all languages (ascending order, so highest appears at top)
        languages_final = [lang for lang, _ in language_totals]
        framework_data = {fw: [] for fw in all_frameworks}

        for lang in languages_final:
            for fw in all_frameworks:
                framework_data[fw].append(data_dict[lang].get(fw, 0))

        # Create grouped bar chart (horizontal)
        y = np.arange(len(languages_final))
        height = 0.8 / len(all_frameworks)  # Height of bars
        
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Create bars for each framework
        colors = plt.cm.tab10(np.linspace(0, 1, len(all_frameworks)))
        for i, (fw, color) in enumerate(zip(all_frameworks, colors)):
            offset = height * (i - len(all_frameworks) / 2 + 0.5)
            bars = ax.barh(y + offset, framework_data[fw], height, label=fw, color=color)
            
            # Add value labels at the end of bars
            for bar in bars:
                width = bar.get_width()
                if width > 0:
                    ax.annotate('{}'.format(int(width)),
                               xy=(width, bar.get_y() + bar.get_height() / 2.),
                               xytext=(3, 0),
                               textcoords='offset points',
                               ha='left', va='center', fontsize=12)

        ax.set_ylabel('Main Repository Language', fontsize=16)
        ax.set_xlabel('Number of Transitions', fontsize=16)
        # ax.set_title('Distribution of Target Framework by Main Repository Language', fontsize=18)
        ax.set_yticks(y)
        ax.set_yticklabels(languages_final)
        ax.legend(title='Target Framework', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(axis='x', alpha=0.3)

        plt.tight_layout()
        plt.savefig(Path(__file__).parent / 'target_framework_by_language.svg', bbox_inches='tight')
        plt.close()
        print("Target framework by language chart saved to target_framework_by_language.svg")

    @staticmethod
    def transitions_timeline_scatter():
        Session = sessionmaker(bind=engine)
        session = Session()
        results = session.execute("""
            SELECT 
                t.repository_name,
                t.type,
                t.source_framework,
                t.target_framework,
                MIN(events.event_date) AS data_effettiva
            FROM transition t
            LEFT JOIN (
                SELECT transition_id, date AS event_date FROM "commit"
                UNION ALL
                SELECT transition_id, created_at AS event_date FROM issue
            ) events ON t.id = events.transition_id
            GROUP BY 
                t.id, 
                t.repository_name, 
                t.type, 
                t.source_framework, 
                t.target_framework;
        """).fetchall()
        session.close()

        # Prepare data for plotting
        adoption_times = []
        adoption_frameworks = []
        migration_times = []
        migration_frameworks = []

        for repo, trans_type, source_fw, target_fw, date in results:
            if date is None:
                continue
            
            # Calculate precise time position (year + month fraction)
            if hasattr(date, 'year'):
                year = date.year
                month = date.month if hasattr(date, 'month') else 1
                time_position = year + (month - 1) / 12.0
            else:
                # If it's a string, try to parse it
                date_str = str(date)
                year = int(date_str[:4])
                try:
                    month = int(date_str[5:7])
                    time_position = year + (month - 1) / 12.0
                except:
                    time_position = year
            
            framework = target_fw
            
            if source_fw is None:  # Adoption
                adoption_times.append(time_position)
                adoption_frameworks.append(framework)
            else:  # Migration
                migration_times.append(time_position)
                migration_frameworks.append(framework)

        # Get all unique frameworks and sort them
        all_frameworks = sorted(set(adoption_frameworks + migration_frameworks))
        framework_to_y = {fw: i for i, fw in enumerate(all_frameworks)}

        # Convert framework names to y positions with small jitter to avoid overlap
        np.random.seed(10)  # For reproducibility
        adoption_y = [framework_to_y[fw] + np.random.uniform(-0.15, 0.15) for fw in adoption_frameworks]
        migration_y = [framework_to_y[fw] + np.random.uniform(-0.15, 0.15) for fw in migration_frameworks]

        # Create scatter plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot adoptions and migrations with specified colors
        ax.scatter(adoption_times, adoption_y, c='#1f77b4', label='Adoption', s=100, edgecolors='black', linewidths=0.5)
        ax.scatter(migration_times, migration_y, c='#ff7f0e', label='Migration', s=100, edgecolors='black', linewidths=0.5)

        # Set labels and title
        ax.set_xlabel('Year', fontsize=16)
        ax.set_ylabel('Target Framework', fontsize=16)
        ax.set_yticks(range(len(all_frameworks)))
        ax.set_yticklabels(all_frameworks)
        
        # Set x-axis to show all years with step of 1
        if adoption_times or migration_times:
            all_times = adoption_times + migration_times
            min_year = int(min(all_times))
            max_year = int(max(all_times)) + 1
            ax.set_xticks(range(min_year, max_year + 1))
        
        ax.legend(fontsize=14)
        ax.grid(axis='x', alpha=0.3)

        plt.tight_layout()
        plt.savefig(Path(__file__).parent / 'transitions_timeline_scatter.svg', bbox_inches='tight')
        plt.close()
        print("Transitions timeline scatter plot saved to transitions_timeline_scatter.svg")

if __name__ == "__main__":
    # print("Repositories count: %d" % StatisticsGenerator.get_all_repositories_count())
    # StatisticsGenerator.adoption_counts_by_framework()
    # StatisticsGenerator.migration_directed_graph()
    # StatisticsGenerator.migration_sankey_diagram()
    # StatisticsGenerator.motivation_category_distribution()
    # StatisticsGenerator.grouped_bar_chart_motivation_category()
    # StatisticsGenerator.playwright_migration_sources()
    # StatisticsGenerator.generate_side_by_side_pie_charts()
    # StatisticsGenerator.target_framework_by_language()
    StatisticsGenerator.transitions_timeline_scatter()