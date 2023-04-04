import cv2
import numpy as np
import os
import glob
import undistort

cam = cv2.VideoCapture(1)

cv2.namedWindow("test")

img_counter = 0

DIM=(1920,1080)

K = np.load("cImages/K.npy", mmap_mode=None, allow_pickle=False, fix_imports=True, encoding='ASCII')
D = np.load("cImages/D.npy", mmap_mode=None, allow_pickle=False, fix_imports=True, encoding='ASCII')


while True:
    ret, frame = cam.read()
    if not ret:
        print("failed to grab frame")
        break
    cv2.imshow("test", frame)
    k = cv2.waitKey(1)
    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    elif k%256 == 32:
        # SPACE pressed
        images = glob.glob('testImages/*.jpg');
        maxNum = 0;
        for fileName in images:
            num = int(fileName[fileName.index('/')+1:fileName.index('.')])
            maxNum = num if num>maxNum else maxNum
        img_name = "testImages/{}.jpg".format(maxNum+1)
        undistortedImage = undistort.undistort(frame,True)
        cv2.imwrite(img_name, undistortedImage)
        print("{} written!".format(img_name))
        img_counter += 1

cam.release()

cv2.destroyAllWindows()