#Old 


import cv2
import numpy as np
import os
import glob
DIM=(1920,1080)

K = np.load("cImages/K.npy", mmap_mode=None, allow_pickle=False, fix_imports=True, encoding='ASCII')
D = np.load("cImages/D.npy", mmap_mode=None, allow_pickle=False, fix_imports=True, encoding='ASCII')
map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
def undistort(img,showImage):
    #img =cv2.imread(img_path)
    undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    if(showImage==True):
        cv2.imshow("undistorted", undistorted_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return undistorted_img; 
    # Save the undistorted image
    cv2.imwrite(new_filename, undistorted_img)

