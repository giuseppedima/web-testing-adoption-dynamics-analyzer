import os

from flask import Flask, jsonify, render_template,request
import pandas as pd

app = Flask(__name__)

#csv_file_path = 'changes_to_analyze_new_merged.csv'
csv_file_path = '/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/PBT/pbt_files_changes.csv'
excel_file_path = '/home/sergio/PycharmProjects/ICSME-be/adoption_commits_filtered.xlsx'

@app.route('/')
def index():
    return render_template('IST-commit-analysis.html')


@app.route('/get_csv_data/<int:index>', methods=['GET'])
def get_csv_data(index):
    #df = pd.read_csv(csv_file_path)
    df = pd.read_excel(excel_file_path, engine='openpyxl')
    if index < 0 or index >= len(df):
        return jsonify({'error': 'Index out of range'})

    row = df.iloc[index].to_dict()

    # Controlla se 'change_label' è NaN
    if pd.isna(row['label']):
        row['label'] = ''  # Assegna una stringa vuota se è NaN

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

    # Leggi il CSV
    #df = pd.read_csv(csv_file_path)
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

@app.route('/labels', methods=['GET'])
def get_labels():
    df = pd.read_csv(csv_file_path)
    # Filtra solo i valori non vuoti
    labels = sorted(df['label'].dropna().unique().tolist())
    # Trunca ogni label a 200 caratteri e aggiungi "..." se necessario
    labels = [label[:200] + "..." if len(label) > 200 else label for label in labels]

    return jsonify(labels)

if __name__ == '__main__':
    app.run(debug=True)
