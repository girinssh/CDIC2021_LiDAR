# -*- coding: utf-8 -*-
"""
Created on Sat Sep 18 20:24:29 2021

@author: tngus
"""

######################################################
# Copyright (c) 2021 Maker Portal LLC
# Author: Joshua Hrisko
######################################################
#
# TF-Luna Mini LiDAR wired to a Raspberry Pi via UART
# --- test ranging plotter for TF-Luna
#
#
######################################################
#
import serial,time
import numpy as np
import matplotlib.pyplot as plt
#
############################
# Serial Functions
############################
#
 # baud rates

class LiDAR:
    def __init__(self, path, samp_rate=100, baud_indx=4):
        LiDAR.baudrates = [9600,19200,38400,57600,115200,230400,460800,921600]
        
        self.path = path
        self.prev_indx = 4 # previous baud rate index (current TF-Luna baudrate)
        self.prev_ser = serial.Serial(path, LiDAR.baudrates[self.prev_indx],timeout=0) # mini UART serial device
        if self.prev_ser.isOpen() == False:
            self.prev_ser.open()
        
        self.baud_indx = baud_indx
        self.samp_rate = samp_rate
        self.ser = self.set_baudrate()
        
        self.set_samp_rate() # set sample rate 1-250
        self.get_version() # print version info for TF-Luna
        
        self.distanceArray = [-1]*100
        
    def read_data(self):
        while True:
            counter = self.ser.in_waiting # count the number of bytes of the serial port
            bytes_to_read = 9
            if counter > bytes_to_read-1:
                bytes_serial = self.ser.read(bytes_to_read) # read 9 bytes
                self.ser.reset_input_buffer() # reset buffer
    
                if bytes_serial[0] == 0x59 and bytes_serial[1] == 0x59: # check first two bytes
                    distance = bytes_serial[2] + bytes_serial[3]*256 # distance in next two bytes
#                    strength = bytes_serial[4] + bytes_serial[5]*256 # signal strength in next two bytes
#                    temperature = bytes_serial[6] + bytes_serial[7]*256 # temp in next two bytes
#                    temperature = (temperature/8) - 256 # temp scaling and offset
                    return distance/100.0#,strength,temperature
    
    def set_samp_rate(self):
        ##########################
        # change the sample rate
        samp_rate_packet = [0x5a,0x06,0x03,self.samp_rate,00,00] # sample rate byte array
        self.ser.write(samp_rate_packet) # send sample rate instruction
        return
                
    def get_version(self):
        ##########################
        # get version info
        info_packet = [0x5a,0x04,0x14,0x00]
    
        self.ser.write(info_packet)
        time.sleep(0.1)
        bytes_to_read = 30
        t0 = time.time()
        while (time.time()-t0)<5:
            counter = self.ser.in_waiting
            if counter > bytes_to_read:
                bytes_data = self.ser.read(bytes_to_read)
                self.ser.reset_input_buffer()
                if bytes_data[0] == 0x5a:
                    version = bytes_data[3:-1].decode('utf-8')
                    print('Version -'+version)
                    return
                else:
                    self.ser.write(info_packet)
                    time.sleep(0.1)
    
    def get_sample_rate(self):
        return self.samp_rate
    
    def set_baudrate(self):
        ##########################
        # get version info
        baud_hex = [[0x80,0x25,0x00], # 9600
                    [0x00,0x4b,0x00], # 19200
                    [0x00,0x96,0x00], # 38400
                    [0x00,0xe1,0x00], # 57600
                    [0x00,0xc2,0x01], # 115200
                    [0x00,0x84,0x03], # 230400
                    [0x00,0x08,0x07], # 460800
                    [0x00,0x10,0x0e]]  # 921600
        info_packet = [0x5a,0x08,0x06,baud_hex[self.baud_indx][0],baud_hex[self.baud_indx][1],
                       baud_hex[self.baud_indx][2],0x00,0x00] # instruction packet 
    
        self.prev_ser.write(info_packet) # change the baud rate
        time.sleep(0.1) # wait to settle
        self.prev_ser.close() # close old serial port
        time.sleep(0.1) # wait to settle
        ser_new =serial.Serial(self.path, LiDAR.baudrates[self.baud_indx],timeout=0) # new serial device
        if ser_new.isOpen() == False:
            ser_new.open() # open serial port if not open
        bytes_to_read = 8
        t0 = time.time()
        while (time.time()-t0)<5:
            counter = ser_new.in_waiting
            if counter > bytes_to_read:
                bytes_data = ser_new.read(bytes_to_read)
                ser_new.reset_input_buffer()
                if bytes_data[0] == 0x5a:
                    indx = [ii for ii in range(0,len(baud_hex)) if \
                            baud_hex[ii][0]==bytes_data[3] and
                            baud_hex[ii][1]==bytes_data[4] and
                            baud_hex[ii][2]==bytes_data[5]]
                    print('Set Baud Rate = {0:1d}'.format(LiDAR.baudrates[indx[0]]))
                    time.sleep(0.1) 
                    return ser_new
                else:
                    ser_new.write(info_packet) # try again if wrong data received
                    time.sleep(0.1) # wait 100ms
                    continue
                
    def close(self):
        self.ser.close()

#
############################
# Configurations
############################
#

 # open serial port if not open
baud_indx = 4 # baud rate to be changed to (new baudrate for TF-Luna)
 # set baudrate, get new serial at new baudrate


#
############################
# Testing the TF-Luna Output
############################
#
#tot_pts = 100 # points for sample rate test
#time_array,dist_array = [],[[],[]] # for storing values

#lidars = [LiDAR("/dev/serial0"), LiDAR("/dev/ttyAMA1")]

# print('Starting Ranging...')
# while len(dist_array[0])<tot_pts:
#     try:
#         distance,strength,temperature = lidars[0].read_data() # read values
#         distance1,strength1,temperature1 = lidars[0].read_data() # read values
#         dist_array[0].append(distance) # append to array
#         dist_array[1].append(distance1) # append to array
#         time_array.append(time.time())
#     except:
#         continue
# print('Sample Rate: {0:2.0f} Hz'.format(len(dist_array[0])/(time_array[-1]-time_array[0]))) # print sample rate
# lidars[0].close() # close serial port
# lidars[1].close()
#
##############################
# Plotting the TF-Luna Output
##############################
#
# plt.style.use('ggplot') # figure formatting
# fig,ax = plt.subplots(figsize=(12,9)) # figure and axis
# ax.plot(np.subtract(time_array,time_array[0]),dist_array[0],linewidth=3.5) # plot ranging data
# ax.plot(np.subtract(time_array,time_array[0]),dist_array[1],linewidth=3.5) # plot ranging data
# ax.set_ylabel('Distance [m]',fontsize=16) 
# ax.set_xlabel('Time [s]',fontsize=16)
# ax.set_title('TF-Luna Ranging Test',fontsize=18)
# plt.show() # show figure
