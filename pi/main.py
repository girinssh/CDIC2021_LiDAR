# -*- coding: utf-8 -*-
"""
Created on Thu Sep 23 18:58:26 2021

@author: tngus
"""

from lidarManager import LiDARManager 
import threading
import matplotlib.plot as plt
import numpy as np

class Main:

    def getCommand():
        pass

    def postCommand():
        pass
    
    def getRPM():
        return 120
    
    
    def __init__(self):
        self.lm = LiDARManager(Main.getRPM(), 100, -50, 50)
        
    def run(self):
        rawsAndAngles = 0
        t = threading.Thread(rawsAndAngles = self.lm.getRaws, args=(0))
        t.start()
        
        t.join()
        
        rawList = rawsAndAngles[0]
        angleList = rawsAndAngles[1]
        
        plt.style.use('ggplot') # figure formatting
        fig,ax = plt.subplots(figsize=(12,9)) # figure and axis
        ax.plot(angleList ,rawList,linewidth=3.5) # plot ranging data
        ax.set_ylabel('Distance [m]',fontsize=16) 
        ax.set_xlabel('Angle [DEG]',fontsize=16)
        ax.set_title('TF-Luna Ranging Test',fontsize=18)
        plt.show() # show figure
        
        
main = Main()

main.run()