
#horizontal distance from car to obstacles by angle

def raw2horiDist(distanceList, rawDistList, srvo_ang, angleList):
	for i in range (0, len(rawDistList)):
		distanceList[i] = rawDistList[i]*math.cos(math.radians(srvo_ang))*math.cos(abs(math.radians(angleList[i])-(math.pi/2)))
    return distanceList

#height of obstacles by angle

def raw2height(heightList, rawDistList, srvo_ang, LiDAR_height):
	for i in range (0, len(rawDistList)):
		heightList[i] = LiDAR_height - rawDistList[i]*math.sin(math.radians(srvo_ang))
    return heightList
