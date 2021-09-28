
#horizontal distance from car to obstacles by angle

import numpy as np

def raw2horiDist(pos:int, rawDistList, srvo_ang:float, angleList):
# 	for i in range (0, len(rawDistList)): 
# 		distanceList[i] = rawDistList[i]*math.cos(math.radians(srvo_ang))*math.cos(abs(math.radians(angleList[i])-(math.pi/2)))
    # return distanceList
    return pos, rawDistList*np.cos(np.deg2rad(srvo_ang))*np.cos(np.abs(np.deg2rad(angleList)-np.pi/2))

#height of obstacles by angle

def raw2height(pos: int, rawDistList, srvo_ang:float, LiDAR_height:float):
# 	for i in range (0, len(rawDistList)):
# 		heightList[i] = LiDAR_height - rawDistList*np.sin(np.deg2rad(srvo_ang)) 
    return pos, LiDAR_height - rawDistList*np.sin(np.deg2rad(srvo_ang))