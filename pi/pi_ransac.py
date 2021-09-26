# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 17:41:41 2021
@author: tngus
"""

import numpy as np
import math

class dangerDetection:
    MIN_ANGLE = 2*math.pi/9
    MAX_ANGLE = 7*math.pi/9

    # y expression
    def getBase(radius:float, velo:float, sec:float, goLeft:bool):
        return radius, (1 if goLeft else -1) * 9*velo*sec/(5*math.pi), (-7 if goLeft else 2)*velo*sec/5

    def RANSAC(pList): #pList [x1, y1], [x2, y2] ... #pList = [angle(radian), distance]
        maxInliers = []
        finOutliers = [] # final outliers list
        
        # algo rotation num is already set: 14
        for i in range(0, 14):
            i1, i2 = np.random.randint(0, pList[:,0].size, size=2)
            p1 = np.array([pList[i1, 0], pList[i1, 1]])
            p2 = np.array([pList[i2, 0], pList[i2, 1]])

            p1x=p1[1]/math.tan(p1[0]) # x (rcos(angle)) value of p1
            a = p1x/math.cos(p1[0])
            as1 = a * math.sin(p1[0])
            as2 = a * math.sin(p2[0])
    
            b = (p2[1] - p1[1] - as2 + as1) / (p1[0] - p2[0])
            c = p1[1] - as1 + b * p1[0]
    
            inliers = []
            outliers = []
    
            for p in pList:
                x = p[0] # angle of p
                y = p[1] # distance of p

                # 임계값 넘어가면 outlier 
                # 임계값 내에 있으면 inlier

                y_th = 0.5 # threshold value [m]

                py = a * math.sin(x) - b * x + c # p1, p2로 만든 식에 만족하는 y 값

                if abs(y - py) > y_th:
                    outliers.append([x,y])
                else:
                    inliers.append([x,y])

            if len(inliers) > len(maxInliers):
                maxInliers = inliers
                finOutliers = outliers
                param = np.array([a, b, c])
    
        return np.array(maxInliers), np.array(finOutliers)
