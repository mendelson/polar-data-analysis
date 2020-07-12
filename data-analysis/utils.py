from datetime import datetime, timedelta
import math
import json
import constants as const
import pandas as pd
from geopy.geocoders import Nominatim
import unidecode
import tempfile
import webbrowser
from os import system, name

def polar_datetime_to_python_datetime_str(polar_dt):
    new_dt = polar_dt.replace('T', ' ')
    date_time_obj = datetime.strptime(new_dt, '%Y-%m-%d %H:%M:%S.%f')

    return date_time_obj.strftime('%Y-%m-%d+%H_%M_%S_%f')

def polar_time_to_python_time(polar_t):
    new_t = polar_t.replace('PT', '')
    new_t = new_t.replace('S', '')
    value = float(new_t)
    milliseconds = value%1
    td = timedelta(seconds=int(value), milliseconds=milliseconds*1000)

    return str(td)

def accesslink_time_to_python_time(accesslink_t):
    new_t = accesslink_t.replace('PT', '')
    new_t = new_t.replace('S', '')
    time = new_t.split('M')
    value = float(time[1])
    milliseconds = value%1
    td = timedelta(minutes=int(time[0]), seconds=int(value), milliseconds=milliseconds*1000)

    return str(td)

def get_km(meters):
    km = meters/1000
    km = math.floor(km*100)/100.0

    return km

def round_speed(speed):
    speed = round(speed*10)/10.0

    return speed

def get_pace(speed):
    pace = 60/speed # min/km
    pace = timedelta(minutes=pace)

    return str(pace)

def calculate_speed(distance, duration):
    time = duration.split(':')
    time[-1] = time[-1][:2] # Keep just the first 2 chars, that indicate the seconds (discarding milliseconds)
    time_hours = int(time[0]) + int(time[1])/60 + int(time[2])/3600

    speed = distance/time_hours
    speed = round_speed(speed)

    return speed

def pretty_print_json(data):
    print(json.dumps(data, indent=4))

def save_json_to_file(data, filename):
    with open(const.out_folder_path + filename, 'a+') as outfile:
        data = str(data).replace('\'', '"')
        # The following 3 substitutions are necessary to
        # make the polar flow day_link work
        data = data.replace('" ', '\' ')
        data = data.replace('="', '=\'')
        data = data.replace('">', '\'>')

        outfile.write(data)
        outfile.write('\n')
        # outfile.write(json.dumps(data, indent=4))

def get_dataframe_from_file(file):
    return pd.read_json(file, lines=True)

def get_age(date):
    date = datetime(int(date[0:4]), int(date[5:7]), int(date[8:10]))
    time_diff = (date - const.birthday)

    return int(time_diff.days/365)

def get_initial_location(first_route_point, file_id):
    lat = first_route_point['latitude']
    lon = first_route_point['longitude']
    geolocator = Nominatim(user_agent='my_analysis')
    
    got_location = False
    while not got_location:
        try:
            location = geolocator.reverse(f'{lat}, {lon}')
            got_location = True
        except:
            print(f'Warning: Retrying to get exercise {file_id}\'s location!')
            # print('Warning: Could not retrieve activity address for the current activity')
            # return '~~~~~~~~~~', '~~~~~~~~~~', '~~~~~~~~~~'

    try:
        landmark = location.raw['address']['tourism']
    except:
        try:
            landmark = location.raw['address']['natural']
        except:
            try:
                landmark = location.raw['address']['suburb']
            except:
                try:
                    landmark = location.raw['address']['city']
                except:
                    keys = list(location.raw['address'].keys())
                    landmark = location.raw['address'][keys[0]]
        
    state = location.raw['address']['state']
    country = location.raw['address']['country']

    return unidecode.unidecode(landmark), unidecode.unidecode(state), unidecode.unidecode(country)

def get_data_at_dist(km, dist_list):
    m = km*1000

    init_time = dist_list[0]['dateTime']
    init_time = datetime(int(init_time[0:4]), int(init_time[5:7]), int(init_time[8:10]),
                         int(init_time[11:13]), int(init_time[14:16]), int(init_time[17:19]),
                         int(init_time[20:])*1000)

    has_distance = False

    for moment in dist_list:
        try:
            if moment['value'] >= m:
                dist = moment['value']
                end_time = moment['dateTime']
                final_time = datetime(int(end_time[0:4]), int(end_time[5:7]), int(end_time[8:10]),
                                      int(end_time[11:13]), int(end_time[14:16]), int(end_time[17:19]),
                                      int(end_time[20:])*1000)
                time = final_time - init_time
                has_distance = True
                break
        except:
            pass

    if not has_distance:
        return const.empty_value, const.empty_value, const.empty_value

    avg_speed = km/(time.seconds/3600)
    avg_pace = 60/avg_speed
    avg_pace = timedelta(minutes=avg_pace)

    return str(time), round_speed(avg_speed), str(avg_pace)

def find_tcx_max_speed(laps):
    max_speed = 0

    for lap in laps:
        current_speed = float(lap['MaximumSpeed'])
        if current_speed > max_speed:
            max_speed = current_speed
    
    # Convert from m/s to km/h
    max_speed = max_speed*3.6

    return round_speed(max_speed)

def convert_tcx_laps_to_downloaded_format(laps):
    samples = []

    for lap in laps:
        for sample in lap['Track']['Trackpoint']:
            sample_dict = {
                            'dateTime': format_tcx_datetime_to_downloaded_datetime(sample['Time']),
                            'value': float(sample['DistanceMeters'])
                        }
            samples.append(sample_dict)

    return samples

def format_tcx_datetime_to_downloaded_datetime(tcx_datetime):
    tcx_datetime = tcx_datetime.replace('Z', '')
    return tcx_datetime[:-1]

def get_day_link(start_time):
     return f"<a href='{const.day_link}{get_day_link_format(start_time)}' target='_blank'>Polar Flow</a>"

def get_day_link_format(start_time):
    return f'{start_time[8:10]}.{start_time[5:7]}.{start_time[0:4]}'

def show_dataframe_in_web(df, message='Dataframe'):
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as f:
        url = 'file://' + f.name
        f.write(f'<h1>{message}</h1>')
        f.write(df.to_html(max_rows=None,
                           max_cols=None,
                           escape=False,
                           justify='center'
                           ))
    webbrowser.open(url)

def clear():
    # for windows
    if name == 'nt':
        _ = system('cls')
    # for mac and linux(here, os.name is 'posix') 
    else:
        _ = system('clear')

def get_date_from_keyboard():
    year = int(input('Enter year (yyyy) - TYPE "-1" FOR TODAY: '))

    if year == -1:
        return get_end_of_day(datetime.now())

    month = int(input('Enter month (mm): '))
    day = int(input('Enter day (dd): '))
    return datetime(year, month, day)

def get_end_of_day(day):
    end_of_day = datetime(day.year, day.month, day.day, 23, 59, 59, 999999)
    return end_of_day