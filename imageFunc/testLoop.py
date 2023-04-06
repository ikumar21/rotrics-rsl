import cv2
import numpy as np
import math
import undistort
from Cam_dev import *
from statistics import mean
import time
def correctHSV(hsvArray):
    #Returns tuple : (H,S,V) in correct format: 0-360degrees, 0-100%, 0-100%
    return round(hsvArray[0]*2.0), round(100.0*hsvArray[1]/255.0,1), round(100.0*hsvArray[2]/255.0,1)

def meanHSV(yPixelLocationsArr,xPixelLocationsArr, imgHSV):
    #imgHSV[yPixelLocation][xPixelLocation]= [H,S,V]
    avgH = mean([float(imgHSV[yPixelLocationsArr[indexPixel]][xPixelLocationsArr[indexPixel]][0]) for indexPixel in range(len(yPixelLocationsArr))])
    avgS = mean([float(imgHSV[yPixelLocationsArr[indexPixel]][xPixelLocationsArr[indexPixel]][1]) for indexPixel in range(len(yPixelLocationsArr))])
    avgV = mean([float(imgHSV[yPixelLocationsArr[indexPixel]][xPixelLocationsArr[indexPixel]][2]) for indexPixel in range(len(yPixelLocationsArr))])
    return [avgH,avgS,avgV]


def pixelsInContour(contours,img):
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
    return objectLocations


def threshPic(undistortedImg):
    grayImg = cv2.cvtColor(undistortedImg, cv2.COLOR_BGR2GRAY)
    gs_img = cv2.GaussianBlur(grayImg, (5, 5), 0) 
    threshA = cv2.threshold(gs_img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    return threshA;


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

def recogn_main():
    global time
    video.open(0,1920,1080)
    
    hsv = cv2.cvtColor(video.get_img(0), cv2.COLOR_BGR2HSV)
    print(len(hsv[5]))
    count = 0;
    times = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
    while True:
        count +=1;

        start_time = time.time()
        img=video.get_img(0)
        times[0]+=time.time()-start_time;

        start_time = time.time()
        undistortedImg = undistort.undistort(img, showImage=False) 
        times[1]+=time.time()-start_time;

        start_time = time.time()
        thresholdPic = threshPic(undistortedImg)
        threshGray = cv2.bitwise_not(thresholdPic)#Invert Image -> White background, black objects
        threshColor = cv2.cvtColor(threshGray,cv2.COLOR_GRAY2BGR)#Convert Gray image to BGR to have Markings in color
        times[2]+=time.time()-start_time;

        start_time = time.time()
        centerX,centerY, contours = getDrawContour(imgThreshBGR=threshColor,imgThreshGray=threshGray)
        times[3]+=time.time()-start_time;

        start_time = time.time()
        objectLocations = pixelsInContour(contours,img)
        times[4]+=time.time()-start_time;

        start_time = time.time()
        cv2.imshow('thresh', threshColor)
        times[5]+=time.time()-start_time;

        start_time = time.time()
        cv2.imshow('src_img', img)
        times[6]+=time.time()-start_time;



        start_time = time.time()
        k = cv2.waitKey(1)
        if k%256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break
        cv2.waitKey(3)
        times[7]+=time.time()-start_time;


        if(count >= 100):
            break
    for time in times:
        print("="*80)
        print(time)

if __name__ == "__main__":
    recogn_main()
    pass