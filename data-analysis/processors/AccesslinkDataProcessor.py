import json
import constants as const
import os
import utils
import shutil
import math
from tqdm import tqdm
from .AbstractDataProcessor import AbstractDataProcessor

class AccesslinkDataProcessor(AbstractDataProcessor):
    def __init__(self):
        super().__init__()

        root = os.getcwd()

        self.init_lists()
        self.process_data()

        # print('Sports counting in Accesslink files:')
        # utils.pretty_print_json(self.sports_count)

        os.chdir(root)

    def process_data(self):
        print('Processing accesslink files...')

        files_list = self.get_folder_files_list(const.accesslink_data_path,
                                                  f'{const.accesslink_summary_file_prefix}*.json')

        ### TODO ###
        # Separar por esporte
        # Se houver mais de um exercise em uma session, chame de sport='MULTI'
        # 
        self.split_sports(files_list)

    def split_sports(self, files_list):
        self.sports_count = {}
        for file in tqdm(files_list):
            self.current_file_id = file[len(const.accesslink_summary_file_prefix):len(const.accesslink_summary_file_prefix)+26]
            
            with open(file, 'r') as f:
                data = json.load(f)

            sport = data['detailed-sport-info']
            
            if sport not in self.sports_count:
                self.sports_count[sport] = 1
            else:
                self.sports_count[sport] += 1

            processor_type = const.sport_processor[sport]
            self.processor_dict.get(processor_type, self.do_nothing)(sport, data)

        self.save_to_file()

    def process_running(self, sport, data, exercise_index=0):
        if sport not in list(self.sports_lists.keys()):
            self.sports_lists[sport] = []

        filtered = {}

        tcx_file = f'{const.accesslink_tcx_file_prefix}{self.current_file_id}.json'

        filtered['start_time'] = self.current_file_id
        
        ### TODO:
        # Pegar a localização da primeira posição do percurso e descobrir o fuso-horário de lá
        # Os horários nos arquivos tcx estão em utc time zone

        with open(tcx_file, 'r') as f:
            tcx_data = json.load(f)

        has_route = False
        # if has_route:
        try:
            first_route_point = {
                                    'latitude': float(tcx_data['TrainingCenterDatabase']['Activities']['Activity']['Lap'][0]['Track']['Trackpoint'][0]['Position']['LatitudeDegrees']),
                                    'longitude': float(tcx_data['TrainingCenterDatabase']['Activities']['Activity']['Lap'][0]['Track']['Trackpoint'][0]['Position']['LongitudeDegrees'])
                                }

            utils.get_weather_data_file(first_route_point, self.current_file_id)
            has_route = True
            filtered['landmark'], filtered['state'], filtered['country'] = utils.get_initial_location(first_route_point, filtered['start_time'])
        except:
            try:
                first_route_point = {
                                        'latitude': float(tcx_data['TrainingCenterDatabase']['Activities']['Activity']['Lap'][0]['Track'][0]['Trackpoint'][0]['Position']['LatitudeDegrees']),
                                        'longitude': float(tcx_data['TrainingCenterDatabase']['Activities']['Activity']['Lap'][0]['Track'][0]['Trackpoint'][0]['Position']['LongitudeDegrees'])
                                    }

                utils.get_weather_data_file(first_route_point, self.current_file_id)
                has_route = True
                filtered['landmark'], filtered['state'], filtered['country'] = utils.get_initial_location(first_route_point, filtered['start_time'])
            except:
                filtered['landmark'], filtered['state'], filtered['country'] = (const.empty_value, const.empty_value, const.empty_value)

        # Checking for no distance recorded
        if 'distance' not in data:
            filtered['distance'] = 1 # if there is no distance recorded, I'll assume it is 1km
        else:
            filtered['distance'] = utils.get_km(data['distance'])

        tcx_laps = tcx_data['TrainingCenterDatabase']['Activities']['Activity']['Lap']

        filtered['duration'] = utils.accesslink_time_to_python_time(data['duration'])

        filtered['avg_speed'] = utils.calculate_speed(filtered['distance'], filtered['duration'])

        try:
            filtered['max_speed'] = utils.find_tcx_max_speed(tcx_laps)
        except:
            filtered['max_speed'] = filtered['avg_speed']
        
        filtered['avg_pace'] = utils.get_pace(filtered['avg_speed'])
        filtered['max_pace'] = utils.get_pace(filtered['max_speed'])

        # Checking for no heart rate recorded
        try:
            filtered['avg_heart_rate'] = data['heart-rate']['average']
            filtered['max_heart_rate'] = data['heart-rate']['maximum']
        except:
            filtered['avg_heart_rate'] = const.empty_value
            filtered['max_heart_rate'] = filtered['avg_heart_rate']
            
        filtered['age'] = utils.get_age(filtered['start_time'])

        filtered['body_max_heart_rate'] = 220 - filtered['age']

        try:
            filtered['avg_heart_rate_as_percentage'] = round(filtered['avg_heart_rate']/filtered['body_max_heart_rate']*10000)/100.0
            filtered['max_heart_rate_as_percentage'] = round(filtered['max_heart_rate']/filtered['body_max_heart_rate']*10000)/100.0
        except:
            filtered['avg_heart_rate_as_percentage'] = const.empty_value
            filtered['max_heart_rate_as_percentage'] = filtered['avg_heart_rate_as_percentage']
        
        if has_route:
            samples = utils.convert_tcx_laps_to_downloaded_format(tcx_laps)

            _, _, _, filtered['has_negative_split'] = utils.get_data_at_dist(filtered['distance'], samples)
            if filtered['has_negative_split'] == const.empty_value:
                _, _, _, filtered['has_negative_split'] = utils.get_data_at_dist(filtered['distance'] - 0.01, samples)

            filtered['5km_time'], filtered['5km_avg_speed'], filtered['5km_avg_pace'], filtered['5km_has_negative_split'] = utils.get_data_at_dist(5, samples)
            filtered['10km_time'], filtered['10km_avg_speed'], filtered['10km_avg_pace'], filtered['10km_has_negative_split'] = utils.get_data_at_dist(10, samples)
            filtered['15km_time'], filtered['15km_avg_speed'], filtered['15km_avg_pace'], filtered['15km_has_negative_split'] = utils.get_data_at_dist(15, samples)
            filtered['21km_time'], filtered['21km_avg_speed'], filtered['21km_avg_pace'], filtered['21km_has_negative_split'] = utils.get_data_at_dist(21, samples)
            filtered['42km_time'], filtered['42km_avg_speed'], filtered['42km_avg_pace'], filtered['42km_has_negative_split'] = utils.get_data_at_dist(42, samples)
        else:
            filtered['has_negative_split'] = const.empty_value
            filtered['5km_time'], filtered['5km_avg_speed'], filtered['5km_avg_pace'], filtered['5km_has_negative_split'] = (const.empty_value, const.empty_value, const.empty_value, const.empty_value)
            filtered['10km_time'], filtered['10km_avg_speed'], filtered['10km_avg_pace'], filtered['10km_has_negative_split'] = (const.empty_value, const.empty_value, const.empty_value, const.empty_value)
            filtered['15km_time'], filtered['15km_avg_speed'], filtered['15km_avg_pace'], filtered['15km_has_negative_split'] = (const.empty_value, const.empty_value, const.empty_value, const.empty_value)
            filtered['21km_time'], filtered['21km_avg_speed'], filtered['21km_avg_pace'], filtered['21km_has_negative_split'] = (const.empty_value, const.empty_value, const.empty_value, const.empty_value)
            filtered['42km_time'], filtered['42km_avg_speed'], filtered['42km_avg_pace'], filtered['42km_has_negative_split'] = (const.empty_value, const.empty_value, const.empty_value, const.empty_value)

        filtered['day_link'] = utils.get_day_link(filtered['start_time'])
        # utils.pretty_print_json(filtered)
        # input()

        self.sports_lists[sport].append(filtered)

    def process_standard_sport(self, sport, data, exercise_index=0):
        if sport not in list(self.sports_lists.keys()):
            self.sports_lists[sport] = []

        filtered = {}

        tcx_file = f'{const.accesslink_tcx_file_prefix}{self.current_file_id}.json'

        filtered['start_time'] = self.current_file_id

        try:
            with open(tcx_file, 'r') as f:
                tcx_data = json.load(f)
        except:
            pass

        has_route = False
        # if has_route:
        try:
            first_route_point = {
                                    'latitude': float(tcx_data['TrainingCenterDatabase']['Activities']['Activity']['Lap'][0]['Track']['Trackpoint'][0]['Position']['LatitudeDegrees']),
                                    'longitude': float(tcx_data['TrainingCenterDatabase']['Activities']['Activity']['Lap'][0]['Track']['Trackpoint'][0]['Position']['LongitudeDegrees'])
                                }
            utils.get_weather_data_file(first_route_point, self.current_file_id)
            has_route = True
            filtered['landmark'], filtered['state'], filtered['country'] = utils.get_initial_location(first_route_point, filtered['start_time'])
        except:
            filtered['landmark'], filtered['state'], filtered['country'] = (const.empty_value, const.empty_value, const.empty_value)

        # Checking for no distance recorded
        if 'distance' not in data:
            filtered['distance'] = const.empty_value
        else:
            filtered['distance'] = utils.get_km(data['distance'])

        filtered['duration'] = utils.accesslink_time_to_python_time(data['duration'])

        # Checking for no heart rate recorded
        try:
            filtered['avg_heart_rate'] = data['heart-rate']['average']
            filtered['max_heart_rate'] = data['heart-rate']['maximum']
        except:
            filtered['avg_heart_rate'] = const.empty_value
            filtered['max_heart_rate'] = filtered['avg_heart_rate']
            
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

        tcx_file = f'{const.accesslink_tcx_file_prefix}{self.current_file_id}.json'

        filtered['start_time'] = self.current_file_id
        
        ### TODO:
        # Pegar a localização da primeira posição do percurso e descobrir o fuso-horário de lá
        # Os horários nos arquivos tcx estão em utc time zone

        try:
            with open(tcx_file, 'r') as f:
                tcx_data = json.load(f)
        except:
            pass

        has_route = False
        # if has_route:
        try:
            first_route_point = {
                                    'latitude': float(tcx_data['TrainingCenterDatabase']['Activities']['Activity']['Lap'][0]['Track']['Trackpoint'][0]['Position']['LatitudeDegrees']),
                                    'longitude': float(tcx_data['TrainingCenterDatabase']['Activities']['Activity']['Lap'][0]['Track']['Trackpoint'][0]['Position']['LongitudeDegrees'])
                                }
            utils.get_weather_data_file(first_route_point, self.current_file_id)
            has_route = True
            filtered['landmark'], filtered['state'], filtered['country'] = utils.get_initial_location(first_route_point, filtered['start_time'])
        except:
            filtered['landmark'], filtered['state'], filtered['country'] = (const.empty_value, const.empty_value, const.empty_value)

        # Checking for no distance recorded
        if 'distance' not in data:
            filtered['distance'] = const.empty_value
        else:
            filtered['distance'] = utils.get_km(data['distance'])

        filtered['duration'] = utils.accesslink_time_to_python_time(data['duration'])

        try:
            filtered['avg_speed'] = utils.calculate_speed(filtered['distance'], filtered['duration'])
        except:
            filtered['avg_speed'] = const.empty_value

        try:
            filtered['max_speed'] = utils.find_tcx_max_speed(tcx_laps)
        except:
            filtered['max_speed'] = filtered['avg_speed']
        
        filtered['avg_pace'] = utils.get_pace(filtered['avg_speed'])

        # Checking for no heart rate recorded
        try:
            filtered['avg_heart_rate'] = data['heart-rate']['average']
            filtered['max_heart_rate'] = data['heart-rate']['maximum']
        except:
            filtered['avg_heart_rate'] = const.empty_value
            filtered['max_heart_rate'] = filtered['avg_heart_rate']
            
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

        tcx_file = f'{const.accesslink_tcx_file_prefix}{self.current_file_id}.json'

        filtered['start_time'] = self.current_file_id
        
        ### TODO:
        # Pegar a localização da primeira posição do percurso e descobrir o fuso-horário de lá
        # Os horários nos arquivos tcx estão em utc time zone

        with open(tcx_file, 'r') as f:
            tcx_data = json.load(f)

        has_route = False
        # if has_route:
        try:
            first_route_point = {
                                    'latitude': float(tcx_data['TrainingCenterDatabase']['Activities']['Activity']['Lap'][0]['Track']['Trackpoint'][0]['Position']['LatitudeDegrees']),
                                    'longitude': float(tcx_data['TrainingCenterDatabase']['Activities']['Activity']['Lap'][0]['Track']['Trackpoint'][0]['Position']['LongitudeDegrees'])
                                }
            utils.get_weather_data_file(first_route_point, self.current_file_id)
            has_route = True
            filtered['landmark'], filtered['state'], filtered['country'] = utils.get_initial_location(first_route_point, filtered['start_time'])
        except:
            filtered['landmark'], filtered['state'], filtered['country'] = (const.empty_value, const.empty_value, const.empty_value)

        # Checking for no distance recorded
        if 'distance' not in data:
            filtered['distance'] = 1 # if there is no distance recorded, I'll assume it is 1km
        else:
            filtered['distance'] = utils.get_km(data['distance'])

        tcx_laps = tcx_data['TrainingCenterDatabase']['Activities']['Activity']['Lap']

        filtered['duration'] = utils.accesslink_time_to_python_time(data['duration'])

        filtered['avg_speed'] = utils.calculate_speed(filtered['distance'], filtered['duration'])

        try:
            filtered['max_speed'] = utils.find_tcx_max_speed(tcx_laps)
        except:
            filtered['max_speed'] = filtered['avg_speed']
        
        filtered['avg_pace'] = utils.get_pace(filtered['avg_speed'])
        filtered['max_pace'] = utils.get_pace(filtered['max_speed'])

        # Checking for no heart rate recorded
        try:
            filtered['avg_heart_rate'] = data['heart-rate']['average']
            filtered['max_heart_rate'] = data['heart-rate']['maximum']
        except:
            filtered['avg_heart_rate'] = const.empty_value
            filtered['max_heart_rate'] = filtered['avg_heart_rate']
            
        filtered['age'] = utils.get_age(filtered['start_time'])

        filtered['body_max_heart_rate'] = 220 - filtered['age']

        try:
            filtered['avg_heart_rate_as_percentage'] = round(filtered['avg_heart_rate']/filtered['body_max_heart_rate']*10000)/100.0
            filtered['max_heart_rate_as_percentage'] = round(filtered['max_heart_rate']/filtered['body_max_heart_rate']*10000)/100.0
        except:
            filtered['avg_heart_rate_as_percentage'] = const.empty_value
            filtered['max_heart_rate_as_percentage'] = filtered['avg_heart_rate_as_percentage']
        
        if has_route:
            samples = utils.convert_tcx_laps_to_downloaded_format(tcx_laps)

            _, _, _, filtered['has_negative_split'] = utils.get_data_at_dist(filtered['distance'], samples)
            if filtered['has_negative_split'] == const.empty_value:
                _, _, _, filtered['has_negative_split'] = utils.get_data_at_dist(filtered['distance'] - 0.01, samples)

            filtered['10km_time'], filtered['10km_avg_speed'], filtered['10km_avg_pace'], filtered['10km_has_negative_split'] = utils.get_data_at_dist(10, samples)
            filtered['30km_time'], filtered['30km_avg_speed'], filtered['30km_avg_pace'], filtered['30km_has_negative_split'] = utils.get_data_at_dist(30, samples)
            filtered['60km_time'], filtered['60km_avg_speed'], filtered['60km_avg_pace'], filtered['60km_has_negative_split'] = utils.get_data_at_dist(60, samples)
            filtered['100km_time'], filtered['100km_avg_speed'], filtered['100km_avg_pace'], filtered['100km_has_negative_split'] = utils.get_data_at_dist(100, samples)
        else:
            filtered['has_negative_split'] = const.empty_value
            filtered['10km_time'], filtered['10km_avg_speed'], filtered['10km_avg_pace'], filtered['10km_has_negative_split'] = (const.empty_value, const.empty_value, const.empty_value, const.empty_value)
            filtered['30km_time'], filtered['30km_avg_speed'], filtered['30km_avg_pace'], filtered['30km_has_negative_split'] = (const.empty_value, const.empty_value, const.empty_value, const.empty_value)
            filtered['60km_time'], filtered['60km_avg_speed'], filtered['60km_avg_pace'], filtered['60km_has_negative_split'] = (const.empty_value, const.empty_value, const.empty_value, const.empty_value)
            filtered['100km_time'], filtered['100km_avg_speed'], filtered['100km_avg_pace'], filtered['100km_has_negative_split'] = (const.empty_value, const.empty_value, const.empty_value, const.empty_value)

        filtered['day_link'] = utils.get_day_link(filtered['start_time'])
        # utils.pretty_print_json(filtered)
        # input()

        self.sports_lists[sport].append(filtered)

    

    