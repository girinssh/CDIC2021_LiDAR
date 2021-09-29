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

import serial,time
import matplotlib.pyplot as plt
import numpy as np

from IMU import *

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
        
        self.height = 0.3 # m
        self.velocity = 5.0 # m/s
        
        
        self.srvo_ang = np.arctan2(np.array([3, 5, 7]), self.height)
        self.dangerLevel = 0
        self.srvo_level = 0

        self.imu = IMUController()

        Main.goLeft = False
        Main.main = self
                              
    def getInstance():
        return Main.main
    
    # only develop at raspberry pi
    def getCommand(self):
        while True:
            pass
        pass

    def postCommand(self):
        pass
    
    # need to be executed every oneway time.
    def lidarThreadRun(self):
        self.lm.getRaws(0)
        pass
    
    def convertRaw2Height(self, raw:dict)->dict:
        return {i[0]: i[1] for i in tpe().map(pi_method.raw2height, raw.keys(), [raw[i][0] for i in raw.keys()], (self.srvo_ang[self.srvo_level],)*3, (self.height,)*3)}
    def convertRaw2YPOS(self, raw:dict)->dict:
        return {i[0]: i[1] for i in tpe().map(pi_method.raw2YPOS, raw.keys(), [raw[i][0] for i in raw.keys()], (self.srvo_ang[self.srvo_level],)*3, (self.velocity,)*3, [raw[i][1] for i in raw.keys()])}
    def convertRaw2XPOS(self, raw:dict)->dict:
        return {i[0]: i[1] for i in tpe().map(pi_method.raw2XPOS, raw.keys(), [raw[i][0] for i in raw.keys()], (self.srvo_ang[self.srvo_level],)*3, [raw[i][1] for i in raw.keys()])}
    
    
    def run(self):
        print(self.onewayTime)
        
        interval_max = 0
        interval_min = 2
        inlier, outlier, param = [], [], []
        total_time = 0
        
        plt.style.use('ggplot') # figure formatting
        fig,ax = plt.subplots(figsize=(12,9)) # figure and axis
        
        cycle = 3
        
        for i in range(cycle):
            start_time = time.time()
            
            rawDistAngle = {}
            
            try:
                rawDistAngle = {i[0] : i[1] for i in tpe().map(self.lm.getRaws, (start_time,)*3, (0, 1, 2), (1 - 2 * (i%2),)*3, timeout=0.25)}
            except:
                print("EXCEPTION")
                continue    

            # 여기서 raw, angle array를 thread로 distx, disty, height로 변환한다. 
            
            heightList = tpe().submit(self.convertRaw2Height, rawDistAngle)
            xposList = tpe().submit(self.convertRaw2XPOS, rawDistAngle)
            yposList = tpe().submit(self.convertRaw2YPOS, rawDistAngle)
            
            heightList = heightList.result()
            xposList = xposList.result()
            yposList = yposList.result()
            
            print("Roll = {}, Pitch = {}".format(self.imu.calc_angle()))
            
            #inlier, outlier, param = dangerDetection().RANSAC(np.vstack((xposList[0], yposList[0])))

            end_time = time.time()
            interval = end_time - start_time
            interval_max = interval if interval > interval_max else interval_max
            interval_min = interval if interval < interval_min else interval_min
            print(i, interval, yposList[0].shape)
            
            for i in range(3):
                ax.scatter(xposList[i], yposList[i])
            
            total_time += interval
        
        interval_avg = total_time / cycle
           
        print("Total Time: ", total_time)
        print("Interval MAX: ", interval_max)
        print("Interval MIN: ", interval_min)
        print("Interval AVG: ", interval_avg)
        ax.set_xlim([-2.0,2.0])
        ax.set_ylim([-2.0,8.0]) 
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
        # #x = param[0] * np.cos(t)
        # y = param[0]* np.sin(t) + param[1] * t + param[2]
        # ax.scatter(np.rad2deg(t) - 90, y, color='g')
        # ax.set_ylabel('Distance [m]',fontsize=16) 
        # ax.set_xlabel('Angle [DEG]',fontsize=16)
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
