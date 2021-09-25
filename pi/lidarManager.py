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
                #lidar("/dev/ttyAMA2", samp_rate=samp_rate)
            ]
        
        # 편도로 가는 동안 몇개의 데이터를 수집해야하는가.
        self.rawPerOneway = int(60 / (self.rpm * 2) * samp_rate)
        
        # 1개의 데이터를 수집할 때 몇초를 소모해야하는가. 
        self.secPerRaw = (float)(1 / samp_rate)
        self.angle_min = minAngle
        self.angle_max = maxAngle
        self.angle_range = maxAngle - minAngle
        self.angle_unit = self.angle_range / self.rawPerOneway
        
    
    def getRaws(self, POS: int, DIR: int):
        print("getRaws ", POS, DIR)
        rawArray = [-1]*self.rawPerOneway
        angleArray = [-1]*self.rawPerOneway
        index = 0
        last = -1
        start = time.time()
        while index < self.rawPerOneway - 1:
            last = time.time()
            #time을 계산하면서 rawArray에 집어넣는다. 
            if last - start < (index + 1) * self.secPerRaw:
                rawArray[index] = self.lidars[POS].read_data()
                angleArray[index] =  DIR *(self.angle_unit * index) + (self.angle_min \
                    if DIR == LiDARManager.DIR_LEFT2RIGHT else self.angle_max)
            index += 1

        return np.array([rawArray, angleArray])
