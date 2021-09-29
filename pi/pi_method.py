
#horizontal distance from car to obstacles by angle

import numpy as np

def raw2YPOS(pos:int, rawDistList, srvo_ang:float, angleList, velocity: float):
    
 	# for i in range (len(rawDistList)): 
  #        distanceList[i] = rawDistList[i]*math.cos(math.radians(srvo_ang))*math.cos(abs(math.radians(angleList[i])-(math.pi/2)))
    return pos, rawDistList*np.cos(srvo_ang)*np.sin(abs(angleList-(np.pi/2)))
    # yList = rawDistList*np.cos(srvo_ang)*np.sin(angleList)
    # return pos, yList


def raw2XPOS(pos:int, rawDistList, srvo_ang:float, angleList):
    return pos, rawDistList*np.cos(srvo_ang)*np.cos(angleList)

#height of obstacles by angle
def raw2height(pos: int, rawDistList, srvo_ang:float, LiDAR_height:float):
# 	for i in range (0, len(rawDistList)):
# 		heightList[i] = LiDAR_height - rawDistList*np.sin(np.deg2rad(srvo_ang)) 
    return pos, LiDAR_height - rawDistList*np.sin(srvo_ang)