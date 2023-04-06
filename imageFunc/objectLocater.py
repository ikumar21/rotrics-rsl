import cv2
import numpy as np
import math
import undistort
from Cam_dev import *
from statistics import mean
# import matplotlib.pyplot as plt

DIM=(1920,1080)

def threshPic(undistortedImg):
    grayImg = cv2.cvtColor(undistortedImg, cv2.COLOR_BGR2GRAY)
    gs_img = cv2.GaussianBlur(grayImg, (5, 5), 0) 
    threshA = cv2.threshold(gs_img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    return threshA;

def correctHSV(hsvArray):
    #Returns tuple : (H,S,V) in correct format: 0-360degrees, 0-100%, 0-100%
    return round(hsvArray[0]*2.0), round(100.0*hsvArray[1]/255.0,1), round(100.0*hsvArray[2]/255.0,1)

def meanHSV(yPixelLocationsArr,xPixelLocationsArr, imgHSV):
    #imgHSV[yPixelLocation][xPixelLocation]= [H,S,V]
    avgH = mean([float(imgHSV[yPixelLocationsArr[indexPixel]][xPixelLocationsArr[indexPixel]][0]) for indexPixel in range(len(yPixelLocationsArr))])
    avgS = mean([float(imgHSV[yPixelLocationsArr[indexPixel]][xPixelLocationsArr[indexPixel]][1]) for indexPixel in range(len(yPixelLocationsArr))])
    avgV = mean([float(imgHSV[yPixelLocationsArr[indexPixel]][xPixelLocationsArr[indexPixel]][2]) for indexPixel in range(len(yPixelLocationsArr))])
    return [avgH,avgS,avgV]

def recogn_main():
    video.open(0,1920,1080)
    while True:
        img = video.get_img(0)
        undistortedImg = undistort.undistort(img, showImage=False) 
        thresholdPic = threshPic(undistortedImg=undistortedImg)
        threshA = thresholdPic
        cv2.imshow('noC', thresholdPic)
        contours, hierarchy = cv2.findContours(image=threshA, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)
        threshA = cv2.cvtColor(threshA,cv2.COLOR_GRAY2BGR)
        centerX =[]
        centerY = []

        for c in contours:
            x,y,w,h = cv2.boundingRect(c)
            xs = [v[0][0] for v in c]
            ys = [DIM[1]-v[0][1] for v in c]
            # plt.plot(xs,ys) 
            # plt.grid()
            # plt.show()
            if(w*h<0.95*DIM[0]*DIM[1]and w*h>0.0003*DIM[0]*DIM[1]):#Don't plot if too big or too small
                print("Area",w*h)
                print("=" * 80)
                cv2.drawContours(threshA, [c], -1, (0, 255, 0), 2)
                M = cv2.moments(c)
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
                print(img[cY][cX])

        objectLocations = []
        # For each list of contour points...
        for i in range(len(contours)):
            # Create a mask image that contains the contour filled in
            cimg = np.zeros_like(img)
            cv2.drawContours(cimg, contours, i, color=255, thickness=-1)
            #cv2.imshow("object{}".format(i+1),cimg)
            # Access the image pixels and create a 1D numpy array then add to list
            pts = np.where(cimg == 255)
            objectLocations.append(pts)
            # print("=" * 80)
            # print(pts)
            
            #cv2.putText(img, "{0}".format(i+1), (centerX[i], centerY[i]),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0),2)

        cv2.imshow('original', img)

        for i in range(len(centerX)):
            print("Object {0} Center: x={1} ; y ={2}".format(i+1,centerX[i],centerY[i]))


        k = cv2.waitKey(1)
        if k%256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break
    pass
    pass

if __name__ == "__main__":
    recogn_main()
    pass