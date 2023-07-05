#Script to look at camera live and take images so it can be processed later using other scripts
#Images are saved in testImages Folder (Make sure that folder exists)
#Press space to save image
#Press esc to exit program

import sys
import os
# adding folder to the system path
sys.path.insert(0, 'ImageModule')
import image_module as img_m
import cv2
import glob

directorySaveImage = "ExampleCode/ImageScripts/testImages/"


def saveFile(directoryName, img):
    num = 1;
    while True:
        if(os.path.exists(directoryName+str(num)+".jpg")):
           num+=1;
        else:
            img_name = directoryName+"{}.jpg".format(num)
            cv2.imwrite(img_name, img)
            print("{} written!".format(img_name))
            break;

#Start up camera
camera0 = img_m.Camera_Object(cameraNum=0,cameraType=img_m.BIG_CAMERA)

while True:
    #Get undistorted image in BGR Format
    undistortedImage = camera0.GetImageBGR(undistorted=True);

    #Show Live Camera Image:
    cv2.imshow("Live Camera", undistortedImage)

    #Pause program and look for keyboard input:
    k = cv2.waitKey(1)

    if k%256 == 27:
        # ESC pressed:Exit Program
        print("Escape hit, closing...")
        break
    elif k%256 == 32:
        # SPACE pressed: Look Image
        cv2.destroyWindow("Live Camera; Press Space to capture image")        
        cv2.imshow("Press Space to Save; Press Escape To discard", undistortedImage)

        #Wait for user input:
        while True:
            k = cv2.waitKey(1)
            if k%256 == 27 or k%256 == 32:
                cv2.destroyWindow("Press Space to Save; Press Escape To discard")
                if k%256 == 27:
                    # ESC pressed:Go back to live feed
                    print("Escape hit, closing...")
                elif k%256 == 32:
                    # Space pressed:Save Image
                    saveFile(directorySaveImage,undistortedImage)
                break





