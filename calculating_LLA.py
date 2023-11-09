from sgp4.api import Satrec
from sgp4.api import jday
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv

import pyproj

import numpy as np

import ray

class date_time:
  def __init__(self, year, month, date, hour, minute, second):
    self.year = year
    self.month = month
    self.date = date
    self.hour = hour
    self.minute = minute
    self.second = second

# Define a remote function to compute the squares of elements in a sub-array
@ray.remote
def single_LLA(s, t, time_steps, time_period):

    satellite = Satrec.twoline2rv(s, t)
    LLA = np.zeros((time_steps, 3), dtype=float)
    e, r, v = 0.0, np.zeros(3, dtype=float), np.zeros(3, dtype=float)

    ecef = pyproj.Proj(proj="geocent", ellps="WGS84", datum="WGS84")
    lla = pyproj.Proj(proj="latlong", ellps="WGS84", datum="WGS84")

    for j in range(time_steps):
        jd, fr = jday(time_period.year, time_period.month, time_period.date, time_period.hour, j, time_period.second)
        e, r, v = satellite.sgp4(jd, fr)

        LLA[j][0], LLA[j][1], LLA[j][2] = pyproj.transform(ecef, lla, r[0], r[1], r[2], radians=False)

    return LLA

def calculating_LLA(time_steps, satsnames, time_period):
    num_of_sats = int(len(satsnames)/2)

    # Initialize Ray
    ray.init()

    LLA = ray.get([single_LLA.remote(satsnames[2*i], satsnames[2*i+1], time_steps, time_period) for i in range(num_of_sats)])
    
    ray.shutdown()

    return LLA

@ray.remote
def find_entry_exit_times_single(trajectory, bottom_left, top_right):
    def is_within_area(point, bottom_left, top_right):
        lat, lon, _ = point
        return (bottom_left[0] <= lat <= top_right[0]) and (bottom_left[1] <= lon <= top_right[1])
    
    inside = False
    entry_time = None
    entry_exit_times = []

    for time, point in enumerate(trajectory):
        if is_within_area(point, bottom_left, top_right):
            if not inside:
                inside = True
                entry_time = time
        else:
            if inside:
                inside = False
                entry_exit_times.append((entry_time, time - 1))
                entry_time = None

    if inside and entry_time is not None:
            entry_exit_times.append((entry_time, len(trajectory) - 1))

    return entry_exit_times

def find_entry_exit_times(LLA, bottom_left, top_right):

    ray.init()
       
    entry_exit_times_all = ray.get([find_entry_exit_times_single.remote(trajectory, bottom_left, top_right) for trajectory in LLA])
    
    ray.shutdown()
  
    return entry_exit_times_all

def saving_entry_exit_times(satellite_times, time_period, bottom_left, top_right):

    s =  "Data for satellites entering and exiting the region between"+ str(bottom_left) + "and" + str(top_right) + "coordinates\n from date " + str(time_period.date) +"/" + str(time_period.month)+"/" + str(time_period.year) + "and time " + str(time_period.hour) +":"+ str(time_period.minute) +":"+ str(time_period.second) + "every minute is as follows"   
    file = open('results.txt', 'w')
    file.write(s)
    for sat_idx, time in enumerate(satellite_times):
        # print(f"Satellite {sat_idx} entered at time and exited at")
        s = "Satellite "+str(sat_idx)+" entered at time and exited at\n"
        file.write(s)
        for i in time:
            file.write(str(i))
        file.write("\n")
        