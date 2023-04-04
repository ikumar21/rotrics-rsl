import cv2
import numpy as np
import math
import undistort
from Cam_dev import *
import imutils



img_path = "testImages/14.jpg"
undistortedImg = cv2.imread(img_path) 
grayImg = cv2.cvtColor(undistortedImg, cv2.COLOR_BGR2GRAY)
gs_img = cv2.GaussianBlur(grayImg, (5, 5), 0) 
threshA = cv2.threshold(gs_img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
dimensions = threshA.shape
print(dimensions)


contours, hierarchy = cv2.findContours(image=threshA, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)
threshA = cv2.cvtColor(threshA,cv2.COLOR_GRAY2BGR)
cv2.imshow('noC', threshA)

# print(contours)
print("=" * 80)
print(contours[0])
# print("=" * 80)
# print(contours[1])
centerX =[]
centerY = []
for c in contours:
    x,y,w,h = cv2.boundingRect(c)
    if(w*h<0.95*dimensions[0]*dimensions[1]and w*h>0.0003*dimensions[0]*dimensions[1]):#Don't plot if too big or too small
        print("Area",w*h)
        print("=" * 80)
        cv2.drawContours(threshA, [c], -1, (0, 255, 0), 2)
        M = cv2.moments(c)
        print("=" * 80)
        print(M)
        if M["m00"] != 0:#Found Center
            print("FOUND")
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            centerX.append(cX)
            centerY.append(cY)
            cv2.circle(threshA, (cX, cY), 7, (0, 0, 255), -1)
            cv2.putText(threshA, "center", (cX - 20, cY - 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        # draw the contour and center of the shape on the image
        cv2.drawContours(threshA, [c], -1, (0, 255, 0), 2)

for i in range(len(centerX)):
    print("Object {0} Center: x={1} ; y ={2}".format(i+1,centerX[i],centerY[i]))
cv2.imshow('thresholdA', threshA)
while True:
    cv2.imshow('thresholdA', threshA)
    k = cv2.waitKey(1)
    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break