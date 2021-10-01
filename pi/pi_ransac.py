import numpy as np

class dangerDetection:
    #~…
    
    def RANSAC(XPOS, H): #XH 평면을 바라보고
        #XPOS : 라이다에서 측정 포인트까지의 x축 방향 distance
        #YPOS :
        #H = heightList : 지면에서 측정 포인트까지의 높이 #1차원 리스트
        
        maxInliers = []
        finOutliers = [] # final outliers list #[i1, i2, …, in] 인덱스 번호
        
        # algo rotation num is already set: 14
        for i in range(0, 14):
            while True: 
                i1, i2 = np.random.randint(0, len(XPOS), size=2)
                if (i1 != i2):
                    p1 = np.array([XPOS[i1], H[i1]])
                    p2 = np.array([XPOS[i2], H[i2]])
                    break
                # a 계산 시 분모가 0이 되는 걸 방지

            #두 점을 지나는 직선 (z=)f(x)=ax+b 구하기 
            a = (p2[1]-p1[1])/(p2[0]-p1[0])
            b = p1[1]-a*p1[0]

            inliers = []
            outliers = []
    
            for i in range(len(XPOS)) :
                x = XPOS[i] # x value of ith point
                z = H[i] # height of ith point

                # 임계값 넘어가면 outlier 
                # 임계값 내에 있으면 inlier

                z_th = 0.3 # threshold value [m]

                pz = a*x+b # p1, p2로 만든 식에 만족하는 z값

                if abs(z - pz) > z_th:
                    outliers.append([i])
                else:
                    inliers.append([i])

            if len(inliers) > len(maxInliers):
                maxInliers = inliers
                finOutliers = outliers
                param = [a, b]

    return maxInliers, finOutliers, param

