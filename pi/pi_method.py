
#horizontal distance from car to obstacles by angle

import numpy as np

def raw2YPOS(pos:int, rawDistList, srvo_ang:float, angleList, timeList, velocity: float):
    yList = rawDistList*np.cos(srvo_ang)*np.sin(angleList)
    yList -= (timeList[-1] - timeList)*velocity
    return pos, yList


def raw2XPOS(pos:int, rawDistList, srvo_ang:float, angleList):
    return pos, rawDistList*np.cos(srvo_ang)*np.cos(angleList)

#height of obstacles by angle
def raw2height(pos: int, rawDistList, srvo_ang:float, LiDAR_height:float):
# 	for i in range (0, len(rawDistList)):
# 		heightList[i] = LiDAR_height - rawDistList*np.sin(np.deg2rad(srvo_ang)) 
    return pos, LiDAR_height - rawDistList*np.sin(srvo_ang)