from unittest import TestCase
import numpy as np
from collections import defaultdict

import airctools as ac

points = {
    "KOAK": (37.71667, -122.21667),
    "KJFK": (40.64028, -73.77833),
    "OMDB": (25.24917, 55.36),
    "EGSS": (51.885, 0.235),
    "VOMM": (12.99361, 80.17694),
    "HEMA": (25.55806, 34.58306),
    "KMCO": (28.43333, -81.31667),
    "LTBA": (40.97611, 28.81417),
    "GMFF": (33.92722, -4.97778),
    "LEPA": (39.55167, 2.73889),
    "EDDF": (50.03333,	8.57056),
    "LCLK": (34.87889,	33.63028),
    "LGAV": (37.93667,	23.94444)

}

distance = defaultdict(dict)
distance['KOAK']['KJFK'] = 2238
distance['KOAK']['OMDB'] = 7035
distance['KOAK']['EGSS'] = 4655
distance['KOAK']['VOMM'] = 7520
distance['KOAK']['HEMA'] = 6801
distance['KOAK']['KMCO'] = 2118
distance['KOAK']['LTBA'] = 5835
distance['KOAK']['GMFF'] = 5274
distance['KOAK']['LEPA'] = 5278
distance['HEMA']['LTBA'] = 967
distance['KJFK']['EDDF'] = 3350

class Test(TestCase):
    def test_compute_time(self):

        testcases=[('KJFK','EDDF', 7.65),
                   ('LCLK','LGAV',1.60)]
        res=np.zeros((2,1))

        for i, case in enumerate(testcases):
            res[i]=abs(ac.computeTime(points[case[0]],points[case[1]]) - case[2])

        if np.sum(res)>(0.5*len(testcases)):
            return False
        else:
            return True


    def test_gcd(self):

        res=np.zeros((10,10))

        for i, pts in enumerate(distance.items()):
            pt1=pts[0]
            for j,pts2 in enumerate(pts[1].items()):
                pt2=pts2[0]
                dist = pts2[1]
                TrueDist=distance[pt1][pt2]
                calcdist = ac.gcd(points[pt1],points[pt2])
                res[i][j]=abs(calcdist-dist)


        if np.sum(res)>1000:
            return False
        else:
            return True