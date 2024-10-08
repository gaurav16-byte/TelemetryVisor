from urllib.request import urlopen
import json
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from time import sleep
import io
import requests
import discord
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

def mainn(i = None):
    driver_acronyms_2024 = ['VER', 'PER', 'LEC', 'SAI', 'HAM', 'RUS', 'ALO', 'STR', 'NOR', 'PIA', 'GAS', 'OCO', 'BOT', 'ZHO', 'MAG', 'HUL', 'TSU', 'DEV', 'ALB', 'SAR', 'COL', 'BEA']
    driver_numbers_2024 = [1, 11, 16, 55, 44, 63, 14, 18, 4, 81, 10, 31, 77, 24, 20, 27, 22, 21, 23, 2, 50, 34]
    drivers = dict(zip(driver_acronyms_2024, driver_numbers_2024))
    drivers1 = dict(zip(driver_numbers_2024, driver_acronyms_2024))
    
    countries = ['Bahrain', 'Saudi Arabia', 'Australia', 'Azerbaijan', 'United States', 'Italy', 'Monaco', 'Spain', 'Canada', 'Austria', 'United Kingdom', 'Hungary', 'Belgium', 'Netherlands', 'Singapore', 'Japan', 'Qatar', 'Mexico', 'Brazil', 'United States', 'United Arab Emirates', 'China', 'United States', 'Italy']
    circuits = ['','','','','Miami','Imola','','','','','','','','','','','','','','Austin','','','Las Vegas', 'Monza']
    laps = [57, 50, 58, 51, 57, 63, 78, 66, 70, 71, 52, 70, 44, 72, 62, 53, 57, 71, 71, 56, 55, 50, 50, 53]
    tracks = []
    for i in range(len(countries)):
        tracks.append(f'{countries[i]}:{circuits[i]}:{laps[i]}')

    return drivers, drivers1, tracks

all_drivers, driver_nos, tracks = mainn()

def solve_time(date, gmt):
    dat = date[:date.find('T')]
    time = date[date.find('T')+1:-6]
    hour = int(gmt[:gmt.find(':')])
    minute = int(gmt[gmt.find(':') + 1 : gmt.rfind(':')])
    utc_datetime = datetime.strptime(f"{dat} {time}", "%Y-%m-%d %H:%M:%S")
    gmt_offset = timedelta(hours=hour, minutes=minute)
    local_datetime = utc_datetime + gmt_offset
    return f'Local Time: {local_datetime}'

def namesss(country, year, ckt = None):
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

def important_values(country, year, ckt = None, session_type = 'Race'):
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
    y = namesss(country_name.replace(' ','+'), year, ckt)
    start_date = data['date_start']
    gmt_offset = data['gmt_offset']
    x = solve_time(start_date, gmt_offset)

    return session_key, meeting_key, ckt_short, country_name, x, y
#session_key, meeting_key, ckt_short, country_name, x, y = important_values('Belgium', 2024)

def cars_data(driver_number, session_key):
    sleep(1)
    response = urlopen(f'https://api.openf1.org/v1/car_data?driver_number={driver_number}&session_key={session_key}&speed>=1')
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

def cars_data_plot(driver_number, session_key, driver_nos = driver_nos):
    rpm, speed, gear, throttle, brake, drs = cars_data(driver_number, session_key)
    fig = make_subplots(rows=2, cols=3, subplot_titles=(
        f"{driver_nos[driver_number]} - RPM",
        f"{driver_nos[driver_number]} - Speed (km/h)",
        f"{driver_nos[driver_number]} - Gear",
        f"{driver_nos[driver_number]} - Throttle (%)",
        f"{driver_nos[driver_number]} - Brake (%)",
        f"{driver_nos[driver_number]} - DRS Status"
    ))
    fig.add_trace(go.Scatter(y=rpm, mode='lines', line=dict(color='blue')), row=1, col=1)
    fig.add_trace(go.Scatter(y=speed, mode='lines', line=dict(color='red')), row=1, col=2)
    fig.add_trace(go.Scatter(y=gear, mode='lines', line=dict(color='green')), row=1, col=3)
    fig.add_trace(go.Scatter(y=throttle, mode='lines', line=dict(color='yellow')), row=2, col=1)
    fig.add_trace(go.Scatter(y=brake, mode='lines', line=dict(color='magenta')), row=2, col=2)
    fig.add_trace(go.Scatter(y=drs, mode='lines', line=dict(color='cyan')), row=2, col=3)

    fig.update_layout(height=600, width=900, title_text=f"Car Data for {driver_nos[driver_number]}", showlegend=False)
    buffer = io.StringIO()
    fig.write_html(buffer)
    html_str = buffer.getvalue().encode('utf-8')
    buffer.close()
    return html_str
    #fig.write_html("C:\\Users\\gaura\\OneDrive\\Desktop\\car_data_plot.html")

def compare_drivers(d1, d2, session_key, metric, driver_nos=driver_nos):
    color1 = '#3671C6'
    color2 = '#FF8700'
    rpm1, speed1, gear1, throttle1, brake1, drs1 = cars_data(d1, session_key)
    rpm2, speed2, gear2, throttle2, brake2, drs2 = cars_data(d2, session_key)
    fig = go.Figure()

    if metric.lower() == 'rpm':
        fig.add_trace(go.Scatter(y=rpm1, mode='lines', name=driver_nos[d1], line=dict(color=color1)))
        fig.add_trace(go.Scatter(y=rpm2, mode='lines', name=driver_nos[d2], line=dict(color=color2)))
        fig.update_layout(title="RPM Comparison of Drivers", yaxis_title="RPM")
        
    elif metric.lower() == 'speed':
        fig.add_trace(go.Scatter(y=speed1, mode='lines', name=driver_nos[d1], line=dict(color=color1)))
        fig.add_trace(go.Scatter(y=speed2, mode='lines', name=driver_nos[d2], line=dict(color=color2)))
        fig.update_layout(title="Speed Comparison of Drivers", yaxis_title="Speed (km/h)")

    elif metric.lower() == 'gear':
        fig.add_trace(go.Scatter(y=gear1, mode='lines', name=driver_nos[d1], line=dict(color=color1)))
        fig.add_trace(go.Scatter(y=gear2, mode='lines', name=driver_nos[d2], line=dict(color=color2)))
        fig.update_layout(title="Gear Comparison of Drivers", yaxis_title="Gear")

    elif metric.lower() == 'throttle':
        fig.add_trace(go.Scatter(y=throttle1, mode='lines', name=driver_nos[d1], line=dict(color=color1)))
        fig.add_trace(go.Scatter(y=throttle2, mode='lines', name=driver_nos[d2], line=dict(color=color2)))
        fig.update_layout(title="Throttle Comparison of Drivers", yaxis_title="Throttle (%)")

    elif metric.lower() == 'brake':
        fig.add_trace(go.Scatter(y=brake1, mode='lines', name=driver_nos[d1], line=dict(color=color1)))
        fig.add_trace(go.Scatter(y=brake2, mode='lines', name=driver_nos[d2], line=dict(color=color2)))
        fig.update_layout(title="Brake Comparison of Drivers", yaxis_title="Brake (%)")

    elif metric.lower() == 'drs':
        fig.add_trace(go.Scatter(y=drs1, mode='lines', name=driver_nos[d1], line=dict(color=color1)))
        fig.add_trace(go.Scatter(y=drs2, mode='lines', name=driver_nos[d2], line=dict(color=color2)))
        fig.update_layout(title="DRS Status Comparison of Drivers", yaxis_title="DRS Status")

    fig.update_layout(
        xaxis_title="Time (or Lap Data Points)",
        legend=dict(x=0, y=1, traceorder="normal", orientation="h"),
        height=600,
        width=900
    )
    buffer = io.StringIO()
    fig.write_html(buffer)
    html_str = buffer.getvalue().encode('utf-8')
    buffer.close()
    return html_str

def laps_info(driver, lap_number, session_key):
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

def plot_times(driver, laps, session_key):
    x = []
    y = []
    for i in range(1, laps + 1):
        x.append(i)
        try:
            started, new_time_string, speed_trap, duration, out_lap, sec1, sec2, sec3 = laps_info(driver, i, session_key)
        except Exception:
            duration = 0
            y.append(duration)
        else:
            y.append(duration)
    for i in range(len(y)):
        if y[i] is None:
            y[i] = 0

    fig = go.Figure(data=[go.Bar(x=x, y=y, marker_color='skyblue')])
    fig.update_layout(
        title='Lap Times per Lap',
        xaxis_title='Lap Number',
        yaxis_title='Lap Time (seconds)',
        yaxis=dict(autorange=True)  # Automatically adjust the y-axis range
    )
    buffer = io.StringIO()
    fig.write_html(buffer)
    html_str = buffer.getvalue().encode('utf-8')
    buffer.close()
    return html_str

def times_comparison(driver1, driver2, laps, session_key, driver_nos = driver_nos):
    color1 = '#3671C6'
    color2 = '#FF8700'
    x = []
    y = []
    z = []
    for i in range(1, laps + 1):
        x.append(i)
        try:
            started, new_time_string, speed_trap, duration, out_lap, sec1, sec2, sec3 = laps_info(driver1, i, session_key)
            started1, new_time_string1, speed_trap1, duration1, out_lap1, sec11, sec21, sec31 = laps_info(driver2, i, session_key)
        except Exception:
            duration = 0
            duration1 = 0
            y.append(duration)
            z.append(duration1)
        else:
            y.append(duration)
            z.append(duration1)
    for i in range(len(y)):
        if y[i] is None:
            y[i] = 0
        if z[i] is None:
            z[i] = 0
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=x,
        y=y,
        name=driver_nos[driver1],
        marker_color=color1,
        width=0.35,
    ))
    fig.add_trace(go.Bar(
        x=x,
        y=z,
        name=driver_nos[driver2],
        marker_color=color2,
        width=0.35,
    ))
    fig.update_layout(
        title='Lap Time Comparison',
        xaxis_title='Laps',
        yaxis_title='Lap Time (Seconds)',
        barmode='group',
        bargap=0.2,
        bargroupgap=0.1,
        legend=dict(title='Drivers'),
        height=600, width=800
    )
    buffer = io.StringIO()
    fig.write_html(buffer)
    html_str = buffer.getvalue().encode('utf-8')
    buffer.close()
    return html_str

def locations(driver, start, end, session_key):
    sleep(1)
    response = urlopen(f'https://api.openf1.org/v1/location?session_key={session_key}&driver_number={driver}&date>{start}&date<{end}')
    data = json.loads(response.read().decode('utf-8'))
    xx = []
    yy = []
    for i in data:
        xx.append(i['x'])
        yy.append(i['y'])
    return xx, yy

def plot_locations(driver, lapp, session_key, driver_nos = driver_nos):
    started, new_time_string, speed_trap, duration, out_lap, sec1, sec2, sec3 = laps_info(driver, lapp, session_key)
    xx, yy = locations(driver, started, new_time_string, session_key)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=xx, y=yy,
        mode='lines',
        name='Car Path',
        line=dict(color='blue'),
    ))
    fig.update_layout(
        title=f'{driver_nos[driver]}, Lap {lapp}',
        xaxis_title='X Coordinates',
        yaxis_title='Y Coordinates',
        showlegend=True,
        height=700, width=900,
    )
    lap_info = f"Lap Duration: {duration:.2f}s<br>Sector 1: {sec1:.2f}s<br>Sector 2: {sec2:.2f}s<br>Sector 3: {sec3:.2f}s<br>Speed Trap: {speed_trap} km/h<br>Out Lap: {out_lap}"
    fig.add_annotation(
        text=lap_info,
        xref='paper', yref='paper',
        x=0.05, y=0.95,
        showarrow=False,
        bordercolor='black',
        borderwidth=1,
        borderpad=5,
        bgcolor='white',
        opacity=0.8,
        align='left',
        font=dict(size=12),
    )
    buffer = io.StringIO()
    fig.write_html(buffer)
    html_str = buffer.getvalue().encode('utf-8')
    buffer.close()
    return html_str

def plot_comparison(d1, d2, lapp, session_key, driver_nos = driver_nos):  #TO PLOT THE TRACK TAKEN BY EACH DRIVER AND COMPARE THEM LAP BY LAP
    color1 = '#3671C6'
    color2 = '#FF8700'
    started1, new_time_string1, speed_trap1, duration1, out_lap1, sec11, sec21, sec31 = laps_info(d1, lapp, session_key)
    xx1, yy1 = locations(d1, started1, new_time_string1, session_key)
    started2, new_time_string2, speed_trap2, duration2, out_lap2, sec12, sec22, sec32 = laps_info(d2, lapp, session_key)
    xx2, yy2 = locations(d2, started2, new_time_string2, session_key)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=xx1, y=yy1,
        mode='lines',
        name=f"{driver_nos[d1]} Path",
        line=dict(color=color1),
    ))
    fig.add_trace(go.Scatter(
        x=xx2, y=yy2,
        mode='lines',
        name=f"{driver_nos[d2]} Path",
        line=dict(color=color2),
    ))
    fig.update_layout(
        title=f'Comparison of {driver_nos[d1]} and {driver_nos[d2]} on Lap {lapp}',
        xaxis_title='X Coordinates',
        yaxis_title='Y Coordinates',
        height=700, width=1000,
        legend_title_text='Car Path',
    )
    lap_info1 = (f"Driver: {driver_nos[d1]}<br>"
                 f"Lap Duration: {duration1:.2f}s<br>"
                 f"Sector 1: {sec11:.2f}s<br>"
                 f"Sector 2: {sec21:.2f}s<br>"
                 f"Sector 3: {sec31:.2f}s<br>"
                 f"Speed Trap: {speed_trap1} km/h<br>"
                 f"Out Lap: {out_lap1}")
    fig.add_annotation(
        text=lap_info1,
        xref="paper", yref="paper",
        x=0.05, y=0.95,
        showarrow=False,
        bordercolor="black",
        borderwidth=1,
        borderpad=5,
        bgcolor="white",
        opacity=0.8,
        align="left",
    )
    lap_info2 = (f"Driver: {driver_nos[d2]}<br>"
                 f"Lap Duration: {duration2:.2f}s<br>"
                 f"Sector 1: {sec12:.2f}s<br>"
                 f"Sector 2: {sec22:.2f}s<br>"
                 f"Sector 3: {sec32:.2f}s<br>"
                 f"Speed Trap: {speed_trap2} km/h<br>"
                 f"Out Lap: {out_lap2}")
    fig.add_annotation(
        text=lap_info2,
        xref="paper", yref="paper",
        x=0.75, y=0.95,
        showarrow=False,
        bordercolor="black",
        borderwidth=1,
        borderpad=5,
        bgcolor="white",
        opacity=0.8,
        align="left",
    )
    buffer = io.StringIO()
    fig.write_html(buffer)
    html_str = buffer.getvalue().encode('utf-8')
    buffer.close()
    return html_str

def tyres(session_key):
    sleep(1)
    response = urlopen(f'https://api.openf1.org/v1/stints?session_key={session_key}&tyre_age_at_start>=0')
    data = json.loads(response.read().decode('utf-8'))
    compound = data[0]['compound']
    start_age = data[0]['tyre_age_at_start']
    start_lap = data[0]['lap_start']
    end_lap = data[0]['lap_end']

def radios(driver, session_key):
    sleep(1)
    response = urlopen(f'https://api.openf1.org/v1/team_radio?session_key={session_key}&driver_number={driver}')
    data = json.loads(response.read().decode('utf-8'))
    dates = []
    urls = []
    for i in data:
        dates.append(i['date'][:-9])
        urls.append(i['recording_url'])
    return dates, urls

def temps(meeting_key):
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
    
    fig = make_subplots(rows=5, cols=1, shared_xaxes=True, subplot_titles=(
        'Air Temperature', 
        'Humidity', 
        'Rainfall', 
        'Track Temperature', 
        'Wind Speed'
    ))
    fig.add_trace(go.Scatter(y=air, mode='lines', name='Air Temperature (°C)', line=dict(color='blue')), row=1, col=1)
    fig.add_trace(go.Scatter(y=hum, mode='lines', name='Humidity (%)', line=dict(color='orange')), row=2, col=1)
    fig.add_trace(go.Scatter(y=rain, mode='lines', name='Rainfall (mm)', line=dict(color='green')), row=3, col=1)
    fig.add_trace(go.Scatter(y=track, mode='lines', name='Track Temperature (°C)', line=dict(color='red')), row=4, col=1)
    fig.add_trace(go.Scatter(y=winsp, mode='lines', name='Wind Speed (km/h)', line=dict(color='purple')), row=5, col=1)
    fig.update_layout(height=800, width=800, title_text="Weather Conditions", showlegend=False)
    fig.update_xaxes(title_text="Time")
    
    buffer = io.StringIO()
    fig.write_html(buffer)
    html_str = buffer.getvalue().encode('utf-8')
    buffer.close()
    return html_str

TOKEN = 'YOUR_TOKEN'
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))

@client.event
async def on_message(message):
    driver_nos = {1: 'VER', 11: 'PER', 16: 'LEC', 55: 'SAI', 44: 'HAM', 63: 'RUS', 14: 'ALO', 18: 'STR', 4: 'NOR', 81: 'PIA', 10: 'GAS', 31: 'OCO', 77: 'BOT', 24: 'ZHO', 20: 'MAG', 27: 'HUL', 22: 'TSU', 21: 'DEV', 23: 'ALB', 2: 'SAR', 50: 'COL', 34: 'BEA'}
    global session_key, circuit, year
    global meeting_key, country
    circuit = None
    if message.author == client.user:
        return
    if message.content.startswith('!hello'):
        await message.channel.send(f"Hello {message.author.display_name}!")
    if message.content.startswith('!drivers'):
        await message.channel.send(all_drivers)
    if message.content.startswith('!tracks'):
        await message.channel.send(tracks)
    if message.content.startswith('!country'):
        cmd, country = message.content.split()
    if message.content.startswith('!year'):
        cmd, year = message.content.split()
    if message.content.startswith('!circuit'):
        cmd, circuit = message.content.split()
    if message.content.startswith('!set'):
        session_key, meeting_key, ckt_short, country_name, x, y = important_values(country, year, circuit)
        await message.channel.send(y)
        await message.channel.send(x)
    if message.content.startswith('!plot_car'):
        cmd, driver = message.content.split()
        html_bytes = cars_data_plot(int(driver), session_key)
        with io.BytesIO(html_bytes) as buff:
            buff.seek(0)
            await message.channel.send("Plot for car " + driver_nos[int(driver)], file=discord.File(buff, 'interactive_plot.html'))
    if message.content.startswith('!plot_metric'):
        cmd, d1, d2, metric = message.content.split()
        html_bytes = compare_drivers(int(d1), int(d2), session_key, metric)
        with io.BytesIO(html_bytes) as buff:
            buff.seek(0)
            await message.channel.send("Comparison of Metrics of " + driver_nos[int(d1)] + " and " + driver_nos[int(d2)], file=discord.File(buff, 'interactive_plot.html'))
    if message.content.startswith('!laptimes'):
        cmd, driver, laps = message.content.split()
        html_bytes = plot_times(int(driver), int(laps), session_key)
        with io.BytesIO(html_bytes) as buff:
            buff.seek(0)
            await message.channel.send("Laptimes of " + driver_nos[int(driver)], file=discord.File(buff, 'interactive_plot.html'))
    if message.content.startswith('!lapsheet'):
        cmd, driver1, driver2, laps = message.content.split()
        html_bytes = times_comparison(int(driver1), int(driver2), int(laps), session_key)
        with io.BytesIO(html_bytes) as buff:
            buff.seek(0)
            await message.channel.send("Laptimes of " + driver_nos[int(driver1)] + " and " + driver_nos[int(driver2)], file=discord.File(buff, 'interactive_plot.html'))
    if message.content.startswith('!route'):
        cmd, driver, lap = message.content.split()
        html_bytes = plot_locations(int(driver), int(lap), session_key)
        with io.BytesIO(html_bytes) as buff:
            buff.seek(0)
            await message.channel.send("Path of " + driver_nos[int(driver)], file=discord.File(buff, 'interactive_plot.html'))
    if message.content.startswith('!locations'):
        cmd, driver1, driver2, lap = message.content.split()
        html_bytes = plot_comparison(int(driver1), int(driver2), int(lap), session_key)
        with io.BytesIO(html_bytes) as buff:
            buff.seek(0)
            await message.channel.send("Paths of " + driver_nos[int(driver1)] + " and " + driver_nos[int(driver2)], file=discord.File(buff, 'interactive_plot.html'))
    if message.content.startswith('!radios'):
        cmd, driver = message.content.split()
        dates, urls = radios(int(driver), session_key)
        for i in range(len(dates)):
            sleep(0.2)
            response = requests.get(urls[i])
            audio_file = io.BytesIO(response.content)
            audio_file.seek(0)
            discord_file = discord.File(audio_file, filename=f'{dates[i]}.mp3')
            await message.channel.send(f"Radio recording for {driver_nos[int(driver)]} on {dates[i]}", file=discord_file)
    if message.content.startswith('!temps'):
        html_bytes = temps(meeting_key)
        with io.BytesIO(html_bytes) as buff:
            buff.seek(0)
            await message.channel.send("Temparatures", file=discord.File(buff, 'interactive_plot.html'))

client.run(TOKEN)