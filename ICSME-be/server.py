import os

from flask import Flask, jsonify, render_template,request
import pandas as pd
from pathlib import Path

app = Flask(__name__)

# excel_file_path = Path(__file__).parent / 'adoption_commits_filtered.xlsx'
# excel_file_path = Path(__file__).parent / 'migration_commits_filtered.xlsx'
# excel_file_path = Path(__file__).parent / 'adoption_issues_filtered.xlsx'
excel_file_path = Path(__file__).parent / 'migration_issues_filtered.xlsx'

@app.route('/')
def index():
    # return render_template('IST-commit-analysis.html')
    return render_template('IST-issue-analysis.html')


@app.route('/get_csv_data/<int:index>', methods=['GET'])
def get_csv_data(index):
    df = pd.read_excel(excel_file_path, engine='openpyxl')
    if index < 0 or index >= len(df):
        return jsonify({'error': 'Index out of range'})

    row = df.iloc[index].to_dict()

    # Controlla i NaN
    for key, value in row.items():
        if pd.isna(value):
            row[key] = ''  # Assegna una stringa vuota se è NaN

    return jsonify(row)


@app.route('/get_total_rows', methods=['GET'])
def get_total_rows():
    if not os.path.exists(excel_file_path):
        return jsonify({'error': 'Excel file not found'}), 404
    try:
        df = pd.read_excel(excel_file_path,engine='openpyxl')
        total_rows = len(df)
        return jsonify({'total_rows': total_rows})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/save_label',methods=['POST'])
def save_label():
    # Ricevi i dati (indice e nuova etichetta)
    data = request.get_json()
    index = data.get('index')
    new_label = data.get('change_label')

    if index is None or new_label is None:
        return jsonify({'error': 'Index or change_label is missing'}), 400

    # Leggi excel
    df = pd.read_excel(excel_file_path,engine='openpyxl')

    # Verifica che l'indice sia valido
    if index < 0 or index >= len(df):
        return jsonify({'error': 'Index out of range'}), 400

    # Aggiorna la riga con la nuova etichetta
    df.at[index, 'label'] = new_label

    # Salva il file CSV con l'aggiornamento
    df.to_excel(excel_file_path, index=False, engine='openpyxl')

    return jsonify({'success': True, 'message': 'Label saved successfully'})

@app.route('/keywords', methods=['GET'])
def get_keywords():
    df = pd.read_excel(excel_file_path, engine='openpyxl')
    # Filtra solo i valori non vuoti
    # Estrai tutte le keyword, splitta per virgola, trimma e rendi uniche
    keywords_series = df['matches'].dropna().apply(lambda x: [kw.strip() for kw in str(x).split(',')])
    keywords = sorted(set(kw for sublist in keywords_series for kw in sublist if kw))
    # Trunca ogni keyword a 200 caratteri e aggiungi "..." se necessario
    keywords = [keyword[:200] + "..." if len(keyword) > 200 else keyword for keyword in keywords]

    return jsonify(keywords)


@app.route('/labels', methods=['GET'])
def get_labels():
    df = pd.read_excel(excel_file_path, engine='openpyxl')
    # Filtra solo i valori non vuoti
    labels = sorted(df['label'].dropna().unique().tolist())
    # Trunca ogni label a 200 caratteri e aggiungi "..." se necessario
    labels = [label[:200] + "..." if len(label) > 200 else label for label in labels]

    return jsonify(labels)

@app.route('/filter_by_keywords', methods=['POST'])
def filter_by_keywords():
    data = request.get_json()
    keywords = data.get('keywords', [])
    if not keywords:
        return jsonify({'indices': []})
    df = pd.read_excel(excel_file_path, engine='openpyxl')
    indices = []
    for idx, row in df.iterrows():
        matches = str(row.get('matches', ''))
        if any(kw in matches for kw in keywords):
            indices.append(idx)
    return jsonify({'indices': indices})

if __name__ == '__main__':
    app.run(debug=True)
