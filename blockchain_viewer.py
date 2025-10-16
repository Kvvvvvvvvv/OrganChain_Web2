from flask import Flask, render_template, jsonify
import json
import os

app = Flask(__name__, 
            template_folder='client/templates',
            static_folder='client/static')

@app.route('/')
def view_blockchain():
    if os.path.exists('blockchain.json'):
        with open('blockchain.json', 'r') as f:
            data = json.load(f)
    else:
        data = []
    return render_template('blockchain.html', chain=data)

@app.route('/api/chain')
def api_chain():
    if os.path.exists('blockchain.json'):
        with open('blockchain.json', 'r') as f:
            data = json.load(f)
    else:
        data = []
    return jsonify(data)

if __name__ == '__main__':
    app.run(port=5001, debug=True)