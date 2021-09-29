# -*- coding: utf-8 -*-
"""
Created on Wed Sep 29 14:16:19 2021

@author: tngus
"""

import smbus,time
import numpy as np

# MPU6050 Registers
MPU6050_ADDR = 0x68
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
ACCEL_CONFIG = 0x1C
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
TEMP_OUT_H   = 0x41
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47

# Low pass Filter
DLPF_BW_256 = 0x00      # Acc: BW-260Hz, Delay-0ms, Gyro: BW-256Hz, Delay-0.98ms
DLPF_BW_188 = 0x01
DLPF_BW_98  = 0x02
DLPF_BW_42  = 0x03
DLPF_BW_20  = 0x04
DLPF_BW_10  = 0x05
DLPF_BW_5   = 0x06

# GYRO_CONFIG: Gyro의 Full Scale 설정(bit 4:3)
GYRO_FS_250  = 0x00 << 3    # 250 deg/sec
GYRO_FS_500  = 0x01 << 3
GYRO_FS_1000 = 0x02 << 3
GYRO_FS_2000 = 0x03 << 3    # 2000 deg/sec

mappingRange = 2**15

DEG_PER_SEC = 32767 / 500
ALPHA = 1 / (1 + 0.05)

class IMUController:
    def __init__(self):
        self.bus = smbus.SMBus(1)
        
        # alter sample rate (stability)
        samp_rate_div = 0 # sample rate = 8 kHz/(1+samp_rate_div)
        self.bus.write_byte_data(MPU6050_ADDR, SMPLRT_DIV, samp_rate_div)
        time.sleep(0.1)
        # reset all sensors
        self.bus.write_byte_data(MPU6050_ADDR,PWR_MGMT_1,0x00)
        time.sleep(0.1)
        # power management and crystal settings
        self.bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0x01)
        time.sleep(0.1)
        #Write to Configuration register
        self.bus.write_byte_data(MPU6050_ADDR, CONFIG, 0)
        time.sleep(0.1)
        #Write to Gyro configuration register
        gyro_config_sel = [0b00000,0b010000,0b10000,0b11000] # byte registers
        gyro_config_vals = [250.0,500.0,1000.0,2000.0] # degrees/sec
        gyro_indx = 0
        self.bus.write_byte_data(MPU6050_ADDR, GYRO_CONFIG, int(gyro_config_sel[gyro_indx]))
        time.sleep(0.1)
        #Write to Accel configuration register
        accel_config_sel = [0b00000,0b01000,0b10000,0b11000] # byte registers
        accel_config_vals = [2.0,4.0,8.0,16.0] # g (g = 9.81 m/s^2)
        accel_indx = 0                            
        self.bus.write_byte_data(MPU6050_ADDR, ACCEL_CONFIG, int(accel_config_sel[accel_indx]))
        time.sleep(0.1)
        # interrupt register (related to overflow of data [FIFO])
        self.bus.write_byte_data(MPU6050_ADDR, INT_ENABLE, 1)
        time.sleep(0.1)
        self.gyrosense = gyro_config_vals[gyro_indx]
        self.accelsense = accel_config_vals[accel_indx]
    
        self.acc = np.array([0] * 3, dtype=float)
        self.gyro = np.array([0] * 3, dtype=float)
        
        self.now = 0
        self.past = 0
        self.during = 0
        
        self.roll = 0.0
        self.pitch = 0.0
        
        self.angleGyro = np.array([0]*3, dtype=float)
        self.angleFi = np.array([0]*3, dtype=float)
        
        self.caliSensor()
        
    def getRoll(self):
        return self.roll
    
    def getPitch(self):
        return self.pitch
    
    def run(self):
        self.caliSensor()
    
    def reset(self):
        self.caliSensor()
        
    
    def calc_angle(self):
        self.getData()
        self.getDT()
        
        angleAcX = np.arctan2(self.acc[1], np.sqrt(self.acc[0]**2 + self.acc[2]**2)) * 180 / np.pi
        angleAcY = np.arctan2(-self.acc[0], np.sqrt(self.acc[1]**2 + self.acc[2]**2)) * 180 / np.pi
        
        self.angleGyro += ((self.gyro - self.avggyro)*DEG_PER_SEC) * self.during
        
        angleTmp = self.angleFi + self.angleGyro * self.during
        
        self.angleFi = ALPHA * angleTmp + (1.0 - ALPHA) * np.array([angleAcX, angleAcY, 1.0])
        
        temp = np.rad2deg(self.angleFi)
        self.roll = temp[0]
        self.pitch = temp[1]
        
        return self.roll, self.pitch
        
    def caliSensor(self):
        sumacc = np.array([0]*3, dtype=float)
        sumgyro = np.array([0]*3, dtype=float)
        
        self.getData()
        for i in range(10):
            sumacc += self.acc
            sumgyro += self.gyro
        self.avgacc = sumacc/10
        self.avggyro = sumgyro/10
        
    def getData(self):
        self.acc[0] = (self.read_raw_bits(ACCEL_XOUT_H)/mappingRange)*self.accelsense
        self.acc[1] = (self.read_raw_bits(ACCEL_YOUT_H)/mappingRange)*self.accelsense
        self.acc[2] = (self.read_raw_bits(ACCEL_ZOUT_H)/mappingRange)*self.accelsense
        
        self.gyro[0] = (self.read_raw_bits(GYRO_XOUT_H)/mappingRange)*self.gyrosense
        self.gyro[1] = (self.read_raw_bits(GYRO_YOUT_H)/mappingRange)*self.gyrosense
        self.gyro[2] = (self.read_raw_bits(GYRO_ZOUT_H)/mappingRange)*self.gyrosense
        return

    def getDT(self):
        self.now = time.time()
        self.during =( self.now - self.past) if self.past != 0 else 0
        self.past = self.now
        return
    
    def read_raw_bits(self, register):
    # read accel and gyro values
        high = self.bus.read_byte_data(MPU6050_ADDR, register)
        low = self.bus.read_byte_data(MPU6050_ADDR, register+1)
    
        # combine higha and low for unsigned bit value
        value = ((high << 8) | low)
        
        # convert to +- value
        if(value > 32768):
            value -= 65536
        return value