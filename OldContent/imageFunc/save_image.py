#Script to look at camera live and take images so it can be processed later using other scripts
#Images are saved in testImages Folder
#Press space to save image
#Press esc to exit program

import sys
# adding folder to the system path
sys.path.insert(0, '../imageFunc')
import image_module as img_m
import cv2
import glob

directorySaveImage = 'testImages/*.jpg'

camera0 = img_m.Camera_Object(cameraNum=0,cameraType=img_m.BIG_CAMERA)


def findMaxFileName(directoryName):
    images = glob.glob(directoryName);
    maxNum = 0;
    for fileName in images:
        try:#Macbook
            num = int(fileName[fileName.index('/')+1:fileName.index('.')])
        except:
            num = int(fileName[fileName.index("\\")+1:fileName.index('.')])
        maxNum = num if num>maxNum else maxNum
    return maxNum;

while True:
    undistortedImage = camera0.GetImageBGR(undistorted=True);

    #Get Live Camera Image:
    cv2.imshow("Live Camera", undistortedImage)

    #Pause program and look for keyboard input:
    k = cv2.waitKey(1)

    if k%256 == 27:
        # ESC pressed:Exit Program
        print("Escape hit, closing...")
        break
    elif k%256 == 32:
        # SPACE pressed: Look Image
        cv2.destroyWindow("Live Camera")        
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
                    maxNum = findMaxFileName(directorySaveImage)
                    img_name = "testImages/{}.jpg".format(maxNum+1)
                    cv2.imwrite(img_name, undistortedImage)
                    print("{} written!".format(img_name))
                break





