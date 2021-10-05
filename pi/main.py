# -*- coding: utf-8 -*-
"""
Created on Thu Sep 23 18:58:26 2021

@author: tngus
"""

from lidarManager import LiDARManager 
import pi_method
from dangerDetection import dangerDetection
from IMU import IMUController

from concurrent.futures import ThreadPoolExecutor as tpe

import threading

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
        self.rpm = 120
        self.samp_rate = 100
        self.min_angle = 2*np.pi / 9
        self.max_angle = 7*np.pi / 9
        self.lm = LiDARManager(self.rpm, self.samp_rate, self.min_angle, self.max_angle)
        self.onewayTime = 60 / (self.rpm * 2) # sec
        
        self.width = 2.0 # m
        self.height = 1.0 # m
        self.velocity = 5.0 # m/s
        self.new_velo = -1
        
        self.velo_range = [0.0, 2.4, 4.0, 5.56]     
        
        self.srvo_ang = np.arctan2(self.height, np.array([3, 5, 7]))
        self.srvo_level = 0
        self.danger_states = [0]*7


        self.velo_trigger = True
        self.danger_trigger = False
        self.post_trigger = True

        self.imu = IMUController()
        self.imu.sensor_calibration()
    

        self.serArdu = serial.Serial('/dev/ttyACM0', 9600, timeout=1.0)
        
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
        
        self.serArdu.flush()
        
        ang = np.rad2deg(self.srvo_ang)
        srvo_ang_str = '{:.2f}, {:.2f}, {:.2f}\n'.format(ang[0], ang[1], ang[2])
        #print(srvo_ang_str)
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
        while self.serArdu.is_open:
            if self.serArdu.inWaiting() > 0:
                com = self.serArdu.readline().decode('utf-8').rstrip()
                if "velocity" in com:
                    self.new_velo = float(com.split(':')[1])
                    print('get: ', self.new_velo)
            time.sleep(0.1)

    def postCommand(self):
        while self.serArdu.is_open:
            if self.post_trigger:       
                ts = ''
                for i in self.danger_states[0:3]:
                    ts += str(i)
                ts += str(self.srvo_level)
                for i in self.danger_states[3:]:
                    ts += str(i)
                ts += '\n'
                if self.velo_trigger:
                    self.velo_trigger = False

                if self.danger_trigger:
                    self.danger_trigger = False

                print('post: ', ts)
                threading.Thread(target=self.serArdu.write, args=(ts.encode('utf-8'),)).start()
                self.post_trigger = False
            time.sleep(0.01)
    
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
        
        interval_max = 0
        interval_min = 2
        # inlier, outlier, param = [], [], []
        total_time = 0
        
        # plt.style.use('ggplot') # figure formatting
        # figure and axis
        # fig = plt.figure()
        # ax = fig.add_subplot(projection='3d')
        # colorList = [['#ff0000', '#00ff00', '#0000ff'],['#dd1111', '#11dd11', '#1111dd']]
        cycle = 9
        
        X = np.arange(-2.0, 2.0, 0.1)
        Y = np.arange(-1.0, 5.0, 0.1)
        X, Y = np.meshgrid(X, Y)
        
        threading.Thread(target=self.getCommand).start()
        threading.Thread(target=self.postCommand).start()
        
        self.lidarCnt = 2
        
        i = 0
        while self.serArdu.is_open:
            try:
                start_time = time.time()
                dangerDetection.resetState()
                rawDistAngleTime = {i[0] : i[1] for i in tpe().map(self.lm.getRaws, (start_time,)*self.lidarCnt, (i for i in range(self.lidarCnt)), (1 - 2 * (i%2),)*self.lidarCnt)}
                # 여기서 raw, angle array를 thread로 distx, disty, height로 변환한다. 
                # { 라이다 번호 : 데이터 } // 0 - left / 1 - right / 2 - backward
                rp = tpe().submit(self.imu.getRollPitch)
                heightList = tpe().submit(self.convertRaw2Height, rawDistAngleTime)
                xposList = tpe().submit(self.convertRaw2XPOS, rawDistAngleTime)
                yposList = tpe().submit(self.convertRaw2YPOS, rawDistAngleTime)
                
                heightList = heightList.result()
                xposList = xposList.result()
                yposList = yposList.result()
                
                frontXList, frontYList, frontHList = self.changeDataAxis(xposList, yposList, heightList)
                #print(frontXList)
                # inlier, outlier, paramR = dangerDetection.RANSAC(frontXList, frontYList, frontHList)
                # paramLSM = dangerDetection.LSM(inlier, frontXList, frontYList, frontHList)
                
                roll, pitch = rp.result()
                
                if self.lidarCnt == 3:
                    backXList = xposList[2]
                    backYList = yposList[2]
                    backHList = heightList[2]
                    tpe.map(dangerDetection.estimate, (0, 2), (frontXList, backXList), (frontYList, backYList), (frontHList, backHList), (roll,)*2, (pitch,)*2)
                else :
                    dangerDetection.estimate(0, frontXList, frontYList, frontHList, roll, pitch)
                    
                new_danger_states = dangerDetection.getState()
                # print("LED: ", self.danger_states)
                
                if sum([ 1 if new_danger_states[i] != self.danger_states[i] else 0 for i in range(7)]) > 0:
                    self.danger_states = new_danger_states
                    self.danger_trigger = True
                
                if self.new_velo != -1:
                    self.velocity = self.new_velo
                    self.new_velo = -1
                    for i in range(3):
                        if self.velo_range[i] < self.velocity < self.velo_range[i+1]:
                            step = i
                            break
                    if step != self.srvo_level:
                        self.srvo_level = step
                        self.velo_trigger = True
                    
                self.post_trigger = self.velo_trigger or self.danger_trigger
                
                end_time = time.time()
                interval = end_time - start_time
                interval_max = interval if interval > interval_max else interval_max
                interval_min = interval if interval < interval_min else interval_min
                total_time += interval
                print(i, interval, yposList.keys())
            except Exception as e:  
                print(e)
                self.serArdu.close()  
            finally:               
                i+=1
            # ax.scatter(frontXList, frontYList, frontHList, color=colorList[(i%2)][i%3])
            
            # ZR = (paramR[0] * X + paramR[1] * Y + paramR[3])/-paramR[2]
            # ax.plot_surface(X, Y, ZR, rstride=4, cstride=4, alpha=0.2)

            # ZLSM = paramLSM[0] * X + paramLSM[1] * Y + paramLSM[2]
            # ax.plot_surface(X, Y, ZLSM, rstride=4, cstride=4, alpha=0.4)
            # for j in range(self.lidarCnt):
            #     ax.scatter(xposList[j], yposList[j], heightList[j], color=colorList[j][i%2])
            
        
        interval_avg = total_time / (i+1)
        if self.serArdu.is_open:
            self.serArdu.close()  
        print("Total Time: ", total_time)
        print("Interval MAX: ", interval_max)
        print("Interval MIN: ", interval_min)
        print("Interval AVG: ", interval_avg)
        #ax.set_xlim([-2.0,2.0])
        # ax.set_zlim([-1.0,1.0]) 
        # ax.set_zlabel('Z Height [m]',fontsize=16) 
        # ax.set_ylabel('Y Distance [m]',fontsize=16) 
        # ax.set_xlabel('X Distance [m]',fontsize=16)
        # ax.set_title('TF-Luna Ranging Test',fontsize=18)
        # plt.show()
    
        
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
