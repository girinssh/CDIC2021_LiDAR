# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 17:41:41 2021
@author: tngus
"""

import numpy as np
import main

class dangerDetection:
    MIN_ANGLE = 2*np.pi/9
    MAX_ANGLE = 7*np.pi/9

    # y expression
    def getBase(radius:float):
        Main = main.Main.getInstance()
        return radius, (1 if Main.goLeft else -1) * 9*Main.velocity*Main.onewayTime/(5*np.pi), (-7 if Main.goLeft else 2)*Main.velocity*Main.onewayTime/5

    def RANSAC(cls, pList): #pList [x1, y1], [x2, y2] ... #pList = [angle(radian), distance]
        print(type(pList))    
        print(pList.shape)
        maxInliers = []
        finOutliers = [] # final outliers list
        
        # algo rotation num is already set: 14
        for i in range(0, 14):
            i1, i2 = np.random.randint(0, pList[:,0].size, size=2)
            
            while i1 == i2:
                i2 = np.random.randint(0, pList[:,0].size, size=1)
            p1 = np.array([pList[i1, 1], pList[i1, 0]])
            p2 = np.array([pList[i2, 1], pList[i2, 0]])

            p1x=p1[1]/np.tan(p1[0]) # x (rcos(angle)) value of p1
            a = p1x/np.cos(p1[0])
            as1 = a * np.sin(p1[0])
            as2 = a * np.sin(p2[0])
    
            b = (p2[1] - p1[1] - as2 + as1) / (p1[0] - p2[0])
            c = p1[1] - as1 + b * p1[0]
    
            inliers = []
            outliers = []
    
            for p in pList[:-1]:
                # print(p)
                x = p[1] # angle of p
                y = p[0] # distance of p

                # 임계값 넘어가면 outlier 
                # 임계값 내에 있으면 inlier

                y_th = 0.5 # threshold value [m]

                py = a * np.sin(x) - b * x + c # p1, p2로 만든 식에 만족하는 y 값

                if abs(y - py) > y_th:
                    outliers.append([x,y])
                else:
                    inliers.append([x,y])

            if len(inliers) > len(maxInliers):
                maxInliers = inliers.copy()
                finOutliers = outliers.copy()
                param = np.array([a, b, c])
    
        return np.array(maxInliers), np.array(finOutliers), param
