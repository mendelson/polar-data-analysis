import os
import glob
import utils
import constants as const
from abc import ABC, abstractmethod

class AbstractDataProcessor(ABC):
    def __init__(self):
        self.processor_dict = {
                                'running': self.process_running,
                                'standard': self.process_standard_sport,
                                'distance_based': self.process_distance_based_sport,
                                'cycling': self.process_cycling
                            }

    def init_lists(self):
        self.sports_lists = {}

    def get_folder_files_list(self, path, file_name_pattern):
        os.chdir(path)
        
        training_sessions = []

        for file in glob.glob(file_name_pattern):
            training_sessions.append(file)

        return training_sessions

    @abstractmethod
    def process_data(self):
        pass

    @abstractmethod
    def split_sports(self, files_list):
        pass

    @abstractmethod
    def process_running(self, sport, data, exercise_index=0):
        pass

    @abstractmethod
    def process_standard_sport(self, sport, data, exercise_index=0):
        pass

    @abstractmethod
    def process_distance_based_sport(self, sport, data, exercise_index=0):
        pass

    @abstractmethod
    def process_cycling(self, sport, data, exercise_index=0):
        pass

    def do_nothing(self, sport, data, exercise_index=0):
        print(f'New sport detected! {sport}')

    def save_to_file(self):
        for sport in list(self.sports_lists.keys()):
            for json_object in self.sports_lists[sport]:
                utils.save_json_to_file(json_object, const.files[sport.lower()])
