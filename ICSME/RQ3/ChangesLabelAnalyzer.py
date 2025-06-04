import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import DBSCAN
import pandas as pd

class ChangesLabelAnalyzer:

    @staticmethod
    def list_all_label():
        file_path = '/home/sergio/PycharmProjects/ICSME-be/changes_to_analyze_new_merged.csv'
        directory_save = '/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/ICSME/RQ3'
        if not os.path.exists(file_path):
            print(f"Error: File not found at {file_path}")
            return

        df = pd.read_csv(file_path)

        if 'label' not in df.columns:
            print("Error: Column 'label' not found in CSV file.")
            return

        labels = (
            df['label']
            .dropna()
            .astype(str)
            .str.split(";")
            .explode()
            .str.strip()
        )

        labels = labels.unique()
        labels = pd.Series(labels)
        labels = labels[labels.str.len() > 0]

        cleaned_df = pd.DataFrame({'label': labels})

        cleaned_df.to_csv(directory_save+"/cleaned_labels.csv", index=False)

        print(labels)
        print(f"Total unique labels: {len(labels)}")

        ChangesLabelAnalyzer.indetify_similar_labels()




    @staticmethod
    def indetify_similar_labels():

        file_path = '/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/ICSME/RQ3/cleaned_labels.csv'
        if not os.path.exists(file_path):
            print(f"Error: File not found at {file_path}")
            return
        df = pd.read_csv(file_path)

        labels = df['label']

        # Step 1: Vettorizzazione delle etichette usando TF-IDF
        vectorizer = TfidfVectorizer().fit_transform(labels)
        vectors = vectorizer.toarray()

        # Step 2: Calcolo della Cosine Similarity
        cos_sim_matrix = cosine_similarity(vectors)

        # Step 3: Calcolo della "distanza" e correzione dei valori negativi
        distance_matrix = 1 - cos_sim_matrix
        distance_matrix = np.clip(distance_matrix, 0, None)

        # Step 4: Clustering usando DBSCAN
        clustering = DBSCAN(eps=0.3, min_samples=1, metric='precomputed')
        labels_clustered = clustering.fit_predict(distance_matrix)

        # Step 5: Visualizzazione dei risultati
        clustered_df = pd.DataFrame({'Label': labels, 'Cluster': labels_clustered})
        print(clustered_df.sort_values(by='Cluster'))
        clustered_df.to_csv('cluster_changes.csv',index=False)


if __name__ == "__main__":
    ChangesLabelAnalyzer.list_all_label()
