from calculating_LLA import *

## Time Interval Specifications

time_period = date_time(2019, 12, 9, 12, 0, 0)  #start time jday(2019, 12, 9, 12, 0, 0)
days = 5                                        #5 days
interval = 1                                    #1 minute
time_steps = 5*24*60                            #5*24*60 #Total timesteps

# Example usage:
bottom_left = (-60.0, -120.0)                   # Replace with actual coordinates
top_right = (60.0, 120.0)                       # Replace with actual coordinates

# Reading the satellite names
satsnames = open('30sats.txt', 'r').readlines()

# Calculating LLA
LLA = calculating_LLA(time_steps, satsnames, time_period)

# Assuming LLA is defined somewhere else in the code
satellite_times = find_entry_exit_times(LLA, bottom_left, top_right)

# Saving the entry_exit_times in a file
saving_entry_exit_times(satellite_times, time_period, bottom_left, top_right)