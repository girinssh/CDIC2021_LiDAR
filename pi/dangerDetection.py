import numpy as np
import IMU
import threading

LEFT = 0
RIGHT = 1
BACK = 2
LR = 3
UD = 4
DOBS = 5
UOBS = 6

class dangerDetection:
    state = [0]*7
    
    def RANSAC(XPOS, YPOS, H): #XH 평면을 바라보고
        #XPOS : 라이다에서 측정 포인트까지의 x축 방향 distance
        #YPOS :
        #H = heightList : 지면에서 측정 포인트까지의 높이 #1차원 리스트
        
        maxInliers = []
        finOutliers = [] # final outliers list #[i1, i2, …, in] 인덱스 번호
        retParam = []
        
        l = len(XPOS)
        
        # algo rotation num is already set: 14
        for i in range(10):
            i1 = np.random.randint(0, l/3)
            i2 = np.random.randint(l/3, l*2/3)
            i3 = np.random.randint(l*2//3, l)
                
            p = np.array([[XPOS[i1], YPOS[i1], H[i1]],
                          [XPOS[i2], YPOS[i2], H[i2]],
                          [XPOS[i3], YPOS[i3], H[i3]]])
                    

            param = np.array([sum([p[j][k] * (p[j-2][k+1] - p[j-1][k+1]) for j in range(3)]) for k in range(-2, 1, 1)])
            
            param = np.append(param, -sum([p[j][0] * (p[j-2][1]*p[j-1][2] - p[j-2][2]*p[j-1][1]) for j in range(3)]))
            
            #print("param: ", param)

            inliers = []
            outliers = []
    
            for j in range(l) :
                if j == i1 or j == i2 or j == i3:
                    continue

                pt = np.array([XPOS[j], YPOS[j], H[j]])
    
                w = pt - p[0]
                # 임계값 넘어가면 outlier 
                # 임계값 내에 있으면 inlier

                z_th = 0.05 # threshold value [m]

                d = np.abs(np.dot(param[:-1],w))/np.linalg.norm(param[:-1])

                #pz = a*x+b # p1, p2로 만든 식에 만족하는 z값

                if d > z_th:
                    outliers.append([i])
                else:
                    inliers.append([i])

            if len(inliers) > len(maxInliers):
                maxInliers = inliers
                finOutliers = outliers
                retParam = param

        return maxInliers, finOutliers, retParam
    
    # Least Square Method 
    # inliers들로 구성된 기준식 하나 구하기 (=a, b 구하기)
    # inliersList는 RANSAC이 return한 maxInliers = [i]
    def LSM( maxInliers, XPOS, YPOS, H):
        A=np.empty((0,3), dtype=np.float32) # A = [x, y, 1] (mx2)
        B=np.empty((0,1), dtype=np.float32) # B = [z] (mx1)

        # A, B 행렬 만들기
        for i in maxInliers:
            tmpx=XPOS[i]
            tmpy=YPOS[i]
            tmph=H[i]
            A = np.append(A, np.array([[tmpx, tmpy, 1]], dtype=np.float32), axis=0)
            B = np.append(B, np.array([[tmph]], dtype=np.float32))

        X=np.linalg.inv(A.T@A)@A.T@B # X 업데이트

        return X # np.array X = [a, b, c]를 return

    # 후면 라이다일 때 좌우 상하 판단 다시
    # 좌우 경사 판단 Method # roll 각도 구하기 # [x, z] # 전면 라이다에서만 진행됨
    def lrSlope(plane): # inliers = inliers에 해당하는 인덱스 리스트

        # p1=[XPOS[inliers[0]], H[inliers[0]]] # 첫번째 inlier의 [x,z] 값 
        # p2=[XPOS[inliers[-1]], H[inliers[-1]]] # 마지막 inlier의 [x,z] 값 
        # rol_ang = np.arctan((p2[1]-p1[1])/(p2[0]-p1[0])) # [rad] # 항상 p2[0] != p1[0] 
        return np.arctan(-plane[0]/plane[2])
    
    # 상하 경사 판단 Method # pitch 각도 구하기  # [y, z] 
    def udSlope(plane):

        # p1=[YPOS[inliers[0]], H[inliers[0]]]
        # p2=[YPOS[inliers[-1]], H[inliers[-1]]]

        # pit_ang = np.arctan((p2[1]-p1[1])/(p2[0]-p1[0]))
        return np.arctan(-plane[1]/plane[2])
    
    # 예상되는 roll, pitch를 계산해서 상하, 좌우 picto 번호와 led 번호를 반환
    def estiSlope(POS, pit_ang, rol_ang, carRol, carPit):
        # car roll, pitch 받아오기
        
        if pit_ang*carPit > 0:
            estPit=abs(pit_ang-carPit) # 차의 현재 각도와 라이다의 예상 각도의 부호가 같을 때 (내리막 > 내리막, 오르막 > 오르막)
        else: estPit=abs(pit_ang+carPit) # 각도가 0이거나 두 각도의 부호가 다를 때 (내리막 > 오르막, 오르막 > 내리막)

        if rol_ang*carRol > 0:
            estRol=abs(rol_ang-carRol) 
        else: estRol=abs(rol_ang+carRol)

        pitTh = 2*np.pi/9 # pitch 위험 기준 각도 40[deg] = 2pi/9[rad]
        rolTh = np.pi/6 # roll 위험 기준 각도 30[deg] = pi/6[rad]

        
        if estPit > pitTh:
            dangerDetection.state[UD] = 1
            if POS == 2: dangerDetection.state[BACK] = 1
            else: dangerDetection.state[LEFT] = dangerDetection.state[RIGHT] = 1

        if estRol > rolTh:
            dangerDetection.state[LR] = 1
            if POS==2: dangerDetection.state[BACK] = 1
            if rol_ang < 0: dangerDetection.state[LEFT] = 1
            elif rol_ang > 0: dangerDetection.state[RIGHT] = 1
            else: 
                if carRol < 0: dangerDetection.state[RIGHT] = 1
                elif carRol > 0: dangerDetection.state[LEFT] = 1

    def Obstacle(POS, finOutliers, XPOS, H):
        
        if len(finOutliers) < 2:
            return 
        
        minpwid = 2 # outliers 인덱스가 최소 몇개 이상 연속돼야하는지 기준값
        zth = 2 # 장애물끼리의 높이 차 허용 기준값

        # minpwid개 이상 연속으로 모인 점들을 리스트에 저장
        packet = []
        tmp = []

        v = finOutliers.pop(0)[0]
        tmp.append(v)
        
        print("TYPE: ", v)

        while len(finOutliers) > 0:
            vv = finOutliers.pop(0)[0]
            if v+1 == vv:
                tmp.append(vv)
                v = vv
            else:
                if len(tmp) > minpwid:
                    packet.append(tmp)
                tmp = []
                tmp.append(vv)
                v = vv
        
        if len(tmp) > minpwid:
            packet.append(tmp)
            
        finobs=[]
        ledpos=[]
        pictopos=[]

        # 1개의 장애물을 구성하는 인덱스들끼리 z값 비교하여 큰 차이 없으면 취함
        for i in range(len(packet)):
            if sum(dangerDetection.state) == 7:
                break
            tmpack = np.array(packet[i])
            tmph=[]
            tmpx=[]
            for j in tmpack:
                tmph.append(H[j])
            if all((np.array(tmph)-tmph[0])<zth): 
                finobs.append(packet[i])

                # 오목인지 볼록인지 판단
                if all(np.array(tmph)>0): dangerDetection.state[UOBS] = 1
                elif all(np.array(tmph)<0): dangerDetection.state[DOBS] = 1
                else: continue

                # 장애물 좌/우/전방 위치 판단
                if POS == 2:
                    dangerDetection.state[BACK] = 1
                else:
                    if sum(dangerDetection.state[LEFT:RIGHT+1]) == 2:
                        continue
                    for k in tmpack:
                        tmpx.append(XPOS[k])
                    if all(np.array(tmpx)>0): dangerDetection.state[RIGHT] = 1
                    elif all(np.array(tmpx)<0): dangerDetection.state[LEFT] = 1
                    else: dangerDetection.state[RIGHT] = dangerDetection.state[LEFT] = 1
        return

#     #roll, pitch, obstacle 각각의 picto, led 결합하여 아두이노로 넘겨줄 최종 picto, led 구하기
#     def finalPictoLed(pictoPit:str, pictoRol:str, obspicto:list, ledPit:str, ledRol:str, obsled:list):
#         finpicto=[0,0,0,0]
#         finled=[0,0,0]
#         repicto="" #아두이노로 return할 picto num ex. "0001"
#         reled="" #아두이노로 return할 led num ex. "100"

#         #print(type(pictoPit), type(pictoRol), type(obspicto), type(ledPit),type(ledRol), type(obsled))

#         for i in range(4):
#             finpicto[i] = int(pictoPit[i])+int(pictoRol[i])+obspicto[i]
#             if finpicto[i]!=0: finpicto[i]=1
#             repicto+=str(finpicto[i])
# 	    #print(finpicto)
# 	    #print(repicto)

#         for i in range(3):
#             finled[i] = int(ledPit[i])+int(ledRol[i])+obsled[i]
#             if finled[i]!=0: finled[i]=1
#             reled+=str(finled[i])
# 	    #print(finled)
# 	    #print(reled)
#         return repicto, reled
        
    def estimate(POS, XPOS, YPOS, H, carRol, carPit):
        inlier, outlier, param = dangerDetection.RANSAC(XPOS, YPOS, H)
        #param = dangerDetection.LSM(inlier, XPOS, YPOS, H)
        t = threading.Thread(target=dangerDetection.Obstacle, args=(POS, outlier, XPOS, H))
        t.start()
        ud = dangerDetection.udSlope(param)
        lr = dangerDetection.lrSlope(param)
        dangerDetection.estiSlope(POS, ud , lr, carRol, carPit)
        t.join()
        return
    
    def getState():
        return dangerDetection.state
    
    def resetState():
        dangerDetection.state = [0]*7
        