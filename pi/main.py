# -*- coding: utf-8 -*-
"""
Created on Thu Sep 23 18:58:26 2021

@author: tngus
"""

from lidarManager import LiDARManager 
from multiprocessing.pool import ThreadPool
import matplotlib.pyplot as plt
import numpy as np

def plotter(plot_pts = 100):
    plt.style.use('ggplot') # plot formatting
    fig,axs = plt.subplots(1,1,figsize=(12,8)) # create figure
    fig.canvas.set_window_title('TF-Luna Real-Time Ranging')
    fig.subplots_adjust(wspace=0.05)
    # ranging axis formatting
    axs.set_xlabel('Sample',fontsize=16)
    axs.set_ylabel('Amplitude',fontsize=16) # amplitude label
    axs.set_xlim([0.0,plot_pts])
    axs.set_ylim([0.0,8.0]) # set ranging limits
    # draw and background specification
    fig.canvas.draw() # draw initial plot
    ax_bgnd = fig.canvas.copy_from_bbox(axs[0].bbox) # get background
    line1, = axs[0].plot(np.zeros((plot_pts,)),linewidth=3.0,
                color=plt.cm.Set1(1)) # dummy initial ranging data (zeros)
    line2, = axs[0].plot(np.zeros((plot_pts,)),linewidth=3.0,
                color=plt.cm.Set1(0)) 
    fig.show() # show plot
    return fig,axs,ax_bgnd,line1,line2

def plot_updater(fig, axs, ax_bgnd, line1, line2, dist_array):
    ##########################################
    # ---- time series 
    fig.canvas.restore_region(ax_bgnd) # restore background 1 (for speed)
    line1.set_ydata(dist_array[0])
    line2.set_ydata(dist_array[1])
    axs[0].draw_artist(line1) # draw line
    axs[0].draw_artist(line2)
    fig.canvas.blit(axs[0].bbox) # blitting (for speed)
    fig.canvas.flush_events() # required for blitting
    return line1, line2

class Main:

    def getCommand():
        pass

    def postCommand():
        pass
    
    def getRPM():
        return 30
    
    
    def __init__(self):
        self.lm = LiDARManager(Main.getRPM(), 100, -50, 50)
        
    def run(self):

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
        fig,axs,ax_bgnd,line1, line2 = plotter(100)         
        distArray = [[],[]]
        print('Starting Ranging...')
        while True:
            distances = self.lm.getRaws(0) # read values
            distArray[0].append(distances[0][0]) # append to array
            distArray[1].append(distances[0][0]) # append to array
            if len(distArray[0])>100:
                distArray = distArray[:][1:] # drop first point (maintain array size)
                line1,line2 = plot_updater(fig,axs,ax_bgnd,line1, line2, distArray) # update plot
        
        
main = Main()

main.run()