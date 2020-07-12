import json
import constants as const
import os
import utils
import shutil
import math
from tqdm import tqdm
from .AbstractDataProcessor import AbstractDataProcessor

class DownloadedDataProcessor(AbstractDataProcessor):
    def __init__(self):
        super().__init__()

        # print(self.processor_dict)

        root = os.getcwd()

        self.init_lists()
        self.process_data()

        # print('Sports counting in downloaded files:')
        # utils.pretty_print_json(self.sports_count)

        os.chdir(root)

    def process_data(self):
        print('Processing downloaded files...')

        files_list = self.get_folder_files_list(const.downloaded_data_path, 'training-session*.json')

        # for file in files_list:
            # self.get_sport_from_dowloaded_file(file)

        # self.total_sessions += len(files_list)

        ### TODO ###
        # Separar por esporte
        # Se houver mais de um exercise em uma session, chame de sport='MULTI'
        # 
        self.split_sports(files_list)

    def split_sports(self, files_list):
        self.sports_count = {}
        for file in tqdm(files_list):
            with open(file, 'r') as f:
                data = json.load(f)


            # Check whether it is a multi-sport session
            if len(data['exercises']) != 1:
                # TODO: implement this!
                # Se houver mais de um exercise em uma session, chame de sport='MULTI'
                print(f'MULTI-SPORT SESSION DETECTED AT {file}: {len(data["exercises"])} sports in this session!')
            else:
                exercise_index = 0
                sport = data['exercises'][exercise_index]['sport']

                if sport not in self.sports_count:
                    self.sports_count[sport] = 1
                else:
                    self.sports_count[sport] += 1

            processor_type = const.sport_processor[sport]
            self.processor_dict.get(processor_type, self.do_nothing)(sport, data, exercise_index)

        self.save_to_file()

    def process_running(self, sport, data, exercise_index=0):
        if sport not in list(self.sports_lists.keys()):
            self.sports_lists[sport] = []

        filtered = {}

        filtered['start_time'] = utils.polar_datetime_to_python_datetime_str(data['exercises'][exercise_index]['startTime'])
        
        has_route = 'recordedRoute' in data['exercises'][0]['samples']
        if has_route:
            first_route_point = data['exercises'][0]['samples']['recordedRoute'][0]
            filtered['landmark'], filtered['state'], filtered['country'] = utils.get_initial_location(first_route_point, filtered['start_time'])
        else:
            filtered['landmark'], filtered['state'], filtered['country'] = (const.empty_value, const.empty_value, const.empty_value)

        # Checking for no distance recorded
        if 'distance' not in data['exercises'][exercise_index]:
            filtered['distance'] = 1 # if there is no distance recorded, I'll assume it is 1km
        else:
            filtered['distance'] = utils.get_km(data['exercises'][exercise_index]['distance'])

        filtered['duration'] = utils.polar_time_to_python_time(data['exercises'][exercise_index]['duration'])
        filtered['avg_speed'] = utils.round_speed(data['exercises'][exercise_index]['speed']['avg'])
        filtered['max_speed'] = utils.round_speed(data['exercises'][exercise_index]['speed']['max'])

        # Checking for zero speed
        if filtered['avg_speed'] == 0:
            filtered['avg_speed'] = utils.calculate_speed(filtered['distance'], filtered['duration'])
            filtered['max_speed'] = filtered['avg_speed']
        
        filtered['avg_pace'] = utils.get_pace(filtered['avg_speed'])
        filtered['max_pace'] = utils.get_pace(filtered['max_speed'])

        # Checking for no heart rate recorded
        if 'heartRate' not in data['exercises'][exercise_index]:
            filtered['avg_heart_rate'] = const.empty_value
            filtered['max_heart_rate'] = filtered['avg_heart_rate']
        else:
            filtered['avg_heart_rate'] = data['exercises'][exercise_index]['heartRate']['avg']
            filtered['max_heart_rate'] = data['exercises'][exercise_index]['heartRate']['max']

        filtered['age'] = utils.get_age(filtered['start_time'])

        filtered['body_max_heart_rate'] = 220 - filtered['age']

        try:
            filtered['avg_heart_rate_as_percentage'] = round(filtered['avg_heart_rate']/filtered['body_max_heart_rate']*10000)/100.0
            filtered['max_heart_rate_as_percentage'] = round(filtered['max_heart_rate']/filtered['body_max_heart_rate']*10000)/100.0
        except:
            filtered['avg_heart_rate_as_percentage'] = const.empty_value
            filtered['max_heart_rate_as_percentage'] = filtered['avg_heart_rate_as_percentage']
        
        if has_route:
            filtered['5km_time'], filtered['5km_avg_speed'], filtered['5km_avg_pace'] = utils.get_data_at_dist(5, data['exercises'][0]['samples']['distance'])
            filtered['10km_time'], filtered['10km_avg_speed'], filtered['10km_avg_pace'] = utils.get_data_at_dist(10, data['exercises'][0]['samples']['distance'])
            filtered['15km_time'], filtered['15km_avg_speed'], filtered['15km_avg_pace'] = utils.get_data_at_dist(15, data['exercises'][0]['samples']['distance'])
            filtered['21km_time'], filtered['21km_avg_speed'], filtered['21km_avg_pace'] = utils.get_data_at_dist(21, data['exercises'][0]['samples']['distance'])
        else:
            filtered['5km_time'], filtered['5km_avg_speed'], filtered['5km_avg_pace'] = (const.empty_value, const.empty_value, const.empty_value)
            filtered['10km_time'], filtered['10km_avg_speed'], filtered['10km_avg_pace'] = (const.empty_value, const.empty_value, const.empty_value)
            filtered['15km_time'], filtered['15km_avg_speed'], filtered['15km_avg_pace'] = (const.empty_value, const.empty_value, const.empty_value)
            filtered['21km_time'], filtered['21km_avg_speed'], filtered['21km_avg_pace'] = (const.empty_value, const.empty_value, const.empty_value)

        filtered['day_link'] = utils.get_day_link(filtered['start_time'])
        # utils.pretty_print_json(filtered)
        # input()

        self.sports_lists[sport].append(filtered)

    def process_standard_sport(self, sport, data, exercise_index=0):
        if sport not in list(self.sports_lists.keys()):
            self.sports_lists[sport] = []

        filtered = {}

        filtered['start_time'] = utils.polar_datetime_to_python_datetime_str(data['exercises'][exercise_index]['startTime'])
        
        has_route = 'recordedRoute' in data['exercises'][0]['samples']
        if has_route:
            first_route_point = data['exercises'][0]['samples']['recordedRoute'][0]
            filtered['landmark'], filtered['state'], filtered['country'] = utils.get_initial_location(first_route_point, filtered['start_time'])
        else:
            filtered['landmark'], filtered['state'], filtered['country'] = (const.empty_value, const.empty_value, const.empty_value)

        # Checking for no distance recorded
        if 'distance' not in data['exercises'][exercise_index]:
            filtered['distance'] = const.empty_value
        else:
            filtered['distance'] = utils.get_km(data['exercises'][exercise_index]['distance'])

        filtered['duration'] = utils.polar_time_to_python_time(data['exercises'][exercise_index]['duration'])

        # Checking for no heart rate recorded
        if 'heartRate' not in data['exercises'][exercise_index]:
            filtered['avg_heart_rate'] = const.empty_value
            filtered['max_heart_rate'] = filtered['avg_heart_rate']
        else:
            filtered['avg_heart_rate'] = data['exercises'][exercise_index]['heartRate']['avg']
            filtered['max_heart_rate'] = data['exercises'][exercise_index]['heartRate']['max']

        filtered['age'] = utils.get_age(filtered['start_time'])

        filtered['body_max_heart_rate'] = 220 - filtered['age']

        try:
            filtered['avg_heart_rate_as_percentage'] = round(filtered['avg_heart_rate']/filtered['body_max_heart_rate']*10000)/100.0
            filtered['max_heart_rate_as_percentage'] = round(filtered['max_heart_rate']/filtered['body_max_heart_rate']*10000)/100.0
        except:
            filtered['avg_heart_rate_as_percentage'] = const.empty_value
            filtered['max_heart_rate_as_percentage'] = filtered['avg_heart_rate_as_percentage']
        
        filtered['day_link'] = utils.get_day_link(filtered['start_time'])
        # utils.pretty_print_json(filtered)
        # input()

        self.sports_lists[sport].append(filtered)

    def process_distance_based_sport(self, sport, data, exercise_index=0):
        if sport not in list(self.sports_lists.keys()):
            self.sports_lists[sport] = []

        filtered = {}

        filtered['start_time'] = utils.polar_datetime_to_python_datetime_str(data['exercises'][exercise_index]['startTime'])
        
        has_route = 'recordedRoute' in data['exercises'][0]['samples']
        if has_route:
            first_route_point = data['exercises'][0]['samples']['recordedRoute'][0]
            filtered['landmark'], filtered['state'], filtered['country'] = utils.get_initial_location(first_route_point, filtered['start_time'])
        else:
            filtered['landmark'], filtered['state'], filtered['country'] = (const.empty_value, const.empty_value, const.empty_value)

        # Checking for no distance recorded
        if 'distance' not in data['exercises'][exercise_index]:
            filtered['distance'] = const.empty_value
        else:
            filtered['distance'] = utils.get_km(data['exercises'][exercise_index]['distance'])

        filtered['duration'] = utils.polar_time_to_python_time(data['exercises'][exercise_index]['duration'])

        try:
            filtered['avg_speed'] = utils.round_speed(data['exercises'][exercise_index]['speed']['avg'])
            filtered['max_speed'] = utils.round_speed(data['exercises'][exercise_index]['speed']['max'])
        except:
            try:
                filtered['avg_speed'] = utils.calculate_speed(filtered['distance'], filtered['duration'])
            except:
                filtered['avg_speed'] = const.empty_value
            filtered['max_speed'] = filtered['avg_speed']
        
        try:
            filtered['avg_pace'] = utils.get_pace(filtered['avg_speed'])
        except:
            filtered['avg_pace'] = const.empty_value

        # Checking for no heart rate recorded
        if 'heartRate' not in data['exercises'][exercise_index]:
            filtered['avg_heart_rate'] = const.empty_value
            filtered['max_heart_rate'] = filtered['avg_heart_rate']
        else:
            filtered['avg_heart_rate'] = data['exercises'][exercise_index]['heartRate']['avg']
            filtered['max_heart_rate'] = data['exercises'][exercise_index]['heartRate']['max']

        filtered['age'] = utils.get_age(filtered['start_time'])

        filtered['body_max_heart_rate'] = 220 - filtered['age']

        try:
            filtered['avg_heart_rate_as_percentage'] = round(filtered['avg_heart_rate']/filtered['body_max_heart_rate']*10000)/100.0
            filtered['max_heart_rate_as_percentage'] = round(filtered['max_heart_rate']/filtered['body_max_heart_rate']*10000)/100.0
        except:
            filtered['avg_heart_rate_as_percentage'] = const.empty_value
            filtered['max_heart_rate_as_percentage'] = filtered['avg_heart_rate_as_percentage']
        
        filtered['day_link'] = utils.get_day_link(filtered['start_time'])
        # utils.pretty_print_json(filtered)
        # input()

        self.sports_lists[sport].append(filtered)

    def process_cycling(self, sport, data, exercise_index=0):
        if sport not in list(self.sports_lists.keys()):
            self.sports_lists[sport] = []

        filtered = {}

        filtered['start_time'] = utils.polar_datetime_to_python_datetime_str(data['exercises'][exercise_index]['startTime'])
        
        has_route = 'recordedRoute' in data['exercises'][0]['samples']
        if has_route:
            first_route_point = data['exercises'][0]['samples']['recordedRoute'][0]
            filtered['landmark'], filtered['state'], filtered['country'] = utils.get_initial_location(first_route_point, filtered['start_time'])
        else:
            filtered['landmark'], filtered['state'], filtered['country'] = (const.empty_value, const.empty_value, const.empty_value)

        # Checking for no distance recorded
        if 'distance' not in data['exercises'][exercise_index]:
            filtered['distance'] = 1 # if there is no distance recorded, I'll assume it is 1km
        else:
            filtered['distance'] = utils.get_km(data['exercises'][exercise_index]['distance'])

        filtered['duration'] = utils.polar_time_to_python_time(data['exercises'][exercise_index]['duration'])
        filtered['avg_speed'] = utils.round_speed(data['exercises'][exercise_index]['speed']['avg'])
        filtered['max_speed'] = utils.round_speed(data['exercises'][exercise_index]['speed']['max'])

        # Checking for zero speed
        if filtered['avg_speed'] == 0:
            filtered['avg_speed'] = utils.calculate_speed(filtered['distance'], filtered['duration'])
            filtered['max_speed'] = filtered['avg_speed']
        
        filtered['avg_pace'] = utils.get_pace(filtered['avg_speed'])
        filtered['max_pace'] = utils.get_pace(filtered['max_speed'])

        # Checking for no heart rate recorded
        if 'heartRate' not in data['exercises'][exercise_index]:
            filtered['avg_heart_rate'] = const.empty_value
            filtered['max_heart_rate'] = filtered['avg_heart_rate']
        else:
            filtered['avg_heart_rate'] = data['exercises'][exercise_index]['heartRate']['avg']
            filtered['max_heart_rate'] = data['exercises'][exercise_index]['heartRate']['max']

        filtered['age'] = utils.get_age(filtered['start_time'])

        filtered['body_max_heart_rate'] = 220 - filtered['age']

        try:
            filtered['avg_heart_rate_as_percentage'] = round(filtered['avg_heart_rate']/filtered['body_max_heart_rate']*10000)/100.0
            filtered['max_heart_rate_as_percentage'] = round(filtered['max_heart_rate']/filtered['body_max_heart_rate']*10000)/100.0
        except:
            filtered['avg_heart_rate_as_percentage'] = const.empty_value
            filtered['max_heart_rate_as_percentage'] = filtered['avg_heart_rate_as_percentage']
        
        if has_route:
            filtered['10km_time'], filtered['10km_avg_speed'], filtered['10km_avg_pace'] = utils.get_data_at_dist(10, data['exercises'][0]['samples']['distance'])
            filtered['30km_time'], filtered['30km_avg_speed'], filtered['30km_avg_pace'] = utils.get_data_at_dist(30, data['exercises'][0]['samples']['distance'])
            filtered['60km_time'], filtered['60km_avg_speed'], filtered['60km_avg_pace'] = utils.get_data_at_dist(60, data['exercises'][0]['samples']['distance'])
            filtered['100km_time'], filtered['100km_avg_speed'], filtered['100km_avg_pace'] = utils.get_data_at_dist(100, data['exercises'][0]['samples']['distance'])
        else:
            filtered['10km_time'], filtered['10km_avg_speed'], filtered['10km_avg_pace'] = (const.empty_value, const.empty_value, const.empty_value)
            filtered['30km_time'], filtered['30km_avg_speed'], filtered['30km_avg_pace'] = (const.empty_value, const.empty_value, const.empty_value)
            filtered['60km_time'], filtered['60km_avg_speed'], filtered['60km_avg_pace'] = (const.empty_value, const.empty_value, const.empty_value)
            filtered['100km_time'], filtered['100km_avg_speed'], filtered['100km_avg_pace'] = (const.empty_value, const.empty_value, const.empty_value)

        filtered['day_link'] = utils.get_day_link(filtered['start_time'])
        # utils.pretty_print_json(filtered)
        # input()

        self.sports_lists[sport].append(filtered)