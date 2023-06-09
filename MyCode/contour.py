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



imageFiles = glob.glob("MyCode/testImages/1.jpg");


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
        #print(c)
        cv2.rectangle(img_data.contourImageBGR, (198 - 0*int(contourObject.width/2), 27 - 0*int(contourObject.height/2)), (280+0*contourObject.centerLocation[1]+0 , 95+0*contourObject.centerLocation[1]+0 ), (255,255,255), 2)
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
        textString+=contourObject.shape
        cv2.putText(contourImageData, textString, (centerX - 20, centerY - 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0,0,0), 1)

    cv2.imshow("Con", img_data.contourImageBGR)

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
    

    # for contour_obj in img_data.contour_objects:
    #     cropInnerImg = contour_obj.cropImgBGR;
    #     cv2.imshow("Crop",cropInnerImg)

    #     parameters.whiteBackground=True;
    #     innerImg_data = i_m.Open_CV_Analysis(cropInnerImg,parameters)

    #     #Create White Image
    #     contourImageData = np.zeros([1080,1920,3],dtype=np.uint8)
    #     contourImageData.fill(255)

    #     cv2.imshow("Inner Thresh analysis", innerImg_data.thresholdBGR)
    #     cv2.imshow("Inner analysis", innerImg_data.contourImageBGR)
    #     #cv2.imshow("Inner analysis", innerImg_data.thresholdBGR)

    now_ns = time.time_ns() # Time in nanoseconds
    stop_time = int(now_ns / 1000000) #Time in Milliseconds
    print(stop_time-start_time)
    while True:
        k = cv2.waitKey(10)
        # ESC pressed:Exit Program
        if k%256 == 27:
            print("Escape hit, closing...")
            break