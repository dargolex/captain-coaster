from flask import Flask, render_template, request, jsonify
from coasters import add_park_by_name, update_coaster_order, load_coasters_for_display

app = Flask(__name__)

@app.route('/')
def index():
    coasters = load_coasters_for_display()
    return render_template('index.html', coasters=coasters)

@app.route('/update_order', methods=['POST'])
def update_order():
    new_order = request.json['order']  # list of coaster IDs in new order
    update_coaster_order(new_order)
    return jsonify({'status': 'success'})

@app.route('/add_park', methods=['POST'])
def add_park():
    data = request.get_json()
    park_name = data.get('park_name')
    if not park_name:
        return jsonify({'status': 'error', 'message': 'No park name provided.'}), 400
    ok, msg = add_park_by_name(park_name)
    if ok:
        return jsonify({'status': 'success', 'message': msg})
    else:
        return jsonify({'status': 'error', 'message': msg})

if __name__ == '__main__':
    app.run(debug=True)
