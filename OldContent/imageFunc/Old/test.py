import cv2
import numpy as np
import math
import undistort
from statistics import mean
import time


def pixelsInContour(contours,img, emptyImg):
    objectLocations = []
    # For each list of contour points...
    for i in range(len(contours)):
        # Create a mask image that contains the contour filled in
        cimg = np.zeros_like(img)

        #cimg = np.full((1080, 1920), 0, dtype=np.int32)
        
        cv2.drawContours(cimg, contours, i, color=255, thickness=-1)
        cv2.imshow("object{}".format(i+1),cimg)
        # Access the image pixels and create a 1D numpy array then add to list
        pts = np.where(cimg == 255)
        #cv2.drawContours(emptyImg, contours, i, color=0, thickness=-1)#reset
        objectLocations.append(pts)
    return objectLocations



def getDrawContour(imgThreshBGR,imgThreshGray):
    contours, hierarchy = cv2.findContours(image=imgThreshGray, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)#Find contours
    dimensions = imgThreshBGR.shape#Find pixel dimensions
    centerX =[]#x location of each object's center
    centerY = []#y location of each object's center
    for c in contours:
        x,y,w,h = cv2.boundingRect(c)#Get Width and Height of each object
        #Get Contour x/y end points
        # xs = [v[0][0] for v in c] 
        # ys = [dimensions[0]-v[0][1] for v in c]
        # # plt.plot(xs,ys) 
        # # plt.grid()
        # # plt.show()
        if(w*h<0.95*dimensions[0]*dimensions[1]and w*h>0.003*dimensions[0]*dimensions[1]):#Don't plot if too big or too small
            cv2.drawContours(imgThreshBGR, [c], -1, (0, 255, 0), 2)#Draw Contours in Green
            M = cv2.moments(c)
            if M["m00"] != 0:#Found Center, don't divide by 0
                print("FOUND")
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                centerX.append(cX)
                centerY.append(cY)
                cv2.circle(imgThreshBGR, (cX, cY), 7, (0, 0, 255), -1)
                cv2.putText(imgThreshBGR, "center", (cX - 20, cY - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            # draw the contour and center of the shape on the image
            print(imgThreshBGR[cY][cX])
    return centerX,centerY, contours


img_path = "testImages/17.jpg"
img = cv2.imread(img_path)
imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
dimensions = img.shape#Get dimensions of image to eliminate small contours

def threshPic(undistortedImg):
    grayImg = cv2.cvtColor(undistortedImg, cv2.COLOR_BGR2GRAY)
    gs_img = cv2.GaussianBlur(grayImg, (5, 5), 0) 
    threshA = cv2.threshold(gs_img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    return threshA;

thresholdPic = threshPic(cv2.imread(img_path))
threshColor = cv2.cvtColor(thresholdPic,cv2.COLOR_GRAY2BGR)

x,y, contours = getDrawContour(threshColor,thresholdPic)
emptyImg = np.zeros_like(thresholdPic)

start_time = time.time()
for i in range(100):
    pixelsInContour(contours,threshColor,emptyImg)


print(time.time()-start_time)
