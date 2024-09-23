from urllib.request import urlopen
import json
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import seaborn as sns

def namesss(country, year, ckt = None): #TO GET PROPER NAME OF THE GRAND PRIX
    response = urlopen(f'https://api.openf1.org/v1/meetings?year={year}&country_name={country}')
    data = json.loads(response.read().decode('utf-8'))
    if len(data) == 1:
        data = data[0]
    else:
        for i in range(len(data)):
            if data[i]['circuit_short_name'].lower() == ckt.lower():
                data = data[i]
    return data["meeting_official_name"]

def important_values(country, session_type, year, ckt = None):  #TO GET THE SESSION, MEETING KEYS, SHORT CIRCUIT NAME, AND COUNTRY
    response = urlopen(f'https://api.openf1.org/v1/sessions?country_name={country}&session_name={session_type}&year={year}')
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
    start_date = data['date_start']
    gmt_offset = data['gmt_offset']
    print(start_date)
    print(gmt_offset)
    return session_key, meeting_key, ckt_short, country_name

session_key, meeting_key, ckt_short, country_name = important_values('United+States', 'Race', 2023, 'Austin')

def cars_data(driver_number, session_key = session_key):
    response = urlopen(f'https://api.openf1.org/v1/car_data?driver_number={driver_number}&session_key={session_key}&speed>=1')  #SPEED AND OTHER CAR DETAILS
    data = json.loads(response.read().decode('utf-8'))
    rpm = speed = gear = throttle = brake = drs = []
    for i in data:
        rpm.append(i['rpm'])
        speed.append(i['speed'])
        gear.append(i['n_gear'])
        throttle.append(i['throttle'])
        brake.append(i['brake'])
        drs.append(i['drs'])
    return rpm, speed, gear, throttle, brake, drs

def drivers_info(car_no, session_key = session_key):    #GET TEAM COLOR AND DRIVERS SHORT NAME
    response = urlopen(f'https://api.openf1.org/v1/drivers?driver_number={car_no}&session_key={session_key}')
    data = json.loads(response.read().decode('utf-8'))[0]
    short = data['name_acronym']
    team_color = data['team_colour']
    return short, team_color
    
def laps_info(driver, lap_number, session_key = session_key):   #ADDED LAP TIMES AND MINI SECTORS
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
    return speed_trap, duration, out_lap, sec1, sec2, sec3, seg1, seg2, seg3, started

speed_trap, duration, out_lap, sec1, sec2, sec3, seg1, seg2, seg3, started = laps_info(1,25)
time_obj = datetime.fromisoformat(started)
seconds_to_add = duration
new_time = time_obj + timedelta(seconds=seconds_to_add)
new_time_string = new_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]

def locations(driver, start, end, session_key = session_key):   #ADDED TRACKERS FOR CARS
    response = urlopen(f'https://api.openf1.org/v1/location?session_key={session_key}&driver_number={driver}&date>{start}&date<{end}')
    data = json.loads(response.read().decode('utf-8'))
    xx = []
    yy = []
    for i in data:
        xx.append(i['x'])
        yy.append(i['y'])
    #'''
    plt.figure(figsize=(10, 8))
    plt.plot(xx, yy, color='blue', label='Car Path')
    plt.xlabel('X Coordinates')
    plt.ylabel('Y Coordinates')
    plt.title('Car Path on Track')
    plt.grid(True)
    plt.legend()
    plt.show()
    #'''

locations(1, started, new_time_string)

def tyres(session_key = session_key):   #STINTS FOR ALL DRIVERS USE A FOR LOOP FOR SPECIFIC DRIVER DATA OR 
    response = urlopen(f'https://api.openf1.org/v1/stints?session_key={session_key}&tyre_age_at_start>=0')
    data = json.loads(response.read().decode('utf-8'))
    compound = data[0]['compound']
    start_age = data[0]['tyre_age_at_start']
    start_lap = data[0]['lap_start']
    end_lap = data[0]['lap_end']

def radios(driver, session_key = session_key):  #WITH COMMENTS CAN LISTEN TO RADIOS ONE BY ONE
    response = urlopen(f'https://api.openf1.org/v1/team_radio?session_key={session_key}&driver_number={driver}')
    data = json.loads(response.read().decode('utf-8'))
    '''
    import pygame
    import requests
    from io import BytesIO
    audios = []
    for i in x:
        audios.append(i['recording_url'])
    def listen(link):
        pygame.mixer.init()
        response = requests.get(link)
        audio_file = BytesIO(response.content)
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
    listen(audios[0])
    '''

def temps(meeting_key = meeting_key):
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