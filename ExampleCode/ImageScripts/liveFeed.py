#Script to look at live camera and see live annotations/contours
#Press esc to exit program


import sys
import os

sys.path.insert(0, 'ImageModule')
import image_module as i_m
import cv2
import glob
import numpy as np
import time

#Start up camera
camera0 = i_m.Camera_Object(cameraNum=0,cameraType=i_m.BIG_CAMERA)

while True:
    #Get undistorted image in BGR Format
    undistortedImage = camera0.GetImageBGR(undistorted=True);

    #Analyze Image:

    #Create Parameters
    parameters = i_m.Open_CV_Parameters()
    parameters.whiteBackground=True
    parameters.colorRecogType = i_m.SIMPLE_FAST_COLOR#Change default parameter for color recognition

    image_analysis = i_m.Open_CV_Analysis(imageBGR=undistortedImage,analysis_parameters= parameters)

    #Create White Image
    contourImageData = np.zeros([1080,1920,3],dtype=np.uint8)
    contourImageData.fill(255)


    #Go through each contour Object and add info to white Image:
    for contourObject in image_analysis.contour_objects:
        centerX = contourObject.centerLocation[0]
        centerY = contourObject.centerLocation[1]
        textString = "Center: "+str(contourObject.centerLocation[0])+", "+str(contourObject.centerLocation[1])+"; Color: "
        textString+=str(contourObject.colorName)+"; Shape: "
        textString+=contourObject.shape
        cv2.putText(contourImageData, textString, (centerX - 20, centerY - 20),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)

    

    # concatenate actual and Threshold image Horizontally & contour and contour Data Image horziontally
    smallActualImg = cv2.resize(image_analysis.imageBGR, (800,450), interpolation = cv2.INTER_AREA)
    smallThresholdImg = cv2.resize(image_analysis.thresholdBGR, (800,450), interpolation = cv2.INTER_AREA)
    actualThreshold = np.concatenate((smallActualImg, smallThresholdImg), axis=1)
    smallContourImg = cv2.resize(image_analysis.contourImageBGR,(800,450), interpolation = cv2.INTER_AREA)
    smallContourDataImg = cv2.resize(contourImageData, (800,450), interpolation = cv2.INTER_AREA)
    contourData = np.concatenate((smallContourImg, smallContourDataImg), axis=1)
    
    # concatenate 4 images Vertically
    allImages = np.concatenate((actualThreshold, contourData), axis=0)
    
    #Show Live Camera Analysis:
    cv2.imshow("Live Camera", allImages)

    #Pause program and look for keyboard input:
    k = cv2.waitKey(10)

    # ESC pressed:Exit Program
    if k%256 == 27:
        
        print("Escape hit, closing...")
        break






