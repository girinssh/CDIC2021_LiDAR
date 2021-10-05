# -*- coding: utf-8 -*-
"""
Created on Thu Sep 23 16:05:30 2021

@author: tngus
"""

from lidar import LiDAR
import time
import numpy as np

class LiDARManager:

    POS_LEFT = 0
    POS_RIGHT = 1
    POS_BACK = 2
    
    DIR_LEFT2RIGHT = 1
    DIR_RIGHT2LEFT = -1
    
    def __init__(self, rpm:int, samp_rate:int, minAngle, maxAngle):
        self.rpm = rpm
        self.samp_rate = samp_rate
        
        self.lidars = [
                LiDAR("/dev/serial0", samp_rate=self.samp_rate),
                LiDAR("/dev/ttyAMA1", samp_rate=self.samp_rate),
                #LiDAR("/dev/ttyAMA2", samp_rate=self.samp_rate)
            ]
        
        # 편도로 가는 동안 몇개의 데이터를 수집해야하는가.
        self.rawPerOneway = int(30 * samp_rate / self.rpm)
        
        # 1개의 데이터를 수집할 때 몇초를 소모해야하는가. 
        self.secPerRaw = (float)(1 / samp_rate)
        
        
        # 편도에 몇초가 걸리는가
        self.secPerOneway = 30 / self.rpm
        self.secLimit = self.secPerOneway * 0.8
        
        self.angle_min = minAngle
        self.angle_max = maxAngle
        self.angle_range = maxAngle - minAngle
        self.angle_unit = self.angle_range / self.rawPerOneway
        
    # ret rawArray and dist Y array
    def getRaws(self, start: float, POS: int, DIR: int):
        #  print("getRaws ", POS, DIR)
        rawArray = []
        angleArray = []
        timeArray = []
        last = -1
        t = 0
        #if POS == 0 : print(self.secPerOneway * 0.9)
        while t < self.secLimit:
            last = time.time()
            t = last - start
            # if POS == 0:
            #     print(t, sep='\t')
            # #time을 계산하면서 rawArray에 집어넣는다. 
            # if last - start >= (index + 1) * self.secPerRaw:
            #     index += 1
            # if POS == 0: print(t)
            val = self.lidars[POS].read_data()
            if val >= 8 or val < 0.2:
                continue
            rawArray.append(val)
            angleArray.append((self.angle_min if DIR == self.DIR_LEFT2RIGHT else self.angle_max) + DIR * self.angle_range * np.sin(2*t*np.pi))
            timeArray.append(t)
        return POS, np.array([rawArray, angleArray, timeArray])
