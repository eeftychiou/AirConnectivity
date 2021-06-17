
import math
from itertools import islice
from sortedcontainers import SortedDict
import pandas as pd

#https://introcs.cs.princeton.edu/python/12types/greatcircle.py.html
def gcd(pointA, pointB):

    x1 = pointA[0]  #Lat
    y1 = pointA[1]  #lon
    x2 = pointB[0]
    y2 = pointB[1]

    # The following formulas assume that angles are expressed in radians.
    # So convert to radians.

    x1 = math.radians(x1)
    y1 = math.radians(y1)
    x2 = math.radians(x2)
    y2 = math.radians(y2)

    # Compute using the law of cosines.

    # Great circle distance in radians
    angle1 = math.acos(math.sin(x1) * math.sin(x2) \
                       + math.cos(x1) * math.cos(x2) * math.cos(y1 - y2))

    # Convert back to degrees.
    angle1 = math.degrees(angle1)

    # Each degree on a great circle of Earth is 60 nautical miles.
    distance1 = 60.0 * angle1

    return distance1

def computeTime(pointA, PointB):
    # up to xxxx = speed in nm/hr
    speed = SortedDict ( {
        500: 300,
        1500: 395,
        2500: 433,
        3500: 450,
        4500: 462,
        5500: 467,
        6500: 477,
        7500: 487,
        8500: 500
    })

    distance = gcd(pointA, PointB)

    curSpeed= closest(speed,distance)
    timetoDest= distance/curSpeed
    return timetoDest

def closest(sorted_dict, key):
    "Return closest value in `sorted_dict` to given `key`."

    assert len(sorted_dict) > 0
    keys = list(islice(sorted_dict.irange(minimum=key), 1))
    keys.extend(islice(sorted_dict.irange(maximum=key, reverse=True), 1))
    return sorted_dict[min(keys, key=lambda k: abs(key - k))]



def load_raw_ECTL_flights(fname):
    header_list = ["ECTRL_ID", "ADEP", "ADEP_Latitude", "ADEP_Longitude", "ADES", "ADES_Latitude", "ADES_Longitude",
                   "FILED_OFF_BLOCK_TIME", "FILED_ARRIVAL_TIME",
                   "ACTUAL_OFF_BLOCK_TIME", "ACTUAL_ARRIVAL_TIME", "AC_Type", "AC_Operator", "AC_Registration",
                   "ICAO_Flight_Type", "STATFOR_Market_Segment", "Requested_FL", "Actual_Distance_Flown"]
    airc_ls = []
    df_chunk = pd.read_csv('data/'+fname,
                           parse_dates=['FILED_OFF_BLOCK_TIME', 'FILED_ARRIVAL_TIME', 'ACTUAL_OFF_BLOCK_TIME',
                                        'ACTUAL_ARRIVAL_TIME'], dayfirst=True,
                           names=header_list, skiprows=1, chunksize=5000, nrows=10000,
                           dtype={'STATFOR_Market_Segment': 'category', 'AC_Type': 'category',
                                  'ICAO_Flight_Type': 'category', 'ADES': 'category', 'ADEP': 'category'})
    iC = 0
    for chunk in df_chunk:
        airc_ls.append(chunk)
        print("Chunk:", iC)
        print("Chunk:", chunk.shape)
        iC = iC + 1
    airc_df = pd.concat(airc_ls)
    print("File contains: ", airc_df.shape)
    airc_df = airc_df[airc_df.STATFOR_Market_Segment.isin(["Traditional Scheduled", "Lowcost"])]
    print("LCC and FSC: ", airc_df.shape)

    return airc_df