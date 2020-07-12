import constants as const
import os

from processors.DownloadedDataProcessor import *
from processors.AccesslinkDataProcessor import *

class DatabaseBuilder(object):
    def __init__(self):
        self.clean_out_folder()

        print('Initializing data cleaning...')

        d = DownloadedDataProcessor()
        a = AccesslinkDataProcessor()

        print('Data cleaning done!')

    def clean_out_folder(self):
        print('Running environment setup.')

        root = os.getcwd()

        folder = f'{const.data_folder}{const.out_folder}'
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

        os.chdir(root)

    