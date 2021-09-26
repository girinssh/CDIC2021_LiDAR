# -*- coding: utf-8 -*-
"""
Created on Thu Sep 23 18:58:26 2021

@author: tngus
"""

from lidarManager import LiDARManager 
from pi_ransac import dangerDetection

import concurrent.futures
from concurrent.futures import ThreadPoolExecutor as tpe

import serial,time
import matplotlib.pyplot as plt
import numpy as np

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
        self.lm = LiDARManager(Main.getRPM(), 100, -50, 50)
        self.onewayTime = 60 / (Main.getRPM() * 2)
        self.height = 0.3
                              
    # only develop at raspberry pi
    def getCommand(self):
        while True:
            pass
        pass

    def postCommand(self):
        pass
    
    def getRPM():
        return 120
    
    # need to be executed every oneway time.
    def lidarThreadRun(self):
        self.lm.getRaws(0)
        pass
                          
    
    def run(self):
        print(self.onewayTime)
        
        totalStart = time.time()
        
        inlier, outlier = [], []
        for i in range(1):
            start_time = time.time()
            
            rawDistAngle = np.array(list(tpe().map(self.lm.getRaws, (0, ), (1, ), timeout=self.onewayTime))[0])
            
            print(rawDistAngle)
            
            inlier, outlier = dangerDetection().RANSAC(rawDistAngle)

            end_time = time.time()
            print(i, end_time - start_time)
        
        plt.style.use('ggplot') # figure formatting
        fig,ax = plt.subplots(figsize=(12,9)) # figure and axis
        if inlier.size() > 0 :    
            ax.scatter(inlier[:][1],inlier[:][0]) # plot ranging data
        if outlier.size() > 0 :    
            ax.scatter(outlier[:][1],outlier[:][0]) # plot ranging data
        ax.set_ylabel('Distance [m]',fontsize=16) 
        ax.set_xlabel('Angle [DEG]',fontsize=16)
        ax.set_title('TF-Luna Ranging Test',fontsize=18)
        totalEnd = time.time()
        
        print("Total Time: ", totalEnd - totalStart)
        
        
        
        
        
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
