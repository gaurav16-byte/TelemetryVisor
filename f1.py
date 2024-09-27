from urllib.request import urlopen
import json
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, time
import seaborn as sns
from time import sleep
import numpy as np
from scipy.interpolate import interp1d

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

session_key, meeting_key, ckt_short, country_name = important_values('United+States', 2023, 'Las Vegas')

def cars_data(driver_number, session_key = session_key):
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


 
def compare_drivers(d1, d2, session_key = session_key, driver_nos = driver_nos):
    color1 = '#3671C6'
    color2 = '#FF8700'
    rpm1, speed1, gear1, throttle1, brake1, drs1 = cars_data(d1)
    rpm2, speed2, gear2, throttle2, brake2, drs2 = cars_data(d2)

    plt.figure(figsize=(10, 6))
    plt.plot(speed1, color=color1, label=driver_nos[d1])
    plt.plot(speed2, color=color2, label=driver_nos[d2])
    plt.title("Speed Comparison of Drivers")
    plt.xlabel("Time (or Lap Data Points)")
    plt.ylabel("Speed (km/h)")
    plt.legend(loc="upper right")
    plt.show()

compare_drivers(1, 44)

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
    seg1 = data[0]['segments_sector_1']
    seg2 = data[0]['segments_sector_2']
    seg3 = data[0]['segments_sector_3']
    time_obj = datetime.fromisoformat(started)
    seconds_to_add = duration
    new_time = time_obj + timedelta(seconds=seconds_to_add)
    new_time_string = new_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
    return started, new_time_string

started, new_time_string = laps_info(1, 25)

def locations(driver, start, end, session_key = session_key):   #ADDED TRACKERS FOR CARS
    sleep(1)
    response = urlopen(f'https://api.openf1.org/v1/location?session_key={session_key}&driver_number={driver}&date>{start}&date<{end}')
    data = json.loads(response.read().decode('utf-8'))
    xx = []
    yy = []
    for i in data:
        xx.append(i['x'])
        yy.append(i['y'])
    '''
    plt.figure(figsize=(10, 8))
    plt.plot(xx, yy, color='blue', label='Car Path')
    plt.xlabel('X Coordinates')
    plt.ylabel('Y Coordinates')
    plt.title('Car Path on Track')
    plt.grid(True)
    plt.legend()
    plt.show()
    '''

#locations(1, started, new_time_string)

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

def temps(meeting_key = meeting_key):
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
    
    background_color = "#0b0b0b"
    line_colors = sns.color_palette("bright", 5)  # Vibrant colors
    font_color = "#b4b1b1"
    sns.set_theme(style="whitegrid")
    fig, axs = plt.subplots(5, 1, figsize=(10, 12))
    fig.patch.set_facecolor(background_color)
    for ax in axs:
        ax.set_facecolor(background_color)
    thin_line_width = 1.6
    sns.lineplot(data=air, ax=axs[0], color=line_colors[0], lw=thin_line_width)
    axs[0].set_title('Air Temperature', fontsize=14, color=font_color)
    axs[0].set_ylabel('Temp (°C)', fontsize=12, color=font_color)
    sns.lineplot(data=hum, ax=axs[1], color=line_colors[1], lw=thin_line_width)
    axs[1].set_title('Humidity', fontsize=14, color=font_color)
    axs[1].set_ylabel('Humidity (%)', fontsize=12, color=font_color)
    sns.lineplot(data=rain, ax=axs[2], color=line_colors[2], lw=thin_line_width)
    axs[2].set_title('Rainfall', fontsize=14, color=font_color)
    axs[2].set_ylabel('Rain (mm)', fontsize=12, color=font_color)
    sns.lineplot(data=track, ax=axs[3], color=line_colors[3], lw=thin_line_width)
    axs[3].set_title('Track Temperature', fontsize=14, color=font_color)
    axs[3].set_ylabel('Track Temp (°C)', fontsize=12, color=font_color)
    sns.lineplot(data=winsp, ax=axs[4], color=line_colors[4], lw=thin_line_width)
    axs[4].set_title('Wind Speed', fontsize=14, color=font_color)
    axs[4].set_ylabel('Wind Speed (km/h)', fontsize=12, color=font_color)
    for ax in axs:
        ax.tick_params(colors=font_color)  # Set tick colors
        ax.xaxis.label.set_color(font_color)  # Set x-axis label color
        ax.yaxis.label.set_color(font_color)  # Set y-axis label color
        ax.set_xticklabels([])
        ax.grid(False)
        ax.axhline(0, color=font_color, lw=1.0)  # Horizontal axis (X-axis)
        ax.axvline(0, color=font_color, lw=1.0)  # Vertical axis (Y-axis)
    plt.tight_layout(pad=2.0)
    plt.show()
