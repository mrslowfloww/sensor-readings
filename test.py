from datetime import datetime, timedelta

# Specify the exact directory where you want to save the files
file_directory = '/home/rock/ssd/Python-Projects/sensor_readings/'

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
                file.write(f"[day when the readings took place, {yesterday_str}]\n")
                file.write(f"highest temp: {highest_temp[0]} {highest_temp[3]}\n")
                file.write(f"lowest temp: {lowest_temp[0]} {lowest_temp[3]}\n")
                file.write(f"highest hum: {highest_hum[1]} {highest_hum[3]}\n")
                file.write(f"lowest hum: {lowest_hum[1]} {lowest_hum[3]}\n")
                file.write(f"highest heat_index: {highest_heat_index[2]} {highest_heat_index[3]}\n")
                file.write(f"lowest heat_index: {lowest_heat_index[2]} {lowest_heat_index[3]}\n")
    except Exception as e:
        print(f"Error in analyze_readings: {e}")

# Call the function to analyze readings
analyze_readings()

