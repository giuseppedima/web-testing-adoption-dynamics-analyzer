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
        plt.savefig(Path(__file__).parent / 'adoption_by_framework.svg', bbox_inches='tight')  # Riduci il bianco

        # Save the figure
        plt.tight_layout()
        plt.savefig(Path(__file__).parent / 'migration_flows.svg', bbox_inches='tight')  # Riduci il bianco

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
    def motivation_category_distribution():
        Session = sessionmaker(bind=engine)
        session = Session()

        results = session.execute("""
            SELECT category, count(*) as transitions_count FROM taxonomy LEFT JOIN taxonomy_transition on taxonomy.id = taxonomy_transition.taxonomy_id GROUP by taxonomy_transition.taxonomy_id
        """).fetchall()
        session.close()
        categories = [row[0].replace('&', '&\n') for row in results]
        counts = [row[1] for row in results]
        #create pie chart
        fig, ax = plt.subplots(figsize=(12, 12))
        wedges, texts, autotexts = ax.pie(counts, labels=categories, autopct='%1.1f%%', startangle=140, textprops={'fontsize': 16})
        for text in texts:
            text.set_fontsize(16)
        for autotext in autotexts:
            autotext.set_fontsize(16)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.tight_layout()
        plt.savefig(Path(__file__).parent / 'motivation_category_distribution.svg', bbox_inches='tight')  # Riduci il bianco    
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
        categories = [row[0].replace('&', '&\n') for row in results]
        adoption_counts = [row[1] for row in results]
        migration_counts = [row[2] for row in results]

        x = np.arange(len(categories))
        width = 0.35  # larghezza delle barre
        spacing = 0.25  # spazio tra i gruppi

        fig, ax = plt.subplots(figsize=(14, 8))

        # Per aggiungere spazio tra i gruppi, creiamo nuovi indici con spazio extra
        indices = np.arange(len(categories)) * (1 + spacing)

        bars1 = ax.bar(indices - width/2, adoption_counts, width, label='Adoption', color='skyblue')
        bars2 = ax.bar(indices + width/2, migration_counts, width, label='Migration', color='orange')

        ax.set_xlabel('Motivation Category')
        ax.set_ylabel('Number of Transitions')
        ax.set_xticks(indices)
        ax.set_xticklabels(categories, rotation=30, ha='right')
        ax.legend()

        # Annotazioni sopra le barre
        for bar in bars1 + bars2:
            height = bar.get_height()
            if height > 0:
                ax.annotate('{}'.format(height),
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),  # 3 punti sopra la barra
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=12)

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

        frameworks = [row[0].replace(' ', '\n') for row in results]
        counts = [row[1] for row in results]
        total = sum(counts)

        fig, ax = plt.subplots(figsize=(12, 12))
        wedges, texts = ax.pie(
            counts, labels=None, startangle=140, textprops={'fontsize': 16},
            wedgeprops=dict(width=0.4)
        )
        # Etichette personalizzate all’interno delle fette (sull'anello)
        for i, (wedge, count, framework) in enumerate(zip(wedges, counts, frameworks)):
            angle = (wedge.theta2 + wedge.theta1) / 2
            r = 0.85  # raggio maggiore per stare sull'anello
            x = r * np.cos(np.deg2rad(angle))
            y = r * np.sin(np.deg2rad(angle))
            percent = count / total * 100
            label = f"{framework}\n{count}/{total}\n{percent:.1f}%"
            ax.text(x, y, label, ha='center', va='center', fontsize=16, color='black')

        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        fig.gca().add_artist(centre_circle)

        ax.axis('equal')
        plt.tight_layout()
        plt.savefig(Path(__file__).parent / 'playwright_migration_sources.svg', bbox_inches='tight')
    
    def adoption_donut_chart():
        Session = sessionmaker(bind=engine)
        session = Session()
        results = session.execute("""
            SELECT target_framework, count(*) as count
            FROM transition
            WHERE source_framework IS NULL
            GROUP BY target_framework
            ORDER BY count DESC
        """).fetchall()
        session.close()

        frameworks = [row[0].replace(' ', '\n') for row in results]
        counts = [row[1] for row in results]
        total = sum(counts)

        fig, ax = plt.subplots(figsize=(12, 12))
        wedges, texts = ax.pie(
            counts, labels=None, startangle=140, textprops={'fontsize': 16},
            wedgeprops=dict(width=0.4)
        )
        # Etichette personalizzate all’interno delle fette (sull'anello)
        for i, (wedge, count, framework) in enumerate(zip(wedges, counts, frameworks)):
            angle = (wedge.theta2 + wedge.theta1) / 2
            r = 0.85  # raggio maggiore per stare sull'anello
            x = r * np.cos(np.deg2rad(angle))
            y = r * np.sin(np.deg2rad(angle))
            percent = count / total * 100
            label = f"{framework}\n{count}/{total}\n{percent:.1f}%"
            ax.text(x, y, label, ha='center', va='center', fontsize=16, color='black')

        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        fig.gca().add_artist(centre_circle)

        ax.axis('equal')
        plt.tight_layout()
        plt.savefig(Path(__file__).parent / 'adoption_donut_chart.svg', bbox_inches='tight')
    
    def migration_donut_chart():
        Session = sessionmaker(bind=engine)
        session = Session()
        results = session.execute("""
            SELECT target_framework, count(*) as count
            FROM transition
            WHERE source_framework IS NOT NULL
            GROUP BY target_framework
            ORDER BY count DESC
        """).fetchall()
        session.close()

        frameworks = [row[0].replace(' ', '\n') for row in results]
        counts = [row[1] for row in results]
        total = sum(counts)

        fig, ax = plt.subplots(figsize=(12, 12))
        wedges, texts = ax.pie(
            counts, labels=None, startangle=140, textprops={'fontsize': 16},
            wedgeprops=dict(width=0.4)
        )
        # Etichette personalizzate all’interno delle fette (sull'anello)
        for i, (wedge, count, framework) in enumerate(zip(wedges, counts, frameworks)):
            angle = (wedge.theta2 + wedge.theta1) / 2
            r = 0.85  # raggio maggiore per stare sull'anello
            x = r * np.cos(np.deg2rad(angle))
            y = r * np.sin(np.deg2rad(angle))
            percent = count / total * 100
            label = f"{framework}\n{count}/{total}\n{percent:.1f}%"
            ax.text(x, y, label, ha='center', va='center', fontsize=16, color='black')

        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        fig.gca().add_artist(centre_circle)

        ax.axis('equal')
        plt.tight_layout()
        plt.savefig(Path(__file__).parent / 'migration_donut_chart.svg', bbox_inches='tight')

if __name__ == "__main__":
    # print("Repositories count: %d" % StatisticsGenerator.get_all_repositories_count())
    # StatisticsGenerator.adoption_counts_by_framework()
    # StatisticsGenerator.migration_directed_graph()
    # StatisticsGenerator.motivation_category_distribution()
    # StatisticsGenerator.grouped_bar_chart_motivation_category()
    # StatisticsGenerator.playwright_migration_sources()
    StatisticsGenerator.adoption_donut_chart()
    StatisticsGenerator.migration_donut_chart()