# -*- coding: utf-8 -*-
"""
Created on Thu Sep 23 18:58:26 2021

@author: tngus
"""

from lidarManager import LiDARManager 
from pi_ransac import dangerDetection
import pi_method

import concurrent.futures
from concurrent.futures import ThreadPoolExecutor as tpe

import threading

import serial,time
import matplotlib.pyplot as plt
import numpy as np

# import IMU

# def plotter(plot_pts = 100):
#     plt.style.use('ggplot') # plot formatting
#     fig,axs = plt.subplots(1,1,figsize=(12,8)) # create figure
#     fig.canvas.set_window_title('TF-Luna Real-Time Ranging')
#     fig.subplots_adjust(wspace=0.05)
#     # ranging axis formatting
#     axs.set_xlabel('Sample',fontsize=16)
#     axs.set_ylabel('Amplitude',fontsize=16) # amplitude label
#     axs.set_xlim([0.0,plot_pts])
#     axs.set_ylim([0.0,8.0]) # set ranging limits
#     # draw and background specification
#     fig.canvas.draw() # draw initial plot
#     ax_bgnd = fig.canvas.copy_from_bbox(axs.bbox) # get background
#     line1, = axs.plot(np.zeros((plot_pts,)),linewidth=3.0,
#                 color=plt.cm.Set1(1)) # dummy initial ranging data (zeros)
#     line2, = axs.plot(np.zeros((plot_pts,)),linewidth=3.0,
#                 color=plt.cm.Set1(0)) 
#     fig.show() # show plot
#     return fig,axs,ax_bgnd,line1,line2
# def plot_updater(fig, axs, ax_bgnd, line1, line2, dist_array):
#     ##########################################
#     # ---- time series 
#     fig.canvas.restore_region(ax_bgnd) # restore background 1 (for speed)
#     line1.set_ydata(dist_array[0])
#     line2.set_ydata(dist_array[1])
#     axs.draw_artist(line1) # draw line
#     axs.draw_artist(line2)
#     fig.canvas.blit(axs.bbox) # blitting (for speed)
#     fig.canvas.flush_events() # required for blitting
#     return line1, line2

class Main:
    def __init__(self):
        self.rpm = 120
        self.samp_rate = 100
        self.min_angle = 2*np.pi / 9
        self.max_angle = 7*np.pi / 9
        self.lm = LiDARManager(self.rpm, self.samp_rate, self.min_angle, self.max_angle)
        self.onewayTime = 60 / (self.rpm * 2) # sec
        
        self.width = 0.3 # m
        self.height = 0.3 # m
        self.velocity = 5.0 # m/s
        
        self.srvo_ang = np.arctan2(self.height, np.array([3, 5, 7]))
        self.dangerLevel = 0
        self.srvo_level = 0

        # self.imu = IMU.IMUController()
        # print(self.imu.set_MPU6050_init(dlpf_bw=IMU.DLPF_BW_98))
        # self.imu.sensor_calibration()

        # self.serArdu = serial.Serial('/dev/ttyAMA0', 9600)

        Main.goLeft = False
        Main.main = self
                              
    def getInstance():
        return Main.main
    
    # only develop at raspberry pi
    def getCommand(self):
        command = []
        # while self.serArdu.is_open:
        #     if self.serArdu.inWaiting() > 0:
        #         com = self.serArdu.readUntil().decode('utf-8').rstrip()
                
        #     pass
        pass

    def postCommand(self):
        
        pass
    
    def getVelocity(self):
        pass
    
    def convertRaw2Height(self, raw:dict)->dict:
        return {i[0]: i[1] for i in tpe().map(pi_method.raw2height, raw.keys(), [raw[i][0] for i in raw.keys()], (self.srvo_ang[self.srvo_level],)*self.lidarCnt, (self.height,)*3)}
    def convertRaw2YPOS(self, raw:dict)->dict:
        return {i[0]: i[1] for i in tpe().map(pi_method.raw2YPOS, raw.keys(), [raw[i][0] for i in raw.keys()], (self.srvo_ang[self.srvo_level],)*self.lidarCnt, [raw[i][1] for i in raw.keys()], [raw[i][2] for i in raw.keys()], (self.velocity,)*self.lidarCnt)}
    def convertRaw2XPOS(self, raw:dict)->dict:
        return {i[0]: i[1] for i in tpe().map(pi_method.raw2XPOS, raw.keys(), [raw[i][0] for i in raw.keys()], (self.srvo_ang[self.srvo_level],)*self.lidarCnt, [raw[i][1] for i in raw.keys()])}
    
    def changeDataAxis(self, xposList, yposList, heightList):
        #dtype = [('x', np.float32), ('y', np.float32), ('z', np.float32)]
        print(xposList[0].shape, xposList[1].shape)
        print(yposList[0].shape, yposList[1].shape)
        print(heightList[0].shape, heightList[1].shape)
        
        xposList[0] = xposList[0] - self.width/2
        xposList[1] = xposList[1] + self.width/2
        
        #xlist = np.hstack((xposList[0] - self.width/2, xposList[1]+ self.width/2))
        xlist = np.hstack((xposList[0], xposList[1]))
        ylist = np.hstack((yposList[0], yposList[1]))
        hlist = np.hstack((heightList[0], heightList[1]))
        
        posList = np.vstack((xlist, ylist, hlist))
        #pos3dList.astype(dtype)
        pos3dList = np.sort(posList.T, order=['f0'], axis=0)        
        print(pos3dList)
        
        return pos3dList
    
    def run(self):
        print(self.onewayTime)
        
        interval_max = 0
        interval_min = 2
        # inlier, outlier, param = [], [], []
        total_time = 0
        
        plt.style.use('ggplot') # figure formatting
        # figure and axis
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        colorList = [['#ff0000', '#00ff00', '#0000ff'],['#dd1111', '#11dd11', '#1111dd']]
        cycle = 1
        
        # threading.Thread(target=self.getCommand).start()
        
        self.lidarCnt = 2
        
        for i in range(cycle):
            start_time = time.time()

            
            rawDistAngleTime = {i[0] : i[1] for i in tpe().map(self.lm.getRaws, (start_time,)*self.lidarCnt, (i for i in range(self.lidarCnt)), (1 - 2 * (i%2),)*self.lidarCnt)}

            print(type(rawDistAngleTime))
            # 여기서 raw, angle array를 thread로 distx, disty, height로 변환한다. 
            # { 라이다 번호 : 데이터 } // 0 - left / 1 - right / 2 - backward
            heightList = tpe().submit(self.convertRaw2Height, rawDistAngleTime)
            xposList = tpe().submit(self.convertRaw2XPOS, rawDistAngleTime)
            yposList = tpe().submit(self.convertRaw2YPOS, rawDistAngleTime)
            
            heightList = heightList.result()
            xposList = xposList.result()
            yposList = yposList.result()
            
            frontXList, frontYList, frontHList = self.changeDataAxis(xposList, yposList, heightList)
            print(frontXList)
            
            if self.lidarCnt == 3:
                backXList = xposList[2]
                backYList = yposList[2]
                backHList = heightList[2]
            
            #print(yposList[0])
            
            #print("(Roll, Pitch) = {}".format(self.imu.getRollPitch()))
            
            # inlier, outlier, param = dangerDetection().RANSAC(np.vstack((xposList[0], yposList[0])))

            end_time = time.time()
            interval = end_time - start_time
            interval_max = interval if interval > interval_max else interval_max
            interval_min = interval if interval < interval_min else interval_min
            print(i, interval, yposList.keys())
            
            ax.scatter(frontXList, frontYList, frontHList, color=colorList[i//2][i%2])
            # for j in range(self.lidarCnt):
            #     ax.scatter(xposList[j], yposList[j], heightList[j], color=colorList[j][i%2])
            
            total_time += interval
        
        interval_avg = total_time / cycle
           
        print("Total Time: ", total_time)
        print("Interval MAX: ", interval_max)
        print("Interval MIN: ", interval_min)
        print("Interval AVG: ", interval_avg)
        #ax.set_xlim([-2.0,2.0])
        #ax.set_ylim([0.0,8.0]) 
        ax.set_zlabel('Z Height [m]',fontsize=16) 
        ax.set_ylabel('Y Distance [m]',fontsize=16) 
        ax.set_xlabel('X Distance [m]',fontsize=16)
        ax.set_title('TF-Luna Ranging Test',fontsize=18)
        plt.show()
        
        # # print(inlier, outlier)

        # print("Inlier Count: ", inlier.shape)
        # if inlier.size > 0 :    
        #     ax.scatter(inlier[:,0],inlier[:,1], color='b') # plot ranging data
        # print("Outlier Count: ", outlier.shape)
        # if outlier.size > 0 :    
        #     ax.scatter(outlier[:,0],outlier[:,1], color='r') # plot ranging data
        
        # print(param)
        
        # t = np.linspace(2*np.pi/9, 7*np.pi/9, 50)
        # x = param[0] * np.cos(t)
        # y = param[0] * np.sin(t) + param[1] * t + param[2]
        # ax.scatter(np.rad2deg(t) - 90, y, color='g')
        # ax.set_ylabel('Distance [m]',fontsize=16)       
        # ax.set_xlabel('Distance [m]',fontsize=16)
        # ax.set_title('TF-Luna Ranging Test',fontsize=18)
        # plt.show()
        
        #######################################
        # ------ Print First 50 points ------ #
        #######################################
        # pool = ThreadPool(processes = 2)        
        # result = pool.map(self.lm.getRaws, (0,1))
        # print(result, sep="\n")
        # plt.style.use('ggplot') # figure formatting
        # fig,ax = plt.subplots(figsize=(12,9)) # figure and axis
        # for raa in result:
        #     rawList = raa[0]
        #     angleList = raa[1]
        #     ax.scatter(angleList ,rawList) # plot ranging data
        # ax.set_ylabel('Distance [m]',fontsize=16) 
        # ax.set_xlabel('Angle [DEG]',fontsize=16)
        # ax.set_title('TF-Luna Ranging Test',fontsize=18)
        # plt.show() # show figure
        
        
        #######################################
        # ------ Real Time Visualizing ------ #
        #######################################
        # fig,axs,ax_bgnd,line1, line2 = plotter(100)         
        # distArray = [[],[]]
        # print('Starting Ranging...')
        # while True:
        #     distance1 = self.lm.getRaws(0) # read values
        #     distance2 = self.lm.getRaws(1)
        #     distArray[0].append(distance1[0][0]) # append to array
        #     distArray[1].append(distance2[0][0]) # append to array
        #     if len(distArray[0])>100:
        #         distArray[0] = distArray[0][1:] # drop first point (maintain array size)
        #         distArray[1] = distArray[1][1:] # drop first point (maintain array size)
        #         line1,line2 = plot_updater(fig,axs,ax_bgnd,line1, line2, distArray) # update plot
        

if __name__ == '__main__':
    main = Main()
    main.run()
