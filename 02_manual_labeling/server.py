import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flask import Flask, jsonify, render_template, request
import pandas as pd
from core.config import RESOURCES_DIR

app = Flask(__name__)

# This will be set by the CLI
excel_file_path = None
is_commits = False  # True if commits, False if issues

@app.route('/')
def index():
    if is_commits:
        return render_template('IST-commit-analysis.html')
    else:
        return render_template('IST-issue-analysis.html')


@app.route('/get_csv_data/<int:index>', methods=['GET'])
def get_csv_data(index):
    if excel_file_path is None:
        return jsonify({'error': 'Excel file path not set'}), 500
    df = pd.read_excel(excel_file_path, engine='openpyxl')
    if index < 0 or index >= len(df):
        return jsonify({'error': 'Index out of range'})

    row = df.iloc[index].to_dict()

    # Controlla i NaN
    for key, value in row.items():
        if pd.isna(value):
            row[key] = ''  # Assign empty string if NaN

    return jsonify(row)


@app.route('/get_total_rows', methods=['GET'])
def get_total_rows():
    if excel_file_path is None:
        return jsonify({'error': 'Excel file path not set'}), 500
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
    # Receive data (index and new label)
    data = request.get_json()
    index = data.get('index')
    new_label = data.get('change_label')

    if index is None or new_label is None:
        return jsonify({'error': 'Index or change_label is missing'}), 400

    if excel_file_path is None:
        return jsonify({'error': 'Excel file path not set'}), 500

    # Read excel
    df = pd.read_excel(excel_file_path,engine='openpyxl')

    # Verify that the index is valid
    if index < 0 or index >= len(df):
        return jsonify({'error': 'Index out of range'}), 400

    # Update the row with the new label
    df.at[index, 'label'] = new_label

    # Save the Excel file with the update
    df.to_excel(excel_file_path, index=False, engine='openpyxl')

    return jsonify({'success': True, 'message': 'Label saved successfully'})

@app.route('/keywords', methods=['GET'])
def get_keywords():
    if excel_file_path is None:
        return jsonify({'error': 'Excel file path not set'}), 500
    df = pd.read_excel(excel_file_path, engine='openpyxl')
    # Filter only non-empty values
    # Extract all keywords, split by comma, trim and make unique
    keywords_series = df['matches'].dropna().apply(lambda x: [kw.strip() for kw in str(x).split(',')])
    keywords = sorted(set(kw for sublist in keywords_series for kw in sublist if kw))
    # Truncate each keyword to 200 characters and add "..." if necessary
    keywords = [keyword[:200] + "..." if len(keyword) > 200 else keyword for keyword in keywords]

    return jsonify(keywords)


@app.route('/labels', methods=['GET'])
def get_labels():
    if excel_file_path is None:
        return jsonify({'error': 'Excel file path not set'}), 500
    df = pd.read_excel(excel_file_path, engine='openpyxl')
    # Filter only non-empty values
    labels = sorted(df['label'].dropna().unique().tolist())
    # Truncate each label to 200 characters and add "..." if necessary
    labels = [label[:200] + "..." if len(label) > 200 else label for label in labels]

    return jsonify(labels)

@app.route('/filter_by_keywords', methods=['POST'])
def filter_by_keywords():
    if excel_file_path is None:
        return jsonify({'error': 'Excel file path not set'}), 500
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

def set_excel_file(file_path, target_type):
    """Set the Excel file path and target type to be used by the server."""
    global excel_file_path, is_commits
    excel_file_path = file_path
    is_commits = (target_type == 'commits')

if __name__ == '__main__':
    app.run(debug=True)
