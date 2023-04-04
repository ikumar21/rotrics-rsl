import cv2
import numpy as np
import math
import undistort
from Cam_dev import *
import imutils

DIM=(1920,1080)
def recogn_main():
    video.open(1,1920,1080)
    while True:
        img = video.get_img(0)
        undistortedImg = undistort.undistort(img, showImage=False) 
        grayImg = cv2.cvtColor(undistortedImg, cv2.COLOR_BGR2GRAY)
        gs_img = cv2.GaussianBlur(grayImg, (5, 5), 0) 
        threshA = cv2.threshold(gs_img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        gs_imgNoGray = cv2.GaussianBlur(undistortedImg, (5, 5), 0) 
        #threshA = cv2.cvtColor(threshA,cv2.COLOR_GRAY2BGR)
        contours, hierarchy = cv2.findContours(image=threshA, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)
        # print("=" * 80)
        # print(contours)
        cnts = contours[0] if len(contours) == 2 else contours[1]
        threshA = cv2.cvtColor(threshA,cv2.COLOR_GRAY2BGR)
        #cv2.drawContours(image=threshA, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=5, lineType=cv2.LINE_AA)
        #cnts = imutils.grab_contours(contours)
        x,y,w,h = cv2.boundingRect(contours)
        print("=" * 80)
        print(x)



        for c in cnts:
            # compute the center of the contour
            M = cv2.moments(c)
            print("=" * 80)
            print(M)
            if M["m00"] != 0:
                print("FOUND")
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            else:
                # Skip this contour
                continue
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            # draw the contour and center of the shape on the image
            cv2.drawContours(threshA, [c], -1, (0, 255, 0), 2)
            cv2.circle(threshA, (cX, cY), 7, (255, 255, 255), -1)
            cv2.putText(threshA, "center", (cX - 20, cY - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        # for rect in contours:
        #     cv2.rectangle(threshA,(100,500),(960,540),(0,255,0),5)
        cv2.imshow('thresholdA', threshA)
        cv2.imshow('undistorted', undistortedImg)
        k = cv2.waitKey(1)
        if k%256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break
        cv2.waitKey(30)
    pass
    pass

if __name__ == "__main__":
    recogn_main()
    pass