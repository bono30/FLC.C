
from flask import Flask, render_template, request, jsonify, send_file
import os
import math
import csv
import matplotlib.pyplot as plt

app = Flask(__name__)

data_store = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save', methods=['POST'])
def save():
    data = request.json
    diameter = float(data['diameter'])
    major_axis = math.dist(data['major'][0], data['major'][1])
    minor_axis = math.dist(data['minor'][0], data['minor'][1])

    strain_major = math.log(major_axis / diameter)
    strain_minor = math.log(minor_axis / diameter)

    result = {
        'ID': len(data_store) + 1,
        'Major_axis_mm': round(major_axis, 3),
        'Minor_axis_mm': round(minor_axis, 3),
        'Major_strain': round(strain_major, 5),
        'Minor_strain': round(strain_minor, 5)
    }

    data_store.append(result)
    generate_plot()
    save_csv()
    return jsonify(data_store)

def save_csv():
    if not data_store:
        return
    os.makedirs('data', exist_ok=True)
    csv_path = 'data/results.csv'
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = data_store[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for data in data_store:
            writer.writerow(data)

def generate_plot():
    eps1 = [d['Major_strain'] for d in data_store]
    eps2 = [d['Minor_strain'] for d in data_store]

    plt.figure(figsize=(6,6))
    plt.scatter(eps1, eps2, color='blue')
    plt.xlabel('Major Strain (ε₁)')
    plt.ylabel('Minor Strain (ε₂)')
    plt.title('Forming Limit Curve (FLC)')
    plt.grid(True)
    plt.savefig('static/flc_plot.png')
    plt.close()

@app.route('/download_csv')
def download_csv():
    return send_file('data/results.csv', as_attachment=True)

@app.route('/reset', methods=['POST'])
def reset():
    global data_store
    data_store = []
    if os.path.exists('data/results.csv'):
        os.remove('data/results.csv')
    if os.path.exists('static/flc_plot.png'):
        os.remove('static/flc_plot.png')
    return jsonify({'status': 'reset'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
