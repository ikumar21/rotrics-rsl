#Analyze image with image module
import sys
import os
# adding folder to the system path
sys.path.insert(0, '../imageFunc')
sys.path.insert(0, '../')
#sys.path.insert(0, 'C:/Users/rsl/Desktop/rotrics-rsl/imageFunc')
import image_module as i_m
import cv2
import glob
import numpy as np
import time

imageFiles = glob.glob("testImages/26.jpg");


for img_path in imageFiles:
    imgBGR = cv2.imread(img_path)

    parameters = i_m.Open_CV_Parameters()
    parameters.whiteBackground=False;
    img_data = i_m.Open_CV_Analysis(imgBGR, parameters)

    #Create White Image
    contourImageData = np.zeros([1080,1920,3],dtype=np.uint8)
    contourImageData.fill(255)


    # concatenate actual and Threshold image Horizontally & contour and contour Data Image horziontally
    smallActualImg = cv2.resize(img_data.imageBGR, (800,450), interpolation = cv2.INTER_AREA)
    smallThresholdImg = cv2.resize(img_data.thresholdBGR, (800,450), interpolation = cv2.INTER_AREA)
    actualThreshold = np.concatenate((smallActualImg, smallThresholdImg), axis=1)
    smallContourImg = cv2.resize(img_data.contourImageBGR,(800,450), interpolation = cv2.INTER_AREA)
    smallContourDataImg = cv2.resize(contourImageData, (800,450), interpolation = cv2.INTER_AREA)
    contourData = np.concatenate((smallContourImg, smallContourDataImg), axis=1)

    # concatenate 4 images Vertically
    allImages = np.concatenate((actualThreshold, contourData), axis=0)

    img_data.FindCropImgBGR();

    cv2.imshow("Analysis", allImages)
    for contour_obj in img_data.contour_objects:
        cropInnerImg = contour_obj.cropImgBGR;
        cv2.imshow("Crop",cropInnerImg)

        parameters.whiteBackground=True;
        innerImg_data = i_m.Open_CV_Analysis(cropInnerImg,parameters)

        #Create White Image
        contourImageData = np.zeros([1080,1920,3],dtype=np.uint8)
        contourImageData.fill(255)

        cv2.imshow("Inner Thresh analysis", innerImg_data.thresholdBGR)
        cv2.imshow("Inner analysis", innerImg_data.contourImageBGR)
        #cv2.imshow("Inner analysis", innerImg_data.thresholdBGR)


        while True:
            k = cv2.waitKey(10)
            # ESC pressed:Exit Program
            if k%256 == 27:
                print("Escape hit, closing...")
                break