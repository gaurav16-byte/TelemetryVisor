from urllib.request import urlopen
import json
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from time import sleep

def mainn():    #TO HAVE THE TRACKS AND COUNTRY ALONG WITH DRIVER DETAILS
    driver_acronyms_2024 = ['VER', 'PER', 'LEC', 'SAI', 'HAM', 'RUS', 'ALO', 'STR', 'NOR', 'PIA', 'GAS', 'OCO', 'BOT', 'ZHO', 'MAG', 'HUL', 'TSU', 'DEV', 'ALB', 'SAR', 'COL', 'BEA']
    driver_numbers_2024 = [1, 11, 16, 55, 44, 63, 14, 18, 4, 81, 10, 31, 77, 24, 20, 27, 22, 21, 23, 2, 50, 34]
    drivers = dict(zip(driver_acronyms_2024, driver_numbers_2024))
    drivers1 = dict(zip(driver_numbers_2024, driver_acronyms_2024))
    
    countries = ['Bahrain', 'Saudi Arabia', 'Australia', 'Azerbaijan', 'United States', 'Italy', 'Monaco', 'Spain', 'Canada', 'Austria', 'United Kingdom', 'Hungary', 'Belgium', 'Netherlands', 'Singapore', 'Japan', 'Qatar', 'Mexico', 'Brazil', 'United States', 'United Arab Emirates', 'China', 'United States', 'Italy']
    circuits = ['','','','','Miami','Imola','','','','','','','','','','','','','','Austin','','','Las Vegas', 'Monza']
    laps = [57, 50, 58, 51, 57, 63, 78, 66, 70, 71, 52, 70, 44, 72, 62, 53, 57, 71, 71, 56, 58, 56, 50, 53]

    return drivers, drivers1

all_drivers, driver_nos = mainn()

def solve_time(date, gmt):  #TO DISPLAY TIME IN THE LOCAL TIME OF THE COUNTRY
    dat = date[:date.find('T')]
    time = date[date.find('T')+1:-6]
    hour = int(gmt[:gmt.find(':')])
    minute = int(gmt[gmt.find(':') + 1 : gmt.rfind(':')])
    utc_datetime = datetime.strptime(f"{dat} {time}", "%Y-%m-%d %H:%M:%S")
    gmt_offset = timedelta(hours=hour, minutes=minute)
    local_datetime = utc_datetime + gmt_offset
    print(f'Local Time: {local_datetime}')

def namesss(country, year, ckt = None): #TO GET PROPER NAME OF THE GRAND PRIX
    sleep(1)
    response = urlopen(f'https://api.openf1.org/v1/meetings?year={year}&country_name={country}')
    data = json.loads(response.read().decode('utf-8'))
    if len(data) == 1:
        data = data[0]
    else:
        for i in range(len(data)):
            if data[i]['circuit_short_name'].lower() == ckt.lower():
                data = data[i]

    return data["meeting_official_name"]

def important_values(country, year, ckt = None, session_type = 'Race'):  #TO GET THE SESSION, MEETING KEYS, SHORT CIRCUIT NAME, AND COUNTRY
    response = urlopen(f'https://api.openf1.org/v1/sessions?country_name={country}&session_name={session_type}&year={year}')
    sleep(1)
    data = json.loads(response.read().decode('utf-8'))
    if len(data) == 1:
        data = data[0]
    else:
        for i in data:
            if i['circuit_short_name'].lower() == ckt.lower():
                data = i

    session_key = data['session_key']
    meeting_key = data['meeting_key']
    ckt_short = data['circuit_short_name']
    country_name = data['country_name']
    print(namesss(country_name.replace(' ','+'), year, ckt))
    start_date = data['date_start']
    gmt_offset = data['gmt_offset']
    solve_time(start_date, gmt_offset)

    return session_key, meeting_key, ckt_short, country_name

session_key, meeting_key, ckt_short, country_name = important_values('Belgium', 2024)

def cars_data(driver_number, session_key = session_key):    #GET VARIOUS DETAILS OF A SPECIFIC CAR
    sleep(1)
    response = urlopen(f'https://api.openf1.org/v1/car_data?driver_number={driver_number}&session_key={session_key}&speed>=1')  #SPEED AND OTHER CAR DETAILS
    data = json.loads(response.read().decode('utf-8'))
    rpm = []
    speed = []
    gear = []
    throttle = []
    brake = []
    drs = []
    for i in data:
        rpm.append(i['rpm'])
        speed.append(i['speed'])
        gear.append(i['n_gear'])
        throttle.append(i['throttle'])
        brake.append(i['brake'])
        drs.append(i['drs'])

    return rpm, speed, gear, throttle, brake, drs

def cars_data_plot(driver_number, session_key = session_key, driver_nos = driver_nos):  #TO PLOT THE VALUES OF A SINGLE CAR
    rpm, speed, gear, throttle, brake, drs = cars_data(driver_number)
    fig, axs = plt.subplots(2, 3, figsize=(12, 8))  # 2 rows, 3 columns
    axs[0, 0].plot(rpm, color='b')
    axs[0, 0].set_title(f"{driver_nos[driver_number]} - RPM")
    axs[0, 0].set_xticks([])    
    axs[0, 1].plot(speed, color='r')
    axs[0, 1].set_title(f"{driver_nos[driver_number]} - Speed (km/h)")
    axs[0, 1].set_xticks([])
    axs[0, 2].plot(gear, color='g')
    axs[0, 2].set_title(f"{driver_nos[driver_number]} - Gear")
    axs[0, 2].set_xticks([])
    axs[1, 0].plot(throttle, color='y')
    axs[1, 0].set_title(f"{driver_nos[driver_number]} - Throttle (%)")
    axs[1, 0].set_xticks([])
    axs[1, 1].plot(brake, color='m')
    axs[1, 1].set_title(f"{driver_nos[driver_number]} - Brake (%)")
    axs[1, 1].set_xticks([])
    axs[1, 2].plot(drs, color='c')
    axs[1, 2].set_title(f"{driver_nos[driver_number]} - DRS Status")
    axs[1, 2].set_xticks([])
    plt.tight_layout()
    plt.show()

def compare_drivers(d1, d2, metric, session_key = session_key, driver_nos = driver_nos):    #TO PLOT THE METRICS OF TWO DIFFERENT DRIVERS
    color1 = '#3671C6'
    color2 = '#FF8700'
    rpm1, speed1, gear1, throttle1, brake1, drs1 = cars_data(d1)
    rpm2, speed2, gear2, throttle2, brake2, drs2 = cars_data(d2)
    plt.figure(figsize=(10, 6))
    plt.plot(f'{metric}1', color=color1, label=driver_nos[d1])
    plt.plot(f'{metric}2', color=color2, label=driver_nos[d2])
    plt.title("Speed Comparison of Drivers")
    plt.xlabel("Time (or Lap Data Points)")
    plt.ylabel("Speed (km/h)")
    plt.legend(loc="upper right")
    plt.show()

#compare_drivers(1, 44)

def laps_info(driver, lap_number, session_key = session_key):   #ADDED LAP TIMES AND MINI SECTORS
    sleep(1)
    try:
        response = urlopen(f'https://api.openf1.org/v1/laps?session_key={session_key}&driver_number={driver}&lap_number={lap_number}')
        data = json.loads(response.read().decode('utf-8'))
    except Exception:
        print("Data not available!")
        return
    if len(data) == 0:
        return
    speed_trap = data[0]['st_speed']
    duration = data[0]['lap_duration']
    out_lap = data[0]['is_pit_out_lap']
    started = data[0]['date_start'][:-9]
    sec1 = data[0]['duration_sector_1']
    sec2 = data[0]['duration_sector_2']
    sec3 = data[0]['duration_sector_3']
    #seg1 = data[0]['segments_sector_1']
    #seg2 = data[0]['segments_sector_2']
    #seg3 = data[0]['segments_sector_3']
    time_obj = datetime.fromisoformat(started)
    seconds_to_add = duration
    new_time = time_obj + timedelta(seconds=seconds_to_add)
    new_time_string = new_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]

    return started, new_time_string, speed_trap, duration, out_lap, sec1, sec2, sec3

def locations(driver, start, end, session_key = session_key):   #ADDED TRACKERS FOR CARS
    sleep(1)
    response = urlopen(f'https://api.openf1.org/v1/location?session_key={session_key}&driver_number={driver}&date>{start}&date<{end}')
    data = json.loads(response.read().decode('utf-8'))
    xx = []
    yy = []
    for i in data:
        xx.append(i['x'])
        yy.append(i['y'])

    return xx, yy

def plot_locations(driver, lapp, session_key = session_key, driver_nos = driver_nos):   #PLOT LOCATIONS OF A SINGLE CAR
    started, new_time_string, speed_trap, duration, out_lap, sec1, sec2, sec3 = laps_info(driver, lapp)
    xx, yy = locations(driver, started, new_time_string, session_key = session_key)
    plt.figure(figsize=(10, 8))
    plt.plot(xx, yy, color='blue', label='Car Path')
    plt.xlabel('X Coordinates')
    plt.ylabel('Y Coordinates')
    plt.title(f'{driver_nos[driver]}, Lap {lapp}')
    plt.grid(True)
    lap_info = f"Lap Duration: {duration:.2f}s\nSector 1: {sec1:.2f}s\nSector 2: {sec2:.2f}s\nSector 3: {sec3:.2f}s\nSpeed Trap: {speed_trap}km/h\nOut Lap:{out_lap}"
    plt.text(0.05, 0.95, lap_info, transform=plt.gca().transAxes, fontsize=12, verticalalignment='top', bbox=dict(facecolor='white', alpha=0.8))
    plt.legend()
    plt.show()

def plot_comparison(d1, d2, lapp, session_key = session_key, driver_nos = driver_nos):  #TO PLOT THE TRACK TAKEN BY EACH DRIVER AND COMPARE THEM LAP BY LAP
    color1 = '#3671C6'
    color2 = '#FF8700'
    started1, new_time_string1, speed_trap1, duration1, out_lap1, sec11, sec21, sec31 = laps_info(d1, lapp)
    xx1, yy1 = locations(d1, started1, new_time_string1, session_key = session_key)
    started2, new_time_string2, speed_trap2, duration2, out_lap2, sec12, sec22, sec32 = laps_info(d2, lapp)
    xx2, yy2 = locations(d2, started2, new_time_string2, session_key = session_key)
    
    plt.figure(figsize=(12, 8))
    plt.plot(xx1, yy1, color=color1, label=driver_nos[d1] + ' Path')
    plt.plot(xx2, yy2, color=color2, label=driver_nos[d2] + ' Path')
    plt.xlabel('X Coordinates')
    plt.ylabel('Y Coordinates')
    plt.title(f'Comparison of {driver_nos[d1]} and {driver_nos[d2]} on Lap {lapp}')
    plt.grid(True)
    lap_info1 = f"Driver: {driver_nos[d1]}\nLap Duration: {duration1:.2f}s\nSector 1: {sec11:.2f}s\nSector 2: {sec21:.2f}s\nSector 3: {sec31:.2f}s\nSpeed Trap: {speed_trap1} km/h\nOut Lap: {out_lap1}"
    plt.text(0.05, 0.95, lap_info1, transform=plt.gca().transAxes, fontsize=12, verticalalignment='top', bbox=dict(facecolor='white', alpha=0.8))
    lap_info2 = f"Driver: {driver_nos[d2]}\nLap Duration: {duration2:.2f}s\nSector 1: {sec12:.2f}s\nSector 2: {sec22:.2f}s\nSector 3: {sec32:.2f}s\nSpeed Trap: {speed_trap2} km/h\nOut Lap: {out_lap2}"
    plt.text(0.75, 0.95, lap_info2, transform=plt.gca().transAxes, fontsize=12, verticalalignment='top', bbox=dict(facecolor='white', alpha=0.8))
    plt.legend()
    plt.show()

def tyres(session_key = session_key):   #STINTS FOR ALL DRIVERS USE A FOR LOOP FOR SPECIFIC DRIVER DATA OR
    sleep(1) 
    response = urlopen(f'https://api.openf1.org/v1/stints?session_key={session_key}&tyre_age_at_start>=0')
    data = json.loads(response.read().decode('utf-8'))
    compound = data[0]['compound']
    start_age = data[0]['tyre_age_at_start']
    start_lap = data[0]['lap_start']
    end_lap = data[0]['lap_end']

def radios(driver, session_key = session_key):  #WITH COMMENTS CAN LISTEN TO RADIOS ONE BY ONE
    sleep(1)
    response = urlopen(f'https://api.openf1.org/v1/team_radio?session_key={session_key}&driver_number={driver}')
    data = json.loads(response.read().decode('utf-8'))

def temps(meeting_key = meeting_key):   #TO PLOT THE TEMPARATURES ON THE TRACK
    sleep(1)
    response = urlopen(f'https://api.openf1.org/v1/weather?meeting_key={meeting_key}&wind_direction>=0&track_temperature>=1')
    data = json.loads(response.read().decode('utf-8'))
    air = []
    hum = []
    rain = []
    track = []
    winsp = []
    for i in data:
        air.append(i['air_temperature'])
        hum.append(i['humidity'])
        rain.append(i['rainfall'])
        track.append(i['track_temperature'])
        winsp.append(i['wind_speed'])
    
    fig, axs = plt.subplots(5, 1, figsize=(10, 12))
    axs[0].plot(air, color='blue', label='Air Temperature (°C)')
    axs[0].set_title('Air Temperature')
    axs[0].set_xticks([])
    axs[1].plot(hum, color='orange', label='Humidity (%)')
    axs[1].set_title('Humidity')
    axs[1].set_xticks([])
    axs[2].plot(rain, color='green', label='Rainfall (mm)')
    axs[2].set_title('Rainfall')
    axs[2].set_xticks([])
    axs[3].plot(track, color='red', label='Track Temperature (°C)')
    axs[3].set_title('Track Temperature')
    axs[3].set_xticks([])
    axs[4].plot(winsp, color='purple', label='Wind Speed (km/h)')
    axs[4].set_title('Wind speed')
    axs[4].set_xticks([])

    plt.tight_layout()
    plt.show()
