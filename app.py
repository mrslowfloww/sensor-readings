import os
from datetime import datetime, timedelta
from flask import Flask, render_template
import plotly.graph_objs as go
from plotly.subplots import make_subplots

app = Flask(__name__)
file_directory = '/home/rock/ssd/Python-Projects/sensor_readings/'

def ensure_static_directory():
    static_dir = os.path.join(file_directory, 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

def read_highs_lows(file_path, days=7):
    today = datetime.now().date()
    start_date = today - timedelta(days=days)
    data = {"dates": [], "high_temp": [], "low_temp": [], "high_hum": [], "low_hum": [], "high_heat_index": [], "low_heat_index": []}
    
    with open(file_path, 'r') as file:
        lines = file.readlines()
        i = 0
        while i < len(lines):
            try:
                if lines[i].startswith("[") and lines[i].endswith("]\n"):
                    date_line = lines[i].strip()
                    date_str = date_line[1:-1]
                    date = datetime.strptime(date_str, "%d/%m/%Y").date()
                    if date < start_date:
                        i += 8
                        continue
                    
                    data["dates"].append(date_str[:-5])  # Store only day and month
                    
                    high_temp = float(lines[i + 1].split()[2])
                    low_temp = float(lines[i + 2].split()[2])
                    high_hum = float(lines[i + 3].split()[2])
                    low_hum = float(lines[i + 4].split()[2])
                    high_heat_index = float(lines[i + 5].split()[2])
                    low_heat_index = float(lines[i + 6].split()[2])
                    
                    data["high_temp"].append(high_temp)
                    data["low_temp"].append(low_temp)
                    data["high_hum"].append(high_hum)
                    data["low_hum"].append(low_hum)
                    data["high_heat_index"].append(high_heat_index)
                    data["low_heat_index"].append(low_heat_index)
                    i += 8
                else:
                    i += 1
            except Exception as e:
                print(f"Error processing line {i}: {lines[i].strip()}, error: {e}")
                i += 1
    
    return data

def create_graph(data, high_key, low_key, filename, y_label):
    fig = make_subplots(specs=[[{"secondary_y": False}]])
    
    fig.add_trace(go.Scatter(x=data["dates"], y=data[low_key], mode='lines+markers+text', name='Low',
                             text=[f"<b>{val}</b>" for val in data[low_key]], textposition="top center", line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=data["dates"], y=data[high_key], mode='lines+markers+text', name='High',
                             text=[f"<b>{val}</b>" for val in data[high_key]], textposition="top center", line=dict(color='red')))
    
    fig.update_layout(
        #title=f"{y_label} pentru ultimele {len(data['dates'])} zile",
        xaxis_title="Date",
        yaxis_title=y_label,
        legend_title="Legend",
        template="plotly_white"
    )

    fig.write_image(filename)

@app.route('/')
def index():
    ensure_static_directory()
    
    file_path = os.path.join(file_directory, 'highs_lows.txt')
    data_7_days = read_highs_lows(file_path, days=7)
    data_30_days = read_highs_lows(file_path, days=30)
    
    temp_graph_7_days = os.path.join(file_directory, 'static/temp_graph_7_days.png')
    hum_graph_7_days = os.path.join(file_directory, 'static/hum_graph_7_days.png')
    heat_index_graph_7_days = os.path.join(file_directory, 'static/heat_index_graph_7_days.png')
    
    temp_graph_30_days = os.path.join(file_directory, 'static/temp_graph_30_days.png')
    hum_graph_30_days = os.path.join(file_directory, 'static/hum_graph_30_days.png')
    heat_index_graph_30_days = os.path.join(file_directory, 'static/heat_index_graph_30_days.png')
    
    create_graph(data_7_days, "high_temp", "low_temp", temp_graph_7_days, "Temperatura (°C)")
    create_graph(data_7_days, "high_hum", "low_hum", hum_graph_7_days, "Umiditatea (%)")
    create_graph(data_7_days, "high_heat_index", "low_heat_index", heat_index_graph_7_days, "Heat Index (°C)")
    
    create_graph(data_30_days, "high_temp", "low_temp", temp_graph_30_days, "Temperatura (°C)")
    create_graph(data_30_days, "high_hum", "low_hum", hum_graph_30_days, "Umiditatea (%)")
    create_graph(data_30_days, "high_heat_index", "low_heat_index", heat_index_graph_30_days, "Heat Index (°C)")
    
    return render_template('index.html', 
                           temp_graph_7_days='static/temp_graph_7_days.png', 
                           hum_graph_7_days='static/hum_graph_7_days.png', 
                           heat_index_graph_7_days='static/heat_index_graph_7_days.png',
                           temp_graph_30_days='static/temp_graph_30_days.png', 
                           hum_graph_30_days='static/hum_graph_30_days.png', 
                           heat_index_graph_30_days='static/heat_index_graph_30_days.png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
