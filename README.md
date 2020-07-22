# Polar Fitness Data Analysis

This is a personal project that I have been using in order to get some extra info about my activities that are not possible to get from the Polar Flow platform.

I have not put much effort on building the requirements file, but feel free to reach me if you want to use this repo and have any doubts you could not figure out by yourself.

The "accesslink-API" folder is a modified fork from Polar's repository. You should use it to get your data. Note that you can only get data from sessions performed after the creation of your API account. But do not worry, you can still download all your past data from [here](https://support.polar.com/en/how-to-download-all-your-data-from-polar-flow).

The "data-analysis" folder is the one I have developed from scratch. It deals with both data downloaded from the link above and data acquired through the API. This is the folder structure the code expects to be created (you should create it, I did not implement auto folder creation):

    .
    └── data                                        # holds all the data
          ├── daily_activity_data                   # holds daily activity data
          ├── exercises_data                        # holds all the sessions' data acquired from the Accesslink API
          ├── physical_data                         # holds the physical data acquired from the Accesslink API
          ├── polar-user-data-export                # holds all the data acquired from the download link I mentioned above
          ├── processed_data                        # this is where the treated data will be stored after the pre-processing
          └── user_data                             # holds all the user data

I have not uploaded any of my personal data, so fill the folders with your own data. Also, feel free to follow me on [Polar Flow](https://flow.polar.com/training/profiles/3142224) and [Strava](https://www.strava.com/athletes/9485255)

If you got everything correctly setup, you should just run
```
python data-analysis\main.py
```

or double-click the __data-analysis\RUNME.bat__ file.

Once again: if you are having trouble running this code, feel free to reach me.