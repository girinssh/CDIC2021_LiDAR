# -*- coding: utf-8 -*-
"""
Created on Thu Sep 23 18:58:26 2021

@author: tngus
"""

import pi_method
from dangerDetection import dangerDetection
# from IMU import IMUController
from lidarManager import LiDARManager 
from concurrent.futures import ThreadPoolExecutor as tpe

import threading

# import serial
import time
import matplotlib.pyplot as plt
import numpy as np

#######################################
###             for test            ###
#######################################
'''
for test - True
for real   - False '''
isTest = False

#######################################
###             Activation          ###
#######################################
activateLiDAR = False
activateIMU = False
activateSerial = False

class Main:
    def __init__(self):
        self.rpm = 120
        self.samp_rate = 100
        self.min_angle = 2*np.pi / 9
        self.max_angle = 7*np.pi / 9
        
        self.lm = LiDARManager(self.rpm, self.samp_rate, self.min_angle, self.max_angle, isLiDAROn=(activateLiDAR or not isTest))
        
        self.onewayTime = 60 / (self.rpm * 2) # sec
        
        self.width = 2.0 if isTest else 0.25 # m
        self.height = 1.0 if isTest else 0.19 # m
        self.velocity = 5.0 # m/s
        self.new_velo = -1
        
        self.velo_range = [0.0, 2.4, 4.0, 5.56]     #(unit: meter per sec)
        
        # Need Change!!!!!!!!!!!!!!!!!!!
        self.base_len = np.array([3, 5, 7]) # searching range (unit: meter)
        self.srvo_ang = np.arctan2(self.height, self.base_len) # (unit: radian)
        self.srvo_level = 2

        ang = np.rad2deg(self.srvo_ang)
        srvo_ang_str = '{:.2f}, {:.2f}, {:.2f}\n'.format(ang[0], ang[1], ang[2])
        print(srvo_ang_str)
        
        '''
        [ led_LEFT
         / led_RIGHT
         / led_BACK 
         / type_UpDown 
         / type_LeftRight 
         / type_UpObstacle 
         / type_DownObstacle ]'''
        self.danger_states = [0]*7 
        self.velo_trigger = True
        self.danger_trigger = False
        self.post_trigger = True

        if activateIMU or not isTest:
            from IMU import IMUController
            self.imu = IMUController()
            self.imu.set_MPU6050_init(dlpf_bw=0x02)
            self.imu.sensor_calibration()
    
        self.nowDanger = False
        
        #######################################
        ###             for Real            ###
        #######################################
        if activateSerial or not isTest:            
            import serial
        if not isTest: 
            self.serArdu = serial.Serial('/dev/ttyACM0', 9600, timeout=1.0)
            self.serArdu.close()
            
            while not self.serArdu.is_open:
                print('waiting...')
                self.serArdu.open()
                time.sleep(0.5)
            
            while True:
                s = self.serArdu.readline().decode('utf-8').rstrip()
                print(s)
                if s == "start":
                    self.serArdu.flushInput()
                    break
            
            self.serArdu.flushInput()
        

            self.serArdu.flushOutput()
            self.serArdu.write(srvo_ang_str.encode('utf-8'))
            
            while True:
                if self.serArdu.inWaiting() > 0:
                    s = self.serArdu.readline().decode('utf-8').rstrip()
                    print(s)
                    if s == "success":
                        self.serArdu.flushInput()
                        break

    
    # only develop at raspberry pi
    def getCommand(self):
        self.serArdu.flushInput()
        while self.serArdu.is_open:
            try:
                com = self.serArdu.readline().decode('utf-8').rstrip()
                print(com)
                if "velocity" in com:
                    self.new_velo = float(com.split(':')[1])
                    #print('get: ', self.new_velo)
            except Exception as e:
                print("GET ERROR: " , e)
            time.sleep(0.1)

    def postCommand(self):
        self.serArdu.flushOutput()
        while self.serArdu.is_open:
            
            try:
                if self.post_trigger:       
                    ts = ''
                    for i in self.danger_states[0:3]:
                        ts += str(i)
                    ts += str(self.srvo_level)
                    for i in self.danger_states[3:]:
                        ts += str(i)
                    ts += '\n'
    
                    print('post: ', ts)
                    
                    if self.velo_trigger:
                        self.velo_trigger = False
    
                    if self.danger_trigger:
                        self.danger_trigger = False
    
                    threading.Thread(target=self.serArdu.write, args=(ts.encode('utf-8'),)).start()
                    self.post_trigger = False
            except Exception as e:
                print("POST ERROR: " , e)
            time.sleep(0.1)
    
    def convertRaw2Height(self, raw:dict)->dict:
        return {i[0]: i[1] for i in tpe().map(pi_method.raw2height, raw.keys(), [raw[i][0] for i in raw.keys()], (self.srvo_ang[self.srvo_level],)*self.lidarCnt, (self.height,)*3)}
    def convertRaw2YPOS(self, raw:dict)->dict:
        return {i[0]: i[1] for i in tpe().map(pi_method.raw2YPOS, raw.keys(), [raw[i][0] for i in raw.keys()], (self.srvo_ang[self.srvo_level],)*self.lidarCnt, [raw[i][1] for i in raw.keys()], [raw[i][2] for i in raw.keys()], (self.velocity,)*self.lidarCnt)}
    def convertRaw2XPOS(self, raw:dict)->dict:
        return {i[0]: i[1] for i in tpe().map(pi_method.raw2XPOS, raw.keys(), [raw[i][0] for i in raw.keys()], (self.srvo_ang[self.srvo_level],)*self.lidarCnt, [raw[i][1] for i in raw.keys()])}
    
    def changeDataAxis(self, xposList, yposList, heightList):
        xposList[0] = np.array([x - self.width/2 for x in xposList[0]])
        xposList[1] = np.array([x + self.width/2 for x in xposList[1]])
        
        xlist = np.hstack((xposList[0], xposList[1]))
        ylist = np.hstack((yposList[0], yposList[1]))
        hlist = np.hstack((heightList[0], heightList[1]))
        
        a = xlist.argsort()
        
        return xlist[a], ylist[a], hlist[a]
    
    def run(self):
        print(self.onewayTime)
    
        total_time = 0
        
        self.dangerMaintainTime = 0
        
        self.lidarCnt = 3
        #######################################
        ###             for Test            ###
        #######################################
        if isTest:
            plt.style.use('ggplot') # figure formatting
            # figure and axis
            plt.figure()
            ax = [plt.subplot(261)                      # front XZ
                  , plt.subplot(262)                    # front YZ
                  , plt.subplot(267)                    # back XZ
                  , plt.subplot(268)                    # back YZ
                  , plt.subplot(132, projection='3d')   # RANSAC 3D
                  , plt.subplot(133, projection='3d')]  # LSM 3D
               
            X = np.arange(-2.0, 2.0, 0.1)
            Y = np.arange(-1.0, 5.0, 0.1)
            X, Y = np.meshgrid(X, Y)
            interval_max = 0
            interval_min = 2
            cycle = 3
            
            if activateSerial:
                threading.Thread(target=self.getCommand).start()
                threading.Thread(target=self.postCommand).start()    
            
            for i in range(cycle):
                start_time = time.time()
                rawDistAngleTime = {}
                if activateLiDAR:
                    rawDistAngleTime = {i[0] : i[1] for i in tpe().map(self.lm.getRaws, (start_time,)*self.lidarCnt, (i for i in range(self.lidarCnt)), (1 - 2 * (i%2),)*self.lidarCnt)}
                else:
                    for j in range(self.lidarCnt):
                        rawDistAngleTime[j] = np.array([
                            [self.base_len[self.srvo_level]*np.cos(self.srvo_ang[self.srvo_level]) + np.random.normal()]*self.lm.rawPerOneway, 
                            [((self.lm.angle_min if (i+1)%2 == self.lm.DIR_LEFT2RIGHT else self.lm.angle_max) + ((-1) ** (i%2)) * self.lm.angle_range * np.sin(2*np.pi*t/100)) for t in range(self.lm.rawPerOneway)], 
                            [(t/100) for t in range(self.lm.rawPerOneway)]
                        ], dtype=np.float32)
                # print(self.base_len[self.srvo_level]*np.tan(self.srvo_ang[self.srvo_level]))
                # { key : value } 
                # { 0 - left / 1 - right / 2 - backward : 0 - Raw / 1 - Angle / 2 - Time }
                dangerDetection.resetState()
                
                # is lidar working? / True - YES / False - NO!!!!!!!!!
                if sum([len([rawDistAngleTime[i][2]]) for i in range(self.lidarCnt)]) > 0 :
                    roll, pitch = [0, 0] if not activateIMU else self.imu.getRollPitch()
                    heightList = tpe().submit(self.convertRaw2Height, rawDistAngleTime)
                    xposList = tpe().submit(self.convertRaw2XPOS, rawDistAngleTime)
                    yposList = tpe().submit(self.convertRaw2YPOS, rawDistAngleTime)
                    
                    heightList = heightList.result()
                    xposList = xposList.result()
                    yposList = yposList.result()
                    
                    frontXList, frontYList, frontHList = self.changeDataAxis(xposList, yposList, heightList)
                            
                    np.hstack((frontXList, [0]))
                    np.hstack((frontYList, [0]))
                    np.hstack((frontHList, [0]))
                    
                    inlier, outlier, paramR = dangerDetection.RANSAC(frontXList, frontYList, frontHList)
                    paramLSM = dangerDetection.LSM(inlier, frontXList, frontYList, frontHList)
                    
                    if self.lidarCnt == 3:
                        backXList = xposList[2]
                        backYList = yposList[2]
                        backHList = heightList[2]
                        
                        np.hstack((backXList, [0]))
                        np.hstack((backYList, [0]))
                        np.hstack((backHList, [0]))
                        tpe().map(dangerDetection.estimate, (0, 2), (frontXList, backXList), (frontYList, backYList), (frontHList, backHList), (roll,)*2, (pitch,)*2, timeout=0.02)
                    else :
                        dangerDetection.estimate(0, frontXList, frontYList, frontHList, roll, pitch)
                        
                    new_danger_states = dangerDetection.getState().copy()
                    # print("LED: ", self.danger_states)
                    for j in range(7):
                        if new_danger_states[j] != self.danger_states[j]:
                            #state가 바뀌었는가?
                            if sum(new_danger_states) > 0 or self.dangerMaintainTime <= 0:
                                self.danger_states = new_danger_states
                                self.nowDanger = True
                                self.dangerMaintainTime = 5.0
                            else:
                                self.nowDanger = False
                                
                            self.danger_trigger = True
                            print("DANGER_TRIGGER_ON")
                            break
                    
                    if self.new_velo != -1 and self.new_velo != self.velocity and not self.nowDanger:
                        self.velocity = self.new_velo
                        self.new_velo = -1
                        
                        for j in range(3):
                            if self.velo_range[j] < self.velocity < self.velo_range[j+1]:
                                step = j
                                break
                        if step != self.srvo_level:
                            self.srvo_level = step
                            self.velo_trigger = True
                        print("VELO_TRIGGER_ON")
                    elif self.nowDanger and self.dangerMaintainTime < 5.0/2: # if dangerouse, than activate
                        self.srvo_level = max(self.srvo_level - 1, 0)
                        self.velocity = self.new_velo
                        self.velo_trigger = True
                    else:
                        self.new_velo = -1
                self.post_trigger = self.velo_trigger or self.danger_trigger
                
                end_time = time.time()
                
                interval = end_time - start_time
                
                if self.dangerMaintainTime > 0:                    
                    self.dangerMaintainTime -= interval
                    
                total_time += interval
                ts = ''
                for i in self.danger_states[0:3]:
                    ts += str(i)
                ts += str(self.srvo_level)
                for i in self.danger_states[3:]:
                    ts += str(i)
                print(i, interval, self.danger_states)
                # time.sleep(max(self.onewayTime - interval, 0))
                
                ax[0].scatter(frontXList, frontHList, color=((1.0 * (i+1) /cycle), 0.5, 0.5), s=2)
                ax[1].scatter(frontYList, frontHList, color=((1.0* (i+1) /cycle), 0.5, 0.5), s=2)
                ax[2].scatter(backXList, backHList, color=( 0.5, (1.0* (i+1)/cycle),0.5), s=2)
                ax[3].scatter(backYList, backHList, color=( 0.5, (1.0* (i+1)/cycle), 0.5), s=2)
                
                ZR = (paramR[0] * X + paramR[1] * Y + paramR[3])/-paramR[2]
                ax[4].plot_surface(X, Y, ZR, rstride=5, cstride=5, alpha=0.3)
    
                ZLSM = paramLSM[0] * X + paramLSM[1] * Y + paramLSM[2]
                ax[5].plot_surface(X, Y, ZLSM, rstride=5, cstride=5, alpha=0.3)

                for k in range(2):
                    ax[k+4].scatter(frontXList, frontYList, frontHList, color=( 0.5, 0.5, (1.0* (i+1)/cycle)), s=2)
            
            interval_avg = total_time / (cycle)
            print("Total Time: ", total_time)
            print("Interval MAX: ", interval_max)
            print("Interval MIN: ", interval_min)
            print("Interval AVG: ", interval_avg)
            
            
            for i in range(4):
                ax[i].set_xlim([-3.0,8.0])
                ax[i].set_ylabel('Z Height [m]',fontsize=8) 
                if i % 2 == 0:
                    ax[i].set_xlabel('X Distance [m]',fontsize=8)
                else:
                    ax[i].set_xlabel('Y Distance [m]',fontsize=8)
            # for RANSAC Graph
            ax[4].set_xlim([-5.0,5.0])
            ax[4].set_ylim([-5.0,5.0])
            ax[4].set_zlim([-1.0,self.height * 1.3]) 
            ax[4].set_zlabel('Z Height [m]',fontsize=8) 
            ax[4].set_ylabel('Y Distance [m]',fontsize=8) 
            ax[4].set_xlabel('X Distance [m]',fontsize=8)
            ax[4].set_title('RANSAC',fontsize=8)
            # for LSM Graph
            ax[5].set_xlim([-5.0,5.0])
            ax[5].set_ylim([-5.0,5.0])
            ax[5].set_zlim([-1.0,self.height * 1.3]) 
            ax[5].set_zlabel('Z Height [m]',fontsize=8) 
            ax[5].set_ylabel('Y Distance [m]',fontsize=8) 
            ax[5].set_xlabel('X Distance [m]',fontsize=8)
            ax[5].set_title('LSM',fontsize=8)
            
            plt.show()
        #######################################
        ###             for Real            ###
        #######################################
        else:
            i = 0
            threading.Thread(target=self.getCommand).start()
            threading.Thread(target=self.postCommand).start()            
            while self.serArdu.is_open:
                start_time = time.time()
                rawDistAngleTime = {i[0] : i[1] for i in tpe().map(self.lm.getRaws, (start_time,)*self.lidarCnt, (i for i in range(self.lidarCnt)), (1 - 2 * (i%2),)*self.lidarCnt)}
                dangerDetection.resetState()
                if sum([len([rawDistAngleTime[i][2]]) for i in range(self.lidarCnt)]) > 0 :
                    roll, pitch = self.imu.getRollPitch()
                    heightList = tpe().submit(self.convertRaw2Height, rawDistAngleTime)
                    xposList = tpe().submit(self.convertRaw2XPOS, rawDistAngleTime)
                    yposList = tpe().submit(self.convertRaw2YPOS, rawDistAngleTime)
                    
                    heightList = heightList.result()
                    xposList = xposList.result()
                    yposList = yposList.result()
                    
                    frontXList, frontYList, frontHList = self.changeDataAxis(xposList, yposList, heightList)
                            
                    np.hstack((frontXList, [0]))
                    np.hstack((frontYList, [0]))
                    np.hstack((frontHList, [0]))

                    if self.lidarCnt == 3:
                        backXList = xposList[2]
                        backYList = yposList[2]
                        backHList = heightList[2]
                        
                        np.hstack((backXList, [0]))
                        np.hstack((backYList, [0]))
                        np.hstack((backHList, [0]))
                        tpe().map(dangerDetection.estimate, (0, 2), (frontXList, backXList), (frontYList, backYList), (frontHList, backHList), (roll,)*2, (pitch,)*2, timeout=0.02)
                    else :
                        dangerDetection.estimate(0, frontXList, frontYList, frontHList, roll, pitch)
                        
                    new_danger_states = dangerDetection.getState().copy()
                   
                    
                    for j in range(7):
                        if new_danger_states[j] != self.danger_states[j]:
                            if sum(new_danger_states) > 0 or self.dangerMaintainTime <= 0:
                                self.danger_states = new_danger_states
                                self.nowDanger = True
                                self.dangerMaintainTime = 5.0
                            else:
                                self.nowDanger = False
                                
                            self.danger_trigger = True
                            print("DANGER_TRIGGER_ON")
                            break
                    
                    if self.new_velo != -1 and self.new_velo != self.velocity and not self.nowDanger:
                        self.velocity = self.new_velo
                        self.new_velo = -1
                        
                        for j in range(3):
                            if self.velo_range[j] < self.velocity < self.velo_range[j+1]:
                                step = j
                                break
                        if step != self.srvo_level:
                            self.srvo_level = step
                            self.velo_trigger = True
                        print("VELO_TRIGGER_ON")
                    elif self.nowDanger and self.dangerMaintainTime < 5.0/2: # 위험상황일 때 증가. 
                        self.srvo_level = max(self.srvo_level - 1, 0)
                        self.velocity = self.new_velo
                        self.velo_trigger = True
                    else:
                        self.new_velo = -1
                self.post_trigger = self.velo_trigger or self.danger_trigger
                
                print("DANGER STATE: ", self.danger_states)
                
                end_time = time.time()
                
                interval = end_time - start_time
                
                if self.dangerMaintainTime > 0:                    
                    self.dangerMaintainTime -= interval
                    
                total_time += interval
                time.sleep(self.onewayTime - interval if self.onewayTime > interval else 0)
                i += 1
        
        if activateSerial:
            if self.serArdu.is_open:
                self.serArdu.close()  

if __name__ == '__main__':
    main = Main()
    main.run()
