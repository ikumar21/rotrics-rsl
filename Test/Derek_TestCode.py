from pydexarm import Dexarm
#from pydexarm import Dexarm
#import time
#import math 
#from random import randint

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





cam = cv2.VideoCapture(0)
ret,img = cam.read()
cam.release()


if (img.shape[0] == 480):
    print("640x480")

# 640*480 Small Camera:
CAMERA_SMALL_MATRIX = np.array([[7.9641507015667764e+02,0.,3.1577913194699374e+02],[0.,7.9661307355876215e+02, 2.1453452136833957e+02],[0.,0.,1.]])
DIST_COEFF_SMALL = np.array([[-1.1949335317713690e+00,1.8078010700662486e+00,4.9410258870084744e-03,2.8036176641915598e-03,-2.0575845684235938e+00]])

img = cv2.undistort(img, CAMERA_SMALL_MATRIX, DIST_COEFF_SMALL, None)
#cv2.imwrite("test.png", undistortedImg)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#blur = cv2.GaussianBlur(gray,(5,5),0) 
_,thresh = cv2.threshold(gray,127,255,cv2.THRESH_BINARY)#0,255

#thresh = cv2.bitwise_not(thresh)

contours,hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

disp = img
i = 0
for contour in contours:
    if i == 0:
        i = 1
        continue

    approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour,True),True)
    print(len(approx))
    cv2.drawContours(disp,[contour],0,(0,0,255),5)

    M = cv2.moments(contour)
    if M['m00'] != 0.0:
        x = int(M['m10']/M['m00'])
        y = int(M['m01']/M['m00'])
    if len(approx) == 1:
        cv2.putText(disp,'Crc',(x,y),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,255,255),2)
    if len(approx) == 4:
        cv2.putText(disp,'Sqr',(x,y),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,255,255),2)
    if len(approx) == 3:
        cv2.putText(disp,'Tri',(x,y),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,255,255),2)

#print(i)

#show image until user presses ESC:
while True:
    cv2.imshow("Display", disp)
    k = cv2.waitKey(1)
    if k%256 == 27:
        break





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