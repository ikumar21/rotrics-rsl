import cv2
import numpy as np
import math
import undistort
from statistics import mean
# import matplotlib.pyplot as plt

img_path = "testImages/50.jpg"







def allHSV(yPixelLocationsArr,xPixelLocationsArr, imgHSV):#Returns all HSV and their occurence
    #Input yPixelLocationsArr : [yPos0, yPos1, ..]
    #Input xPixelLocationsArr : [xPos0, xPos1, ..]
    #Input imgHSV: image in HSV

    #Returns [[H0,S0,V0],[H1,S1,V1], ...], [count0, count1, ...]
    #imgHSV[yPixelLocation][xPixelLocation]= [H,S,V]
    allHSV = []
    countHSV = []
    for indexPixel in range(len(yPixelLocationsArr)):
        hsvValue = imgHSV[yPixelLocationsArr[indexPixel]][xPixelLocationsArr[indexPixel]];
        try:
            indexInHSV = allHSV.index(hsvValue.tolist())
        except:
            indexInHSV = -1
        if indexInHSV ==-1:#HSV value not in array
            allHSV.append(hsvValue.tolist())
            countHSV.append(1)
        else:#Increment count
            countHSV[indexInHSV]+=1

    return allHSV,countHSV









def cropImg(contours, img):
    for contour in contours:
        grayImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        mask = np.zeros_like(grayImg)
        cv2.drawContours(mask, contours, 0, color=255, thickness=-1)
        perimeter = cv2.arcLength(contour, True)
        vertices = cv2.approxPolyDP(contour, 0.04 * perimeter, True);
        minY = min([elem[0][1] for elem in vertices])
        maxY = max([elem[0][1] for elem in vertices])
        maxX = max([elem[0][0] for elem in vertices])
        minX = min([elem[0][0] for elem in vertices])
        crop_img = img[minY:maxY, minX:maxX].copy()
        mask = mask[minY:maxY, minX:maxX];
        grayImg = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
        pts = np.where(mask != 255)
        yPixelLocationsArr,xPixelLocationsArr = pts[0],pts[1]
        for indexPixel in range(len(yPixelLocationsArr)):
            crop_img[yPixelLocationsArr[indexPixel]][xPixelLocationsArr[indexPixel]]=(128,151,166);
        cv2.imshow("New Image", crop_img);
        while True:
            k = cv2.waitKey(1)
            if k%256 == 27:
                # ESC pressed
                print("Escape hit, closing...")
                break
        return crop_img
    




def runStuff(imgBGR, whiteBackground):
    imgHSV = cv2.cvtColor(imgBGR, cv2.COLOR_BGR2HSV)
    dimensions = imgBGR.shape#Get dimensions of image to eliminate small contours
    thresholdPic = threshPic(imgBGR)
    if(whiteBackground==True):#If Objects are white, invert so it becomes black background/white objects
        thresholdPic = cv2.bitwise_not(thresholdPic)#Invert Image

    threshColor = cv2.cvtColor(thresholdPic,cv2.COLOR_GRAY2BGR)#Convert Gray image to BGR to have Markings in color

    centerX,centerY, contours = getDrawContour(imgThreshBGR=threshColor,imgThreshGray=thresholdPic)
    
    print(centerX,centerY)
    shapes = getObjectShape(contours)
    print(shapes)
    cv2.imshow('thresh', threshColor)
    cv2.imshow('src_img', imgBGR)

    while True:
        k = cv2.waitKey(1)
        if k%256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break

#Already Implemented:
def colorRecog(hsv):#Input hsv value -> [H,S,V]
    #output: color in string all capitilized
    hVal = hsv[0]
    sVal = hsv[1]
    vVal = hsv[2]
    if(sVal<10):#Could be white, Gray or white
        if(vVal >=90):
            return "WHITE"
        elif(vVal<=6):
            return "BLACK"
        else:
            return "GRAY"
    if(0<=hVal<=30 or 330<=hVal<=360):
        return "RED"
    elif(30<=hVal<=50):
        return "ORANGE"
    elif(50<=hVal<=90):
        return "YELLOW"
    elif(90<=hVal<=150):
        return "GREEN"
    elif(150<=hVal<=210):
        return "CYAN"
    elif(210<=hVal<=270):
        return "BLUE"
    elif(270<=hVal<=330):
        return "MAGENTA"
    else:
        return "ERROR"



def meanHSV(yPixelLocationsArr,xPixelLocationsArr, imgHSV):#Returns mean HSV in area
    #imgHSV[yPixelLocation][xPixelLocation]= [H,S,V]
    avgH = mean([float(imgHSV[yPixelLocationsArr[indexPixel]][xPixelLocationsArr[indexPixel]][0]) for indexPixel in range(len(yPixelLocationsArr))])
    avgS = mean([float(imgHSV[yPixelLocationsArr[indexPixel]][xPixelLocationsArr[indexPixel]][1]) for indexPixel in range(len(yPixelLocationsArr))])
    avgV = mean([float(imgHSV[yPixelLocationsArr[indexPixel]][xPixelLocationsArr[indexPixel]][2]) for indexPixel in range(len(yPixelLocationsArr))])
    return [avgH,avgS,avgV]
def correctHSV(hsvArray):
    #Returns tuple : (H,S,V) in correct format: 0-360degrees, 0-100%, 0-100%
    return round(hsvArray[0]*2.0), round(100.0*hsvArray[1]/255.0,1), round(100.0*hsvArray[2]/255.0,1)
def pixelsInContour(contours,img):
    objectLocations = []
    # For each list of contour points...
    for i in range(len(contours)):
        # Create a mask image that contains the contour filled in
        cimg = np.zeros_like(img)

        #cimg = np.full((1080, 1920), 0, dtype=np.int32)
        
        cv2.drawContours(cimg, contours, i, color=255, thickness=-1)
        #cv2.imshow("object{}".format(i+1),cimg)
        # Access the image pixels and create a 1D numpy array then add to list
        pts = np.where(cimg == 255)
        #cv2.drawContours(emptyImg, contours, i, color=0, thickness=-1)#reset
        objectLocations.append(pts)
    return objectLocations
def getObjectLocation(imgBGR):
    objectWhite= False;
    imgBGR = cv2.imread(imgBGR)
    imgHSV = cv2.cvtColor(imgBGR, cv2.COLOR_BGR2HSV)
    dimensions = imgBGR.shape#Get dimensions of image to eliminate small contours
    simpleImage = cv2.cvtColor(imgBGR, cv2.COLOR_BGR2GRAY)

    #imgBGR = undistort.undistort(img, showImage=False) 

    thresholdPic = threshPic(imgBGR)
    if(objectWhite):#If Objects are white, invert so it becomes black background/white objects
        thresholdPic = cv2.bitwise_not(thresholdPic)#Invert Image

    threshColor = cv2.cvtColor(thresholdPic,cv2.COLOR_GRAY2BGR)#Convert Gray image to BGR to have Markings in color
    centerX,centerY, contours = getDrawContour(imgThreshBGR=threshColor,imgThreshGray=thresholdPic)
    return centerX,centerY

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
    numberCount =0;
    actualContours=[];
    for c in contours:
        x,y,w,h = cv2.boundingRect(c)#Get Width and Height of each object
        if(w*h<0.95*dimensions[0]*dimensions[1]and w*h>0.003*dimensions[0]*dimensions[1]):#Don't plot if too big or too small
            actualContours.append(c)
            numberCount+=1
            cv2.drawContours(imgThreshBGR, [c], -1, (0, 255, 0), 2)#Draw Contours in Green
            M = cv2.moments(c)
            if M["m00"] != 0:#Found Center, don't divide by 0
                # print("FOUND, Area:",w*h)
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                centerX.append(cX)
                centerY.append(cY)
                cv2.circle(imgThreshBGR, (cX, cY), 7, (0, 0, 255), -1)
                cv2.putText(imgThreshBGR, "center"+str(numberCount), (cX - 20, cY - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            # draw the contour and center of the shape on the image

    return centerX,centerY, actualContours

def getObjectShape(contours):
    def shapeFromVertice(vertices, shapes, num):
        prefix = "Object " +str(num)+": "
        numVertices = len(vertices);
        if(numVertices==3):
            shapes.append(prefix+"Triangle")
        elif(numVertices==4):
            shapes.append(prefix+"Rectangle")
        else:
            shapes.append(prefix+str(numVertices)+" edges")
    allShapes=[];
    allVertices = [];
    for num in range(len(contours)):
        contour = contours[num];
        perimeter = cv2.arcLength(contour, True)
        vertices = cv2.approxPolyDP(contour, 0.04 * perimeter, True);
        allVertices.append(vertices)
        shapeFromVertice(vertices, allShapes, num+1)
    return allShapes;




if __name__ == "__main__":
    objectWhite= True;
    imgBGR = cv2.imread(img_path)
    imgHSV = cv2.cvtColor(imgBGR, cv2.COLOR_BGR2HSV)
    dimensions = imgBGR.shape#Get dimensions of image to eliminate small contours
    simpleImage = cv2.cvtColor(imgBGR, cv2.COLOR_BGR2GRAY)

    #imgBGR = undistort.undistort(img, showImage=False) 

    thresholdPic = threshPic(imgBGR)
    if(objectWhite):#If Objects are white, invert so it becomes black background/white objects
        thresholdPic = cv2.bitwise_not(thresholdPic)#Invert Image

    threshColor = cv2.cvtColor(thresholdPic,cv2.COLOR_GRAY2BGR)#Convert Gray image to BGR to have Markings in color

    centerX,centerY, contours = getDrawContour(imgThreshBGR=threshColor,imgThreshGray=thresholdPic)
    
    print(centerX,centerY)
    shapes = getObjectShape(contours)
    print(shapes)

    objects = pixelsInContour(contours,imgBGR)
    allObjectsHSV = [];
    for object in objects:
        objectHSV = meanHSV(object[0],object[1],imgHSV);
        allObjectsHSV.append(objectHSV)
        print(correctHSV(objectHSV),colorRecog(correctHSV(objectHSV)))




    #runStuff(cropImg(contours, imgBGR),True)






    #getObjectColor(contours,simpleImage,imgHSV)
    cv2.imshow('thresh', threshColor)
    cv2.imshow('src_img', imgBGR)

    while True:
        k = cv2.waitKey(1)
        if k%256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break
