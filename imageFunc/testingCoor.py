import cv2
import numpy as np
import math
import undistort
from statistics import mean
import contour 
from sympy import symbols, Eq, solve, atan
from scipy.optimize import fsolve
import glob

def func(x):
     global u_adjusted, v_adjusted,k1,k2,k3,k4
     return [x[0] -np.arctan(x[2]),
             x[1]-x[0]*(1+k1*x[0]**2+k2*x[0]**4+k3*x[0]**6+k4*x[0]**8),
             x[2]**2-x[3]**2-x[4]**2,
             u_adjusted-x[1]*x[3]/x[2],
             v_adjusted-x[1]*x[4]/x[2]]


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
def robotImgPosition(rPosition):
    img29Robot = [0,300,167]
    img30Robot = [0,300,150]
    img31Robot = [0,300,100]
    img32Robot = [0,300,167]
    img33Robot = [0,300,150]
    img34Robot = [0,300,100]
    img36Robot = [50,250,150]
    img37Robot = [-50,340,150]
    img38Robot = [70,240,150]
    img39Robot = [0,300,40]
    img40Robot = [50,300,40]
    rPosition.append(img29Robot)
    rPosition.append(img30Robot)
    rPosition.append(img31Robot)
    rPosition.append(img32Robot)
    rPosition.append(img33Robot)
    rPosition.append(img34Robot)
    rPosition.append(img36Robot)
    rPosition.append(img37Robot)
    rPosition.append(img38Robot)
    rPosition.append(img39Robot)
    rPosition.append(img40Robot)







robotPosition = []
robotImgPosition(robotPosition)

imageIndex = 0;
images = glob.glob('testImages/*.jpg');
for fileName in images:#Get image num
    try:#Macbook
        num = int(fileName[fileName.index('/')+1:fileName.index('.')])
    except:
        num = int(fileName[fileName.index("\\")+1:fileName.index('.')])
    if(num>=29 and num<=40 and num != 35):#Test on Images 29-40; 35 image won't work
        centerX, centerY = contour.getObjectLocation(fileName)
        u_adjusted = (centerX[0]*1.0-cx)/fx
        v_adjusted = (centerY[0]*1.0-cy)/fy
        sol = fsolve(func, [1, 1,1,1,1])
        #print(sol)
        z_c = z_c0-z_object+robotPosition[imageIndex][2]#z Distance from object to camera
        x_c = sol[3]*z_c;
        y_c = sol[4]*z_c;

        x_e = x_c*1.0;
        y_e = -y_c*1.0-61.0+300.0;#y axis is flipped and translated upwards 
        z_e = 0.0;#dummy z

        P_e = np.array([[x_e],[y_e], [z_e], [1]])
        theta = np.arcsin(robotPosition[imageIndex][0]/math.sqrt(robotPosition[imageIndex][0]**2+robotPosition[imageIndex][1]**2))        
        T_r_e=np.array([[np.cos(theta), np.sin(theta), 0.0,robotPosition[imageIndex][0]*1.0], 
            [-np.sin(theta), np.cos(theta), 0.0,robotPosition[imageIndex][1]*1.0], 
            [0.0, 0.0, 1.0, robotPosition[imageIndex][2]*1.0],
            [0.0, 0.0, 0.0, 1.0]])
        
        #print(T_r_e)
        print(fileName)
        P_r = T_r_e * P_e;
        print(P_r[0],P_r[1])
        print("="*80)
        imageIndex+=1;







# centerX, centerY = contour.getObjectLocation("testImages/29.jpg")
# u_adjusted = (centerX[0]*1.0-cx)/fx
# v_adjusted = (centerY[0]*1.0-cy)/fy
# print(centerX[0],centerY[0])
# sol = fsolve(func, [1, 1,1,1,1])
# print(sol)
# x_c = sol[3]*z_c;
# y_c = sol[4]*z_c;
# print(x_c,y_c)
# print(np.isclose(func(sol), [0.0, 0.0,0.0,0.0,0.0]))
# print("="*80)



# centerX, centerY = contour.getObjectLocation("testImages/32.jpg")
# u_adjusted = (centerX[0]*1.0-cx)/fx
# v_adjusted = (centerY[0]*1.0-cy)/fy
# print(centerX[0],centerY[0])
# sol = fsolve(func, [1, 1,1,1,1])
# print(sol)
# x_c = sol[3]*z_c;
# y_c = sol[4]*z_c;
# print(x_c,y_c)







# # exprTheta = theta-atan(r)
# exprFisheyeDistortion = theta_d-theta*(1+k1*theta**2+k2*theta**4+k3*theta**6+k4*theta**8)
# exprR2 = r**2-a**2-b**2;




# u=centerX[0]
# v = centerY[0]
#theta_d, theta, a ,b,r = symbols('theta_d, theta, a, b,r')
# exprU = (u*1.0-cx)/fx-theta_d*a/r;
# exprV = (v*1.0-cy)/fy-theta_d*b/r;
# #sol = solve((exprTheta,exprFisheyeDistortion,exprR2,exprU,exprV), (theta,a,b,theta_d,r))