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


    
    def getBase(radius:float, velo:float, sec:float, goLeft:bool):
        return radius, (1 if goLeft else -1) * 9*velo*sec/(5*math.pi), (-7 if goLeft else 2)*velo*sec/5
    
    def RANSAC(pList, angleList): #pList [x1, y1], [x2, y2] ... 
        maxInliers = []
        outliers = []
        
        for i in range(0, 14):
            i1, i2 = np.random.randint(0, pList[:,0].size, size=2)
            p1 = np.array([pList[i1, 0], pList[i1, 1]])
            p2 = np.array([pList[i2, 0], pList[i2, 1]])
    
            a = p1[0]/math.cos(angleList[i1])
            as1 = a * math.sin(angleList[i1])
            as2 = a * math.sin(angleList[i2])
    
            b = (p2[1] - p1[1] - as2 + as1) / (angleList[i1] - angleList[i2])
            c = p1[1] - as1 + b * angleList[i1]
    
            inliers = []
    
            for p in pList:
                x = p[0]
                y = p[1]
                
                d = 0
                # 여기서 베이스와 Y축 값 비교 하면서 
                # 임계값 넘어가면 outlier 
                # 임계값 내에 있으면 inlier
    
            if len(inliers) > len(maxInliers):
                maxInliers = inliers
                param = np.array([a, b, c])
    
        return maxInliers, outliers