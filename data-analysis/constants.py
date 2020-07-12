from datetime import datetime

birthday = datetime(1993, 7, 4)
ever_date = birthday

data_folder = '../data/'
downloaded_data_folder = 'polar-user-data-export/'
accesslink_data_folder = 'exercises_data/'

out_folder = 'processed_data/'
out_folder_path = f'../{out_folder}'

downloaded_data_path = f'{data_folder}{downloaded_data_folder}'
accesslink_data_path = f'{data_folder}{accesslink_data_folder}'

accesslink_summary_file_prefix = 'summary_data_'
accesslink_tcx_file_prefix = 'tcx_data_'

files = {
	'running': 'RUNNING.json',
	'strength_training': 'STRENGTH_TRAINING.json',
	'pool_swimming': 'POOL_SWIMMING.json',
	'open_water_swimming': 'OPEN_WATER_SWIMMING.json',
	'walking': 'WALKING.json',
	'other_indoor': 'OTHER_INDOOR.json',
	'treadmill_running': 'TREADMILL_RUNNING.json',
	'other_outdoor': 'OTHER_OUTDOOR.json',
	'cycling': 'CYCLING.json',
	'functional_training': 'FUNCTIONAL_TRAINING.json',
	'spinning': 'SPINNING.json',
	'swimming': 'SWIMMING.json',
	'futsal': 'FUTSAL.json',
	'mobility_static': 'MOBILITY_STATIC.json'
}

sport_processor = {
	'RUNNING': 'running',
	'STRENGTH_TRAINING': 'standard',
	'POOL_SWIMMING': 'distance_based',
	'OPEN_WATER_SWIMMING': 'distance_based',
	'WALKING': 'distance_based',
	'OTHER_INDOOR': 'standard',
	'TREADMILL_RUNNING': 'distance_based',
	'OTHER_OUTDOOR': 'distance_based',
	'CYCLING': 'cycling',
	'FUNCTIONAL_TRAINING': 'standard',
	'SPINNING': 'distance_based',
	'SWIMMING': 'distance_based',
	'FUTSAL': 'distance_based',
	'MOBILITY_STATIC': 'standard'
}


menu_delay = 5
empty_value = '~~~~~~~~~~'
day_link = 'https://flow.polar.com/training/day/'