from flask import Flask, render_template, request, jsonify
import pandas as pd

# Import the process_park function directly from parc_to_list.py
from parc_to_list import process_park

app = Flask(__name__)

EXCEL_FILE = 'coasters_info.xlsx'

def load_coasters():
    df = pd.read_excel(EXCEL_FILE)
    df = df.sort_values('rank')
    return df

@app.route('/')
def index():
    df = load_coasters()
    coasters = df.to_dict(orient='records')
    return render_template('index.html', coasters=coasters)

@app.route('/update_order', methods=['POST'])
def update_order():
    new_order = request.json['order']  # list of coaster IDs in new order
    df = pd.read_excel(EXCEL_FILE)
    df['rank'] = df['id'].apply(lambda x: new_order.index(x))
    df = df.sort_values('rank')
    df.to_excel(EXCEL_FILE, index=False)
    return jsonify({'status': 'success'})

@app.route('/add_park', methods=['POST'])
def add_park():
    data = request.get_json()
    park_name = data.get('park_name')
    if not park_name:
        return jsonify({'status': 'error', 'message': 'No park name provided.'}), 400

    # Call the process_park function directly
    try:
        # Capture the output of process_park
        import io
        import sys

        captured_output = io.StringIO()
        sys_stdout = sys.stdout
        sys.stdout = captured_output
        process_park(park_name)
        sys.stdout = sys_stdout
        output = captured_output.getvalue()

        if f"No coasters found for park: {park_name}" in output:
            return jsonify({'status': 'error', 'message': f"No coasters found for '{park_name}'."})
        return jsonify({'status': 'success', 'message': f"Park '{park_name}' added!"})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
