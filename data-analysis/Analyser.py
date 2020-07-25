import os
import constants as const
import utils
import pandas as pd
import plotly.express as px
from plotly.offline import plot
from datetime import datetime
from time import sleep

class Analyser(object):
    def __init__(self):
        root = os.getcwd()
        os.chdir(f'{const.data_folder}{const.out_folder}')
        pd.set_option('display.max_columns', None)

        self.prepare_dataframes()

        self.counts = {}

        for sport in self.df_dict.keys():
            self.counts[sport] = self.df_dict[sport].shape[0]

        os.chdir(root)

    def prepare_dataframes(self):
        self.df_dict = {}
        for sport in list(const.files.keys()):
            try:
                self.df_dict[sport] = utils.get_dataframe_from_file(const.files[sport])
            except:
                print(f'Failed to find {const.files[sport]} file')
                sleep(2)

    def __order_dict(self, input_dict):
        return {k: v for k, v in sorted(input_dict.items(), key=lambda item: item[1], reverse=True)}

    def show_all_counts(self):
        ordered_dict = self.__order_dict(self.counts)
        fig = px.bar(x=list(ordered_dict.keys()), y=list(ordered_dict.values()))
        fig.update_layout(title_text='Sports count since ever',
                            xaxis_title='Sport',
                            yaxis_title='# of sessions')
        plot(fig)

    def show_all_counts_in_interval(self, start_date, end_date):
        counts = {}

        for sport in self.df_dict.keys():
            counts[sport] = 0
            for _, row in self.df_dict[sport].iterrows():
                date = row['start_time']
                date = datetime.strptime(date, '%Y-%m-%d+%H_%M_%S_%f')
                if date >= start_date and date <= end_date:
                    counts[sport] += 1

        ordered_dict = self.__order_dict(counts)
        fig = px.bar(x=list(ordered_dict.keys()), y=list(ordered_dict.values()))
        fig.update_layout(title_text=f'Sports count between {start_date} and {end_date} (all inclusive)',
                            xaxis_title='Sport',
                            yaxis_title='# of sessions')
        plot(fig)

    def get_sessions_in_timespan(self, df, start_date, end_date):
        rows_list = []
        for _, row in df.iterrows():
            date = row['start_time']
            date = datetime.strptime(date, '%Y-%m-%d+%H_%M_%S_%f')
            if date >= start_date and date <= end_date:
                rows_list.append(True)
            else:
                rows_list.append(False)
        df = df[rows_list]
        return df
    
    def show_all(self, sport, start_date, end_date):
        df = self.df_dict[sport].copy(deep=False)
        df = self.get_sessions_in_timespan(df, start_date, end_date)
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'i-th session (0 started)'}, inplace=True)
        df = df.sort_values(by='start_time', ascending=False, ignore_index=True)
        utils.show_dataframe_in_web(df, 'All sessions')

    def show_top_distances(self, sport, how_many, start_date, end_date):
        df = self.df_dict[sport].copy(deep=False)
        df = self.get_sessions_in_timespan(df, start_date, end_date)
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'i-th session (0 started)'}, inplace=True)

        # Dealing with strings and ints
        df = df.replace(const.empty_value, 0)
        df = df.sort_values(by='distance', ascending=False, ignore_index=True).head(how_many)
        df = df.replace(0, const.empty_value)

        utils.show_dataframe_in_web(df, f'{how_many} longest sessions')

    def show_top_time_consuming(self, sport, how_many, start_date, end_date):
        df = self.df_dict[sport].copy(deep=False)
        df = self.get_sessions_in_timespan(df, start_date, end_date)
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'i-th session (0 started)'}, inplace=True)

        df = df.sort_values(by='duration', ascending=False, ignore_index=True).head(how_many)

        utils.show_dataframe_in_web(df, f'{how_many} most time consuming sessions')

    def show_top_time_in_distance(self, sport, how_many, distance, start_date, end_date):
        column = f'{distance}km_time'
        df = self.df_dict[sport].copy(deep=False)
        df = self.get_sessions_in_timespan(df, start_date, end_date)
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'i-th session (0 started)'}, inplace=True)

        df = df.sort_values(by=column, ascending=True, ignore_index=True).head(how_many)

        utils.show_dataframe_in_web(df, f'Best {distance}km time sessions')

    def show_top_avg_speeds(self, sport, how_many, start_date, end_date):
        df = self.df_dict[sport].copy(deep=False)
        df = self.get_sessions_in_timespan(df, start_date, end_date)
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'i-th session (0 started)'}, inplace=True)
        
        # Dealing with strings and ints
        df = df.replace(const.empty_value, 0)
        df = df.sort_values(by='avg_speed', ascending=False, ignore_index=True).head(how_many)
        df = df.replace(0, const.empty_value)

        utils.show_dataframe_in_web(df, f'Best {how_many} average speed in session')

    def show_top_avg_heart_rates(self, sport, how_many, start_date, end_date):
        df = self.df_dict[sport].copy(deep=False)
        df = self.get_sessions_in_timespan(df, start_date, end_date)
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'i-th session (0 started)'}, inplace=True)

        # Dealing with strings and ints
        df = df.replace(const.empty_value, 0)
        df = df.sort_values(by=['avg_heart_rate', 'avg_heart_rate_as_percentage', 'max_heart_rate', 'max_heart_rate_as_percentage'], ascending=False, ignore_index=True).head(how_many)
        df = df.replace(0, const.empty_value)

        utils.show_dataframe_in_web(df, f'{how_many} highest average heart rates in session')

    def show_landmarks_stats(self, sport, start_date, end_date):
        df = self.df_dict[sport].copy(deep=False)
        df = self.get_sessions_in_timespan(df, start_date, end_date)
        df.reset_index(inplace=True)
        df.rename(columns={'index': '# of sessions'}, inplace=True)

        df['duration'] = utils.duration_to_timedelta(df['duration'])

        if const.sport_processor[sport.upper()] == 'running' or const.sport_processor[sport.upper()] == 'distance_based' or const.sport_processor[sport.upper()] == 'cycling':
            # Dealing with strings
            df = df.replace({'distance': const.empty_value,
                             'duration': const.empty_value,
                             'avg_speed': const.empty_value}, 0)
            df = df.groupby(by='landmark').agg({'# of sessions': 'count',
                                                 'distance': 'sum',
                                                 'duration': 'sum',
                                                 'avg_speed': 'mean'
                                                 })
            df = df.sort_values(by=['# of sessions', 'distance', 'duration', 'avg_speed'], ascending=False, ignore_index=False)
        else:
            df = df.groupby(by='landmark').agg({'# of sessions': 'count',
                                                 'duration': 'sum'
                                                 })
            df = df.sort_values(by=['# of sessions', 'duration'], ascending=False, ignore_index=False)
        df['duration'] = utils.timedelta_to_duration(df['duration'])

        utils.show_dataframe_in_web(df, f'Landmark stats for {sport}')

    def show_state_stats(self, sport, start_date, end_date):
        df = self.df_dict[sport].copy(deep=False)
        df = self.get_sessions_in_timespan(df, start_date, end_date)
        df.reset_index(inplace=True)
        df.rename(columns={'index': '# of sessions'}, inplace=True)

        df['duration'] = utils.duration_to_timedelta(df['duration'])

        if const.sport_processor[sport.upper()] == 'running' or const.sport_processor[sport.upper()] == 'distance_based' or const.sport_processor[sport.upper()] == 'cycling':
            # Dealing with strings
            df = df.replace({'distance': const.empty_value,
                             'duration': const.empty_value,
                             'avg_speed': const.empty_value}, 0)
            df = df.groupby(by='state').agg({'# of sessions': 'count',
                                                 'distance': 'sum',
                                                 'duration': 'sum',
                                                 'avg_speed': 'mean'
                                                 })
            df = df.sort_values(by=['# of sessions', 'distance', 'duration', 'avg_speed'], ascending=False, ignore_index=False)
        else:
            df = df.groupby(by='state').agg({'# of sessions': 'count',
                                                 'duration': 'sum'
                                                 })
            df = df.sort_values(by=['# of sessions', 'duration'], ascending=False, ignore_index=False)
        df['duration'] = utils.timedelta_to_duration(df['duration'])

        utils.show_dataframe_in_web(df, f'State stats for {sport}')

    def show_country_stats(self, sport, start_date, end_date):
        df = self.df_dict[sport].copy(deep=False)
        df = self.get_sessions_in_timespan(df, start_date, end_date)
        df.reset_index(inplace=True)
        df.rename(columns={'index': '# of sessions'}, inplace=True)

        df['duration'] = utils.duration_to_timedelta(df['duration'])

        if const.sport_processor[sport.upper()] == 'running' or const.sport_processor[sport.upper()] == 'distance_based' or const.sport_processor[sport.upper()] == 'cycling':
            # Dealing with strings
            df = df.replace({'distance': const.empty_value,
                             'duration': const.empty_value,
                             'avg_speed': const.empty_value}, 0)
            df = df.groupby(by='country').agg({'# of sessions': 'count',
                                                 'distance': 'sum',
                                                 'duration': 'sum',
                                                 'avg_speed': 'mean'
                                                 })
            df = df.sort_values(by=['# of sessions', 'distance', 'duration', 'avg_speed'], ascending=False, ignore_index=False)
        else:
            df = df.groupby(by='country').agg({'# of sessions': 'count',
                                                 'duration': 'sum'
                                                 })
            df = df.sort_values(by=['# of sessions', 'duration'], ascending=False, ignore_index=False)
        df['duration'] = utils.timedelta_to_duration(df['duration'])

        utils.show_dataframe_in_web(df, f'Country stats for {sport}')