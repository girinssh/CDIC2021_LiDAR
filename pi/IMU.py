# -*- coding: utf-8 -*-

# GPIO 라이브러리
import smbus    # 많이 찾아봤는데... Python에서는 I2C 보다는 smbus를 I2C로 사용하더라
                # 없다면, sudo apt-get install python-smbus로 설치
import math
import time

'''
기본코드 참조: http://practical.kr/?p=76   # 단, ACCEL을 이용한 각도계산만 수록됨
이론설명 참조: https://blog.naver.com/codingbird/221766900497
'''
################################
# MPU 레지스터 번호(필요한것만...)
################################
# MPU-6050 Register
CONFIG       = 0x1A     # LowPassFilter bit 2:0
GYRO_CONFIG  = 0x1B     # FS_SEL bit 4:3
ACCEL_CONFIG = 0x1C     # FS_SEL bit 4:3
PWR_MGMT_1   = 0x6B     # sleep bit 6, clk_select bit 2:0

# CONFIG: Low Pass Filter 설정(bit 2:0)
DLPF_BW_256 = 0x00      # Acc: BW-260Hz, Delay-0ms, Gyro: BW-256Hz, Delay-0.98ms
DLPF_BW_188 = 0x01
DLPF_BW_98  = 0x02
DLPF_BW_42  = 0x03
DLPF_BW_20  = 0x04
DLPF_BW_10  = 0x05
DLPF_BW_5   = 0x06      # Acc: BW-5Hz, Delay-19ms, Gyro: BW-5Hz, Delay-18.6ms

# GYRO_CONFIG: Gyro의 Full Scale 설정(bit 4:3)
GYRO_FS_250  = 0x00 << 3    # 250 deg/sec
GYRO_FS_500  = 0x01 << 3
GYRO_FS_1000 = 0x02 << 3
GYRO_FS_2000 = 0x03 << 3    # 2000 deg/sec

# ACCEL_CONFIG: 가속도센서의 Full Scale 설정(bit 4:3)
ACCEL_FS_2  = 0x00 << 3     # 2g
ACCEL_FS_4  = 0x01 << 3
ACCEL_FS_8  = 0x02 << 3
ACCEL_FS_16 = 0x03 << 3     # 16g

# PWR_MGMT_1: sleep(bit 6)
SLEEP_EN        = 0x01 << 6
SLEEP_DIS       = 0x00 << 6
# PWR_MGMT_1: clock(bit 2:0)
CLOCK_INTERNAL  = 0x00  # internal clk(8KHz) 이용 (Not! Recommended)
CLOCK_PLL_XGYRO = 0x01  # XGyro와 동기
CLOCK_PLL_YGYRO = 0x02  # YGyro와 동기
CLOCK_PLL_ZGYRO = 0x03  # ZGyro와 동기

# Data 읽기
ACCEL_XOUT_H = 0x3B     # Low는 0x3C
ACCEL_YOUT_H = 0x3D     # Low는 0x3E
ACCEL_ZOUT_H = 0x3F     # Low는 0x40
GYRO_XOUT_H  = 0x43     # Low는 0x44
GYRO_YOUT_H  = 0x45     # Low는 0x46
GYRO_ZOUT_H  = 0x47     # Low는 0x48

################################
# I2C 읽고 쓰기
################################
# I2C Bus 초기화
class IMUController:
    def __init__(self):
        self.I2C_bus = smbus.SMBus(1)
        self.MPU6050_addr = 0x68
        
            
        # 각도(deg) = Gyro값(step) / DEGREE_PER_SECOND(step*sec/deg) * dt(sec) 의 누적...
        self.DEGREE_PER_SECOND = 32767 / 250  # Gyro의 Full Scale이 250인 경우
                                         # Full Scale이 1000인 경우 32767/1000
        self.past = 0      # 현재 시간(sec)
        self.baseAcX = 0   # 기준점(가만히 있어도 회전이 있나???)
        self.baseAcY = 0
        self.baseAcZ = 0
        self.baseGyX = 0
        self.baseGyY = 0
        self.baseGyZ = 0
        
        self.GyX_deg = 0   # 측정 각도
        self.GyY_deg = 0
        self.GyZ_deg = 0
        
        self.alpha = 1 / (1 + 0.05)
    
    # 한바이트 쓰기
    def write_byte(self, adr, data):
        self.I2C_bus.write_byte_data(self.MPU6050_addr, adr, data)
    
    # 한바이트 읽기
    def read_byte(self, adr):
        return self.I2C_bus.read_byte_data(self.MPU6050_addr, adr)
    
    # 두바이트 읽기
    def read_word(self, adr):
        high = self.I2C_bus.read_byte_data(self.MPU6050_addr, adr)
        low = self.I2C_bus.read_byte_data(self.MPU6050_addr, adr+1)
        val = (high << 8) + low
        return val
    
    # 두바이트를 2's complement로 읽기(-32768~32767)
    # 아두이노는 변수를 signed 16bit로 선언해서 처리하지만
    # 라즈베리파이는 이렇게 변환해 줘야 한다. 
    def read_word_2c(self, adr):
        val = self.read_word(adr)
        if (val >= 0x8000):
            return -((65535 - val) + 1)
        else:
            return val             
    
    # 레지스터에서 raw data를 읽기
    def get_raw_data(self):
        """
        가속도(accel)와 각속도(gyro)의 현재 값 읽기
        :return: accel x/y/z, gyro x/y/z
        """
        gyro_xout = self.read_word_2c(GYRO_XOUT_H)
        gyro_yout = self.read_word_2c(GYRO_YOUT_H)
        gyro_zout = self.read_word_2c(GYRO_ZOUT_H)
        accel_xout = self.read_word_2c(ACCEL_XOUT_H)
        accel_yout = self.read_word_2c(ACCEL_YOUT_H)
        accel_zout = self.read_word_2c(ACCEL_ZOUT_H)
        return accel_xout, accel_yout, accel_zout,\
               gyro_xout, gyro_yout, gyro_zout
    
    
    """ 
    Accel값(가속도)만 이용해서 Y축과 X축 방향의 기울어진 각도 측정
    중력가속도를 기준으로 기울여졌을때의 각 방향의 크기를 이용(삼각함수)
    진동에 취약
    """
    def cal_angle_acc(self, AcX, AcY, AcZ):
        """
        Accel값만 이용해서 X, Y의 각도 측정
        (고정 좌표 기준?)
        그런데... 각도가 0 -> 90 -> 0 -> -90 -> 0으로 바뀐다. 왜?
        0도 -> 90도 -> 180도 -> 270도 -> 360도
        즉, 30도와 120도가 모두 30도로 표시된다. 왜?
        :param AcX: Accel X
        :param AcY: Accel Y
        :param AcZ: Accel Z
        :return: X, Y angle in degree
        """
        y_radians = math.atan2(AcX, math.sqrt((AcY*AcY) + (AcZ*AcZ)))
        x_radians = math.atan2(AcY, math.sqrt((AcX*AcX) + (AcZ*AcZ)))
        return math.degrees(x_radians), -math.degrees(y_radians)

    
    def cal_angle_gyro(self, GyX, GyY, GyZ):
        """
        Gyro를 이용한 현재 각도 계산
        누적 방식이라... 회전하는 방향에 따라 양수/음수가 정해진다.
        :param y: 현재 Gyro 출력
        :return: 현재 각도, 기준 시간 -> past
        """
    
        now = time.time()
        dt = now - self.past     # 초단위
    
        self.GyX_deg += ((GyX - self.baseGyX) / self.DEGREE_PER_SECOND) * dt
        self.GyY_deg += ((GyY - self.baseGyY) / self.DEGREE_PER_SECOND) * dt
        self.GyZ_deg += ((GyZ - self.baseGyZ) / self.DEGREE_PER_SECOND) * dt
    
        return now      # 다음 계산을 위해 past로 저장되어야 한다.
    
    def sensor_calibration(self):
        """
        1초동안의 평균을 이용하여 기준점 계산
        :return: Accel과 Gyro의 기준점 -> baseAcX ~ basGyZ
        """
        SumAcX = 0
        SumAcY = 0
        SumAcZ = 0
        SumGyX = 0
        SumGyY = 0
        SumGyZ = 0
    
        for i in range(10):
            AcX, AcY, AcZ, GyX, GyY, GyZ = self.get_raw_data()
            SumAcX += AcX
            SumAcY += AcY
            SumAcZ += AcZ
            SumGyX += GyX
            SumGyY += GyY
            SumGyZ += GyZ
            time.sleep(0.1)
    
        avgAcX = SumAcX / 10
        avgAcY = SumAcY / 10
        avgAcZ = SumAcZ / 10
        avgGyX = SumGyX / 10
        avgGyY = SumGyY / 10
        avgGyZ = SumGyZ / 10
    
        return avgAcX, avgAcY, avgAcZ, avgGyX, avgGyY, avgGyZ
    
    # Now wake the 6050 up as it starts in sleep mode
    # MPU 6050 초기화
    def set_MPU6050_init(self, dlpf_bw=DLPF_BW_256,
                         gyro_fs=GYRO_FS_250, accel_fs=ACCEL_FS_2,
                         clk_pll=CLOCK_PLL_XGYRO):
    
        # MPU6050 초기값 setting
        self.write_byte(PWR_MGMT_1, SLEEP_EN | clk_pll)      # sleep mode(bit6), clock(bit2:0)은 XGyro 동기
        self.write_byte(CONFIG, dlpf_bw)                     # bit 2:0
        self.write_byte(GYRO_CONFIG, gyro_fs)                # Gyro Full Scale bit 4:3
        self.write_byte(ACCEL_CONFIG, accel_fs)              # Accel Full Scale Bit 4:3
        self.write_byte(PWR_MGMT_1, SLEEP_DIS | clk_pll)     # Start
    
        # sensor 계산 초기화
        baseAcX, baseAcY, baseAcZ, baseGyX, baseGyY, baseGyZ \
            = self.sensor_calibration()
        self.past = time.time()
    
        return self.read_byte(PWR_MGMT_1)    # 정말 시작되었는지 확인
        
    def getRollPitch(self):
        AcX, AcY, AcZ, GyX, GyY, GyZ = self.get_raw_data()
     
        AcX_deg, AcY_deg = self.cal_angle_acc(AcX, AcY, AcZ)

        self.past = self.cal_angle_gyro(GyX, GyY, GyZ)
        return self.alpha * self.GyY_deg + (1 - self.alpha)*AcY_deg, self.alpha * self.GyX_deg + (1 - self.alpha)*AcX_deg
        

########################################
# 테스트 코드
########################################
if __name__ == '__main__':
    ''' -----------------------------------'''
    ''' Gyro 테스트 '''
    ''' -----------------------------------'''
    # 1) MPU 6050 초기화
    test = IMUController()  # BW만 변경, 나머지는 default 이용
    print("Gyro PWR_MGMT_1 Register = ", test.set_MPU6050_init(dlpf_bw=DLPF_BW_98) )

    # 2) Gyro 기준값 계산(Gyro 이용시)
    test.sensor_calibration()    # Gyro의 기준값 계산

    cnt = 0

    while True:
        # 3) accel, gyro의 Raw data 읽기, 
        AcX, AcY, AcZ, GyX, GyY, GyZ = test.get_raw_data()
     
        # 4-1) Accel을 이용한 각도 계산
        AcX_deg, AcY_deg = test.cal_angle_acc(AcX, AcY, AcZ)

        # 4-2) Gyro를 이용한 각도 계산 
        test.past = test.cal_angle_gyro(GyX, GyY, GyZ)

        # 5) 0.01초 간격으로 값 읽기
        time.sleep(0.01)
        cnt += 1

        # 1초에 한번씩 display
        if cnt%100 == 0:
            # print("GyX,Y,Z_deg = ", GyX_deg, ',', GyY_deg, ',', GyZ_deg)
            print("AcX_deg, AcY_deg = ", AcX_deg, ',', AcY_deg)

