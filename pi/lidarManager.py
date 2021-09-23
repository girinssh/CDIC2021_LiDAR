# -*- coding: utf-8 -*-
"""
Created on Thu Sep 23 16:05:30 2021

@author: tngus
"""

# import lidar
import time
import threading

class LiDARManager:

    POS_LEFT = 0
    POS_RIGHT = 1
    POS_BACK = 2
    
    
    STATE_FORWARD = 1
    STATE_BACKWARD = -1
    STATES = [STATE_FORWARD, STATE_BACKWARD]
    
    def __init__(self, rpm, samp_rate):
        self.rpm = rpm
        self.samp_rate = samp_rate
        
        self.state = LiDARManager.STATE_FORWARD
        
        # self.lidars = [
        #         lidar("/dev/serial0", samp_rate=samp_rate),
        #         lidar("/dev/ttyAMA1", samp_rate=samp_rate),
        #         lidar("/dev/ttyAMA2", samp_rate=samp_rate)
        #     ]
        
        self.distPerOneway = 60 / (self.rpm * 2) * samp_rate
    
    def getDistances(self, POS: int)->list:
        distArray = []
        angleArray = []
        
        if POS == LiDARManager.POS_LEFT:
            pass
        elif POS == LiDARManager.POS_RIGHT:
            pass
        elif POS == LiDARManager.POS_BACK:
            pass
        
        return []

    def setState(self, newState):
        if newState in LiDARManager.STATES:
            self.state = newState
        return self.state
            
    def getState(self)->int:
        return self.state