from flask import Flask, render_template, request, jsonify
import pandas as pd

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

if __name__ == '__main__':
    app.run(debug=True)
