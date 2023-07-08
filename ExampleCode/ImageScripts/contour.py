#Analyze image with image module
import sys
import os
# Add Image Module
sys.path.insert(0, 'ImageModule')

# #Add Access to test images
# sys.path.insert(1, 'ExampleCode/ImageScripts/testImages')

import image_module as i_m
import cv2
import glob
import numpy as np
import time


now_ns = time.time_ns() # Time in nanoseconds
start_time = int(now_ns / 1000000) #Time in Milliseconds

print(now_ns)



imageFiles = glob.glob("ExampleCode/ImageScripts/testImages/48.jpg");


for img_path in imageFiles:
    print(img_path)
    imgBGR = cv2.imread(img_path)
    
    parameters = i_m.Open_CV_Parameters()
    parameters.whiteBackground=True;
    parameters.runFindColorContour=True;
    parameters.colorRecogType = i_m.SIMPLE_FAST_COLOR
    parameters.contourMaxArea=95;
    parameters.contourMinArea=0.05
    parameters.minEdgePercent=0.03;
    img_data = i_m.Open_CV_Analysis(imgBGR, parameters)

    #Create White Image
    contourImageData = np.zeros([1080,1920,3],dtype=np.uint8)
    contourImageData = np.zeros([508,700,3],dtype=np.uint8)
    contourImageData.fill(255)

    #Go through each contour Object and add info to white Image:
    for contourObject in img_data.contour_objects:
        contourObject:i_m.OpenCV_Contour_Data
        print(contourObject.number)
        if(type(contourObject.color[0])==list):
            for i in range(len(contourObject.color)):
                print(contourObject.colorName[i],i_m.CorrectHSV(contourObject.color[i]), contourObject.colorCount[i])
        else:
            print(contourObject.color)
        centerX = contourObject.centerLocation[0]
        centerY = contourObject.centerLocation[1]
        print(contourObject.width,contourObject.height,contourObject.centerLocation)
        textString = "Center"+ str(contourObject.number)+": "+str(contourObject.centerLocation[0])
        textString+=", "+str(contourObject.centerLocation[1])+"; Color: "
        textString+=str(contourObject.colorName)+"; Shape: "
        textString+=str(contourObject.shape)
        print(textString);
        cv2.putText(contourImageData, textString, (centerX-40, centerY-5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0,0,0), 1)


    # concatenate actual and Threshold image Horizontally & contour and contour Data Image horziontally
    smallActualImg = cv2.resize(img_data.imageBGR, (800,450), interpolation = cv2.INTER_AREA)
    smallThresholdImg = cv2.resize(img_data.thresholdBGR, (800,450), interpolation = cv2.INTER_AREA)
    actualThreshold = np.concatenate((smallActualImg, smallThresholdImg), axis=1)
    smallContourImg = cv2.resize(img_data.contourImageBGR,(800,450), interpolation = cv2.INTER_AREA)
    smallContourDataImg = cv2.resize(contourImageData, (800,450), interpolation = cv2.INTER_AREA)
    contourData = np.concatenate((smallContourImg, smallContourDataImg), axis=1)



    # concatenate 4 images Vertically
    allImages = np.concatenate((actualThreshold, contourData), axis=0)

    cv2.imshow("Analysis", allImages)
    
    now_ns = time.time_ns() # Time in nanoseconds
    stop_time = int(now_ns / 1000000) #Time in Milliseconds
    print(stop_time-start_time)
    while True:
        k = cv2.waitKey(10)
        # ESC pressed:Exit Program
        if k%256 == 27:
            print("Escape hit, closing...")
            break