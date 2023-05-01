#Simulate G code: https://nraynaud.github.io/webgcode/
import sys

# adding folder to the system path
sys.path.insert(0, '../')
from pydexarm import Dexarm
import undistort
import cv2
import numpy as np
import contour 
from scipy.optimize import fsolve
import math

DIM=(1920,1080)



K=np.array([[1082.575588874099, 0.0, 972.4972458089494], 
            [0.0, 1080.778686260306, 548.7794822734731], 
            [0.0, 0.0, 1.0]])
D=np.array([[-0.09591921573503272], [-0.03262541200866185], [0.03432325058813786], [-0.015350145846566209]])

k1 = D[0][0];
k2 = D[1][0];
k3 = D[2][0];
k4 = D[3][0];
fx = K[0][0]
fy = K[1][1]
cx = K[0][2]
cy = K[1][2]


z_c0 = 78;
z_object = 30;


def funcRealWorld(x):
     global u_adjusted, v_adjusted,k1,k2,k3,k4
     return [x[0] -np.arctan(x[2]),
             x[1]-x[0]*(1+k1*x[0]**2+k2*x[0]**4+k3*x[0]**6+k4*x[0]**8),
             x[2]**2-x[3]**2-x[4]**2,
             u_adjusted-x[1]*x[3]/x[2],
             v_adjusted-x[1]*x[4]/x[2]]



def getRealLocation(imageBGR,robotPosition):
    #Inputs:image in BGR format, robot position of arm: [x,y,z]

    global u_adjusted, v_adjusted,k1,k2,k3,k4
    centerX, centerY = contour.getObjectLocation(imageBGR)
    print(centerX,centerY)
    u_adjusted = (centerX[0]*1.0-cx)/fx
    v_adjusted = (centerY[0]*1.0-cy)/fy
    sol = fsolve(funcRealWorld, [1, 1,1,1,1])
    print(funcRealWorld(sol))
    print(np.isclose(funcRealWorld(sol), [0.0, 0.0,0.0,0.0,0.0]))

    z_c = z_c0-z_object+robotPosition[2]#z Distance from object to camera
    x_c = sol[3]*z_c;
    y_c = sol[4]*z_c;

    x_e = x_c*1.0;
    y_e = -y_c*1.0-61.0;#y axis is flipped and translated upwards 
    z_e = 0.0;#dummy z

    P_e = np.array([[x_e],[y_e], [z_e], [1]])
    theta = np.arcsin(robotPosition[0]/math.sqrt(robotPosition[0]**2+robotPosition[1]**2))        
    T_r_e=np.array([[np.cos(theta), np.sin(theta), 0.0,robotPosition[0]*1.0], 
        [-np.sin(theta), np.cos(theta), 0.0,robotPosition[1]*1.0], 
        [0.0, 0.0, 1.0, robotPosition[2]*1.0],
        [0.0, 0.0, 0.0, 1.0]])
    
    #print(T_r_e)
    #print(P_e)
    P_r = np.matmul(T_r_e,P_e);#Multiply homogeneous transform by position in end-effector frame to get position in robot/global frame
    print(P_r[0],P_r[1])
    #print("="*80)
    return P_r[0][0],P_r[1][0]



cam = cv2.VideoCapture(0)#Change
cam.set(cv2.CAP_PROP_FRAME_WIDTH, DIM[0])
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, DIM[1])




pickUpDexarm = Dexarm(port="COM6")#Open communication with dexarm
pickUpDexarm.go_home()#Initializes Robot and goes home position



cameraRedRobot = (150,300,120)
cameraGreenRobot = (-100,360,100)


pickUpDexarm.move_to(*cameraGreenRobot,feedrate=16000)
ret, imageGreen = cam.read()
imageGreen =undistort.undistort(imageGreen,True)
xGreen, yGreen =getRealLocation(imageGreen,cameraGreenRobot)
pickUpDexarm.move_to(xGreen,yGreen,-37)
pickUpDexarm.air_picker_pick();


pickUpDexarm.move_to(*cameraRedRobot,feedrate=16000)#Camera Location to find Red Block;
ret, imageRed = cam.read()
imageRed =undistort.undistort(imageRed,False)
xRed, yRed =getRealLocation(imageRed,cameraRedRobot)
pickUpDexarm.move_to(xRed,yRed,-7)



pickUpDexarm.air_picker_place()
pickUpDexarm.move_to(None, None, 20)
pickUpDexarm.air_picker_stop()