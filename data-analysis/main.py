from DatabaseBuilder import *
from Analyser import *
from time import sleep
from datetime import datetime
import constants as const
import utils

def show_main_menu():
    utils.clear()
    print('Choose an option:')
    print(' 1 => Go to analysis')
    print(' 2 => Build database')
    print('---------------')
    print('-1 => Exit')

def show_sports_menu():
    utils.clear()
    print('Choose sport:')
    print(' 0 => All')

    sports = list(const.files.keys())
    for idx, sport in enumerate(sports):
        if idx + 1 < 10:
            print(f' {idx+1} => {sport}')
        else:
            print(f'{idx+1} => {sport}')
    print('---------------')
    print('-1 => Go back')

def process_sport_choice(sport_idx):
    sports = list(const.files.keys())

    try:
        sport = sports[sport_idx - 1]
    except:
        show_invalid_option()
        return

    if sport_idx == 0:
        sessions_count_menu()
    else:
        processor = const.sport_processor[sport.upper()]

        {
            'running': running_menu,
            'standard': standard_sport_menu,
            'distance_based': distance_based_sport_menu,
            'cycling': cycling_menu
        }.get(processor, show_invalid_option)(sport)

def define_timespan():
    print('Enter start date (inclusive)')
    start_date = utils.get_date_from_keyboard()
    print('Enter end date (inclusive)')
    end_date = utils.get_end_of_day(utils.get_date_from_keyboard())
    return start_date, end_date

def ask_for_timespan():
    quit_menu = False
    while not quit_menu:
        utils.clear()
        print('Choose the timespan you want to analyse:')
        print(' 1 => Since the beginning')
        print(' 2 => A specific timespan')
        print('---------------')
        print('-1 => Go back')
        option = int(input('> '))

        if option == 1:
            return const.ever_date, utils.get_end_of_day(datetime.now())
        elif option == 2:
            return define_timespan()
        elif option == -1:
            quit_menu = True
        else:
            show_invalid_option()
    return 'quit', 'quit'

def sessions_count_menu():
    quit_menu = False
    while not quit_menu:
        utils.clear()
        print('Choose an option:')
        print(' 1 => Get sessions count since the beginning')
        print(' 2 => Get sessions count in time interval')
        print('---------------')
        print('-1 => Go back')
        option = int(input('> '))

        if option == 1:
            an.show_all_counts()
        elif option == 2:
            start_date, end_date = define_timespan()
            an.show_all_counts_in_interval(start_date, end_date)
        elif option == -1:
            quit_menu = True
        else:
            show_invalid_option()

def running_menu(sport):
    quit_menu = False
    start_date, end_date = ask_for_timespan()
    if start_date == 'quit':
        quit_menu = True

    while not quit_menu:
        utils.clear()
        print(f'========== {sport} ==========')
        print(f'Start date: {start_date.strftime("%Y-%m-%d+%H_%M_%S_%f")}')
        print(f'End date: {end_date.strftime("%Y-%m-%d+%H_%M_%S_%f")}')
        print('Choose an option:')
        print(' 0 => Get all sessions')
        print(' 1 => Get longest distances')
        print(' 2 => Get most time consuming sessions')
        print(' 3 => Get best times in distance')
        print(' 4 => Get highest average speeds')
        print(' 5 => Get highest average heart rates')
        print('---------------')
        print('-1 => Go back')
        best = int(input('> '))

        if best == 0:
            an.show_all(sport, start_date, end_date)
        elif best == 1:
            amount = get_how_many()
            an.show_top_distances(sport, amount, start_date, end_date)
        elif best == 2:
            amount = get_how_many()
            an.show_top_time_consuming(sport, amount, start_date, end_date)
        elif best == 3:
            amount = get_how_many()
            distance = int(input('Choose distance (5, 10, 15 or 21 km): '))
            an.show_top_time_in_distance(sport, amount, distance, start_date, end_date)
        elif best == 4:
            amount = get_how_many()
            an.show_top_avg_speeds(sport, amount, start_date, end_date)
        elif best == 5:
            amount = get_how_many()
            an.show_top_avg_heart_rates(sport, amount, start_date, end_date)
        elif best == -1:
            quit_menu = True
        else:
            show_invalid_option()

def standard_sport_menu(sport):
    quit_menu = False
    start_date, end_date = ask_for_timespan()
    if start_date == 'quit':
        quit_menu = True

    while not quit_menu:
        utils.clear()
        print(f'========== {sport} ==========')
        print(f'Start date: {start_date.strftime("%Y-%m-%d+%H_%M_%S_%f")}')
        print(f'End date: {end_date.strftime("%Y-%m-%d+%H_%M_%S_%f")}')
        print('Choose an option:')
        print(' 0 => Get all sessions')
        print(' 1 => Get most time consuming sessions')
        print(' 2 => Get highest average heart rates')
        print('---------------')
        print('-1 => Go back')
        best = int(input('> '))

        if best == 0:
            an.show_all(sport, start_date, end_date)
        elif best == 1:
            amount = get_how_many()
            an.show_top_time_consuming(sport, amount, start_date, end_date)
        elif best == 2:
            amount = get_how_many()
            an.show_top_avg_heart_rates(sport, amount, start_date, end_date)
        elif best == -1:
            quit_menu = True
        else:
            show_invalid_option()

def distance_based_sport_menu(sport):
    quit_menu = False
    start_date, end_date = ask_for_timespan()
    if start_date == 'quit':
        quit_menu = True

    while not quit_menu:
        utils.clear()
        print(f'========== {sport} ==========')
        print(f'Start date: {start_date.strftime("%Y-%m-%d+%H_%M_%S_%f")}')
        print(f'End date: {end_date.strftime("%Y-%m-%d+%H_%M_%S_%f")}')
        print('Choose an option:')
        print(' 0 => Get all sessions')
        print(' 1 => Get longest distances')
        print(' 2 => Get most time consuming sessions')
        print(' 3 => Get highest average speeds')
        print(' 4 => Get highest average heart rates')
        print('---------------')
        print('-1 => Go back')
        best = int(input('> '))

        if best == 0:
            an.show_all(sport, start_date, end_date)
        elif best == 1:
            amount = get_how_many()
            an.show_top_distances(sport, amount, start_date, end_date)
        elif best == 2:
            amount = get_how_many()
            an.show_top_time_consuming(sport, amount, start_date, end_date)
        elif best == 3:
            amount = get_how_many()
            an.show_top_avg_speeds(sport, amount, start_date, end_date)
        elif best == 4:
            amount = get_how_many()
            an.show_top_avg_heart_rates(sport, amount, start_date, end_date)
        elif best == -1:
            quit_menu = True
        else:
            show_invalid_option()

def cycling_menu(sport):
    quit_menu = False
    start_date, end_date = ask_for_timespan()
    if start_date == 'quit':
        quit_menu = True

    while not quit_menu:
        utils.clear()
        print(f'========== {sport} ==========')
        print(f'Start date: {start_date.strftime("%Y-%m-%d+%H_%M_%S_%f")}')
        print(f'End date: {end_date.strftime("%Y-%m-%d+%H_%M_%S_%f")}')
        print('Choose an option:')
        print(' 0 => Get all sessions')
        print(' 1 => Get longest distances')
        print(' 2 => Get most time consuming sessions')
        print(' 3 => Get best times in distance')
        print(' 4 => Get highest average speeds')
        print(' 5 => Get highest average heart rates')
        print('---------------')
        print('-1 => Go back')
        best = int(input('> '))

        if best == 0:
            an.show_all(sport, start_date, end_date)
        elif best == 1:
            amount = get_how_many()
            an.show_top_distances(sport, amount, start_date, end_date)
        elif best == 2:
            amount = get_how_many()
            an.show_top_time_consuming(sport, amount, start_date, end_date)
        elif best == 3:
            amount = get_how_many()
            distance = int(input('Choose distance (10, 30, 60 or 100 km): '))
            an.show_top_time_in_distance(sport, amount, distance, start_date, end_date)
        elif best == 4:
            amount = get_how_many()
            an.show_top_avg_speeds(sport, amount, start_date, end_date)
        elif best == 5:
            amount = get_how_many()
            an.show_top_avg_heart_rates(sport, amount, start_date, end_date)
        elif best == -1:
            quit_menu = True
        else:
            show_invalid_option()

def show_invalid_option(foo=''):
    print('Invalid option, try again!')
    sleep(const.menu_delay)

def get_how_many():
    return int(input('How many results do you want? '))

# This is the function to show the menu.
# Yes, it is big and weird, deal with it.
if __name__ == '__main__':

    exit = False
    while not exit:
        show_main_menu()
        option = int(input('> '))

        if option == 1:
            an = Analyser()

            main_menu = False
            while not main_menu:
                show_sports_menu()
                sport_idx = int(input('> '))
                if sport_idx == -1:
                    main_menu = True
                else:
                    process_sport_choice(sport_idx)
                ############################################

        elif option == 2:
            db = DatabaseBuilder()
            sleep(const.menu_delay)
        elif option == -1:
            exit = True
        else:
            show_invalid_option()