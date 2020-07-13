#!/usr/bin/env python

from __future__ import print_function

import utils
from accesslink import AccessLink
from datetime import datetime

try:
    input = raw_input
except NameError:
    pass


CONFIG_FILENAME = 'config.yml'


class PolarAccessLinkExample(object):
    """Example application for Polar Open AccessLink v3."""

    def __init__(self):
        self.config = utils.load_config(CONFIG_FILENAME)

        if 'access_token' not in self.config:
            print('Authorization is required. Run authorization.py first.')
            return

        self.accesslink = AccessLink(client_id=self.config['client_id'],
                                     client_secret=self.config['client_secret'])

        self.running = True
        self.show_menu()

    def show_menu(self):
        while self.running:
            print('\nChoose an option:\n' +
                  '-----------------------\n' +
                  ' 1 => Get data\n' +
                  ' 2 => Revoke access token\n' +
                  '-1 => Exit\n' +
                  '-----------------------')
            self.get_menu_choice()

    def get_menu_choice(self):
        choice = input('> ')
        {
            '1': self.get_all_data,
            # '1': self.get_user_information,
            # '2': self.check_available_data,
            '2': self.revoke_access_token,
            '-1': self.exit
        }.get(choice, self.get_menu_choice)()

    def get_all_data(self):
        self.get_user_information()
        self.check_available_data()

    def get_user_information(self):
        user_info = self.accesslink.users.get_information(user_id=self.config['user_id'],
                                                          access_token=self.config['access_token'])
        print('==========\tUSER INFORMATION\t==========')
        utils.pretty_print_json(user_info)
        utils.save_json_to_file(user_info, f'user_data/user_data_{datetime.today().strftime("%Y-%m-%d")}.json')

    def check_available_data(self):
        available_data = self.accesslink.pull_notifications.list()

        print('==========\tDATA\t==========')

        if not available_data:
            print('No new data available.')
            return

        print('Available data:')
        utils.pretty_print_json(available_data)

        for item in available_data['available-user-data']:
            if item['data-type'] == 'EXERCISE':
                self.get_exercises()
            elif item['data-type'] == 'ACTIVITY_SUMMARY':
                self.get_daily_activity()
            elif item['data-type'] == 'PHYSICAL_INFORMATION':
                self.get_physical_info()

    def revoke_access_token(self):
        self.accesslink.users.delete(user_id=self.config['user_id'],
                                     access_token=self.config['access_token'])

        del self.config['access_token']
        del self.config['user_id']
        utils.save_config(self.config, CONFIG_FILENAME)

        print('Access token was successfully revoked.')

        self.exit()

    def exit(self):
        self.running = False

    def get_exercises(self):
        transaction = self.accesslink.training_data.create_transaction(user_id=self.config['user_id'],
                                                                       access_token=self.config['access_token'])
        if not transaction:
            print('No new exercises available.')
            return

        resource_urls = transaction.list_exercises()['exercises']

        for url in resource_urls:
            exercise_summary = transaction.get_exercise_summary(url)
            gpx_data = transaction.get_gpx(url)
            tcx_data = transaction.get_tcx(url)
            hr_data = transaction.get_heart_rate_zones(url)
            samples_data = transaction.get_available_samples(url)
            sample_data = transaction.get_samples(url)

            print('Exercise summary:')
            utils.pretty_print_json(exercise_summary)
            time = utils.polar_datetime_to_python_datetime_str(str(exercise_summary['start-time']))
            utils.save_json_to_file(exercise_summary, f'exercises_data/summary_data_{time}.json')
            if gpx_data: # not empty dict. If there is no data, this variable will have '{}' value
            	utils.save_json_to_file(utils.xml_to_dict(gpx_data), f'exercises_data/gpx_data_{time}.json')
            if tcx_data:
            	utils.save_json_to_file(utils.xml_to_dict(tcx_data), f'exercises_data/tcx_data_{time}.json')
            if hr_data:
            	utils.save_json_to_file(hr_data, f'exercises_data/hr_data_{time}.json')
            if samples_data:
            	utils.save_json_to_file(samples_data, f'exercises_data/samples_data_{time}.json')
            if sample_data:
            	utils.save_json_to_file(sample_data, f'exercises_data/sample_data_{time}.json')

        transaction.commit()

    def get_daily_activity(self):
        transaction = self.accesslink.daily_activity.create_transaction(user_id=self.config['user_id'],
                                                                        access_token=self.config['access_token'])
        if not transaction:
            print('No new daily activity available.')
            return

        resource_urls = transaction.list_activities()['activity-log']

        for url in resource_urls:
            activity_summary = transaction.get_activity_summary(url)

            print('Activity summary:')
            utils.pretty_print_json(activity_summary)
            utils.save_json_to_file(activity_summary, f'daily_activity_data/daily_activity_data_{str(activity_summary["date"])}.json')

        transaction.commit()

    def get_physical_info(self):
        transaction = self.accesslink.physical_info.create_transaction(user_id=self.config['user_id'],
                                                                       access_token=self.config['access_token'])
        if not transaction:
            print('No new physical information available.')
            return

        resource_urls = transaction.list_physical_infos()['physical-informations']

        for url in resource_urls:
            physical_info = transaction.get_physical_info(url)

            print('Physical info:')
            utils.pretty_print_json(physical_info)
            time = utils.polar_datetime_to_python_datetime_str(str(physical_info['created']))
            utils.save_json_to_file(physical_info, f'physical_data/physical_data{time}.json')

        transaction.commit()


if __name__ == '__main__':
    PolarAccessLinkExample()
