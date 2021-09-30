# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 17:41:41 2021
@author: tngus
"""

import numpy as np
# import main

class dangerDetection:
    MIN_ANGLE = 2*np.pi/9
    MAX_ANGLE = 7*np.pi/9

    # y expression
    # def getBase(radius:float):
    #     Main = main.Main.getInstance()
    #     return radius, (1 if Main.goLeft else -1) * 9*Main.velocity*Main.onewayTime/(5*np.pi), (-7 if Main.goLeft else 2)*Main.velocity*Main.onewayTime/5

    def getNumberOfCycle(m: int, alpha=0.8, p=0.01)-> int:
        return int(np.log10(p)/np.log10(1-alpha ** m))
    
    # def RANSAC(cls, pos:int, pList): #pList [x1, y1], [x2, y2] ... #pList = [angle(radian), distance]
    #     maxInliers = []
    #     finOutliers = [] # final outliers list
        
    #     print(pList.shape)
        
    #     a = np.sqrt(pList[-1][0] ** 2 + pList[-1][1] ** 2)
        
    #     y_th = 0.5 # threshold value [m]

    #     # algo rotation num is already set: 14
    #     for i in range(cls.getNumberOfCycle(pList.shape[0])):
    #         i1, i2 = np.random.randint(0, pList[:,0].size, size=2)
            
    #         while i1 == i2:
    #             i2 = np.random.randint(0, pList[:,0].size, size=1)
    #         p1 = pList[i1]
    #         p2 = pList[i2]

    #         t1pt2d2 = np.arctan2(p2[0]-p1[0], p1[1]-p2[1])
            

    #         inliers = []
    #         outliers = []
    
    #         for p in pList:
    #             # print(p)
    #             x = p[0] 
    #             y = p[1] 

    #             # 임계값 넘어가면 outlier 
    #             # 임계값 내에 있으면 inlier

    #             t = np.arccos(x/a)
    #             py = a * np.sin(t) - b * t + c # p1, p2로 만든 식에 만족하는 y 값

    #             if abs(y - py) > y_th:
    #                 outliers.append([x,y])
    #             else:
    #                 inliers.append([x,y])

    #         if len(inliers) > len(maxInliers):
    #             maxInliers = inliers.copy()
    #             finOutliers = outliers.copy()
    #             param = np.array([a, b, c], dtype=float)
    
    #     return np.array(maxInliers), np.array(finOutliers), param
