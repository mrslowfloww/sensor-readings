import requests
from bs4 import BeautifulSoup
import schedule
import time
from datetime import datetime, timedelta

# Specify the exact directory where you want to save the files
file_directory = '/home/rock/ssd/Python-Projects/sensor_readings/'

def fetch_and_log_readings():
    url = "http://192.168.0.67/"
    attempts = 0
    while attempts < 2:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            temp = soup.find("div", class_="card temperature").find("span", class_="reading").text
            hum = soup.find("div", class_="card humidity").find("span", class_="reading").text
            heat_index = soup.find("div", class_="card heat_index").find("span", class_="reading").text

            current_time = datetime.now().strftime("%d/%m/%Y %H:%M")
            # Use the specified directory for file path
            with open(file_directory + "readings.txt", "a") as file:
                file.write(f"{current_time} temp: {temp} hum: {hum} heat_index: {heat_index}\n")
            break
        except requests.exceptions.RequestException:
            attempts += 1
            if attempts < 2:
                time.sleep(30)
            else:
                print(f"Failed to retrieve data at {datetime.now().strftime('%d/%m/%Y %H:%M')}, skipping this hour.")

def analyze_readings():
    try:
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        yesterday_str = yesterday.strftime("%d/%m/%Y")

        readings = []
        # Use the specified directory for file path
        with open(file_directory + "readings.txt", "r") as file:
            for line in file:
                try:
                    # Split the line into date and the rest of the readings
                    parts = line.strip().split(' ', 2)
                    date_str = parts[0]
                    time_str = parts[1]
                    readings_str = parts[2]

                    # Split the readings based on labels
                    temp_str = readings_str.split('hum:')[0].split('temp:')[1].strip()
                    hum_str = readings_str.split('heat_index:')[0].split('hum:')[1].strip()
                    heat_index_str = readings_str.split('heat_index:')[1].strip()

                    # Print the parts to debug
                    print(f"Parsed line: date: {date_str}, time: {time_str}, temp: {temp_str}, hum: {hum_str}, heat_index: {heat_index_str}")

                    date = datetime.strptime(date_str + ' ' + time_str, "%d/%m/%Y %H:%M").date()
                    if date == yesterday:
                        temp = float(temp_str)
                        hum = float(hum_str)
                        heat_index = float(heat_index_str)
                        readings.append((temp, hum, heat_index, date_str + ' ' + time_str))
                except Exception as e:
                    print(f"Error parsing line: {line}, error: {e}")

        if readings:
            highest_temp = max(readings, key=lambda x: x[0])
            lowest_temp = min(readings, key=lambda x: x[0])
            highest_hum = max(readings, key=lambda x: x[1])
            lowest_hum = min(readings, key=lambda x: x[1])
            highest_heat_index = max(readings, key=lambda x: x[2])
            lowest_heat_index = min(readings, key=lambda x: x[2])

            # Use the specified directory for file path
            with open(file_directory + "highs_lows.txt", "a") as file:
                file.write(f"[{yesterday_str}]\n")
                file.write(f"highest temp: {highest_temp[0]} {highest_temp[3]}\n")
                file.write(f"lowest temp: {lowest_temp[0]} {lowest_temp[3]}\n")
                file.write(f"highest hum: {highest_hum[1]} {highest_hum[3]}\n")
                file.write(f"lowest hum: {lowest_hum[1]} {lowest_hum[3]}\n")
                file.write(f"highest heat_index: {highest_heat_index[2]} {highest_heat_index[3]}\n")
                file.write(f"lowest heat_index: {lowest_heat_index[2]} {lowest_heat_index[3]}\n\n")
    except Exception as e:
        print(f"Error in analyze_readings: {e}")

# Calculate the delay until the next full hour
now = datetime.now()
next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
delay = (next_hour - now).total_seconds()
print(f"Sleeping for {delay} seconds until the next full hour.")
time.sleep(delay)

# Schedule the tasks
schedule.every().hour.at(":00").do(fetch_and_log_readings)
schedule.every().day.at("00:01").do(analyze_readings)

# Run the schedule
while True:
    schedule.run_pending()
    time.sleep(1)

