from pydexarm import Dexarm
#import time
#from random import randint
import numpy as np
import math
from scipy.stats import gmean
from scipy.optimize import minimize
from statistics import mean

import sys
# adding folder to the system path
sys.path.insert(0, '../Test')

import numpy as np
#import os
#import glob
import cv2
#from google.cloud import vision
#import io
#from statistics import mean
#from scipy.optimize import fsolve
#import math

import image_moduleTest as img_m

dexarm = Dexarm(port="COM6")

#dexarm.go_home()
dexarm.move_to(None,None,50)#150


def sort_counterclockwise(points, centre):
  centre_x, centre_y = sum([x for x,_ in points])/len(points), sum([y for _,y in points])/len(points)
  angles = [math.atan2(y - centre_y, x - centre_x) for x,y in points]
  counterclockwise_indices = sorted(range(len(points)), key=lambda i: angles[i])
  counterclockwise_points = [points[i] for i in counterclockwise_indices]
  return counterclockwise_points

def shoelace(x_y):
    x_y = np.array(x_y)
    x_y = x_y.reshape(-1,2)

    x = x_y[:,0]
    y = x_y[:,1]

    S1 = np.sum(x*np.roll(y,-1))
    S2 = np.sum(y*np.roll(x,-1))

    area = .5*np.absolute(S1 - S2)

    return area

def auto_canny_edge_detection(image, sigma=0.33):
    md = np.median(image)
    lower_value = int(max(0, (1.0-sigma) * md))
    upper_value = int(min(255, (1.0+sigma) * md))
    print(lower_value,upper_value)
    print(md)
    return cv2.Canny(image, lower_value, upper_value)


cam = cv2.VideoCapture(0)
ret,img = cam.read()
cam.release()


if (img.shape[0] == 480):
    dim = img.shape
    print("640x480")

# 640*480 Small Camera:
CAMERA_SMALL_MATRIX = np.array([[7.9641507015667764e+02,0.,3.1577913194699374e+02],[0.,7.9661307355876215e+02, 2.1453452136833957e+02],[0.,0.,1.]])
DIST_COEFF_SMALL = np.array([[-1.1949335317713690e+00,1.8078010700662486e+00,4.9410258870084744e-03,2.8036176641915598e-03,-2.0575845684235938e+00]])

img = cv2.undistort(img, CAMERA_SMALL_MATRIX, DIST_COEFF_SMALL, None)
#cv2.imwrite("test.png", undistortedImg)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray,(5,5),0) 
#thresh = cv2.threshold(blur,127,255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]#127,255
thresh = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY_INV,51,7)#7,7
#thresh = auto_canny_edge_detection(blur)

#show image until user presses ESC:
while True:
    cv2.imshow("Display", thresh)
    k = cv2.waitKey(1)
    if k%256 == 27:
        break


#thresh = cv2.bitwise_not(thresh)

#grayImg = cv2.cvtColor(self.imageBGR, cv2.COLOR_BGR2GRAY)
#blurredImg = cv2.GaussianBlur(grayImg, kSize,sigmaX) 
#threshImageGray = cv2.threshold(blurredImg, 0, 255, threshType)[1]

#thresh = cv2.bitwise_not(thresh)

contours,hierarchy = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
#print(hierarchy[0])

disp = img
for i in range(1,len(contours)):
    approx = cv2.approxPolyDP(contours[i], 0.01 * cv2.arcLength(contours[i],True),True)
    #approx = contours[i]
    #cv2.drawContours(disp,[contours[i]],0,(0,0,255),3)
    
    Ai = cv2.contourArea(approx)
    print(Ai)
    
    contourPercentage = 100*Ai/(dim[0]*dim[1])
    if contourPercentage >= 95 or contourPercentage <= 0.3:
        print(contourPercentage)
        continue

    Rcenter,Rdim,Rang = cv2.minAreaRect(approx)
    Ccenter,Crad = cv2.minEnclosingCircle(approx)
    TA,Tpnts = cv2.minEnclosingTriangle(approx)

    RA = Rdim[0]*Rdim[1]
    CA = np.pi*Crad**2

    error = [abs(Ai-RA)/Ai*100,abs(Ai-TA)/Ai*100,abs(Ai-CA)/Ai*100]
    print(error)

    if error[0] < error[1] and error[0] < error[2]:
        rect = cv2.boxPoints(cv2.minAreaRect(approx))
        rect = np.int0(rect)
        
        cv2.drawContours(disp,[rect],0,(0,0,255),2)
        cv2.putText(disp,'S',np.int0(Rcenter),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,255,255),2)
    elif error[1] < error[0] and error[1] < error[2]:
        Tcenter = [np.sum(Tpnts[:,:,0])/3,np.sum(Tpnts[:,:,1])/3]

        cv2.drawContours(disp,[np.int0(Tpnts[:,0,:])],0,(0,0,255),2)
        cv2.putText(disp,'T',np.int0(Tcenter),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,255,255),2)
    else:
        cv2.putText(disp,'C',np.int0(Ccenter),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,255,255),2)
        cv2.circle(disp,np.int0(Ccenter),np.int0(Crad),(0,0,255),2)
    
    


    #M = cv2.moments(contour)
    #if M['m00'] != 0.0:
    #    x = int(M['m10']/M['m00'])
    #    y = int(M['m01']/M['m00'])
    #if len(approx) == 1:
    #    cv2.putText(disp,'Crc',(x,y),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,255,255),2)
    #if len(approx) == 4:
    #    cv2.putText(disp,'Sqr',(x,y),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,255,255),2)
    #if len(approx) == 3:
    #    cv2.putText(disp,'Tri',(x,y),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,255,255),2)


#print(rect)


#show image until user presses ESC:
while True:
    cv2.imshow("Display",disp)
    k = cv2.waitKey(1)
    if k%256 == 27:
        break

#cv2.minEnclosingTriangle(approx)




'''
cam = cv2.VideoCapture(0)
cv2.namedWindow("test")
img_counter = 0
while True:
    ret, frame = cam.read()
    if not ret:
        print("failed to grab frame")
        break
    cv2.imshow("test", frame)

    k = cv2.waitKey(1)
    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    elif k%256 == 32:
        # SPACE pressed
        img_name = "opencv_frame_{}.png".format(img_counter)
        cv2.imwrite(img_name, frame)
        print("{} written!".format(img_name))
        img_counter += 1
cam.release()
cv2.destroyAllWindows()
'''


'''
import pathlib
desktop = pathlib.Path('C:/Users/rsl/Desktop/rotrics-rsl/Test/cImages')
for item in desktop.iterdir():
    print(f"{item} - {'dir' if item.is_dir() else 'file'}")
'''
'''
#1920*1080 camera:
#Import Undistortion constants
K = np.load("C:/Users/rsl/Desktop/rotrics-rsl/Test/cImages/K.npy", mmap_mode=None, allow_pickle=False, fix_imports=True, encoding='ASCII')
D = np.load("C:/Users/rsl/Desktop/rotrics-rsl/Test/cImages/D.npy", mmap_mode=None, allow_pickle=False, fix_imports=True, encoding='ASCII')

FISHEYE_K1 = D[0][0];
FISHEYE_K2 = D[1][0];
FISHEYE_K3 = D[2][0];
FISHEYE_K4 = D[3][0];
FISHEYE_FX = K[0][0]
FISHEYE_FY = K[1][1]
FISHEYE_CX = K[0][2]
FISHEYE_CY = K[1][2]

MAP_1, MAP_2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, (1920,1080), cv2.CV_16SC2)

#print(D[0][0])
#print(D)
'''