import cv2
import numpy as np
import os
import glob
DIM=(1920,1080)

K = np.load("cImages/K.npy", mmap_mode=None, allow_pickle=False, fix_imports=True, encoding='ASCII')
D = np.load("cImages/D.npy", mmap_mode=None, allow_pickle=False, fix_imports=True, encoding='ASCII')

def undistort(img_path):
    img = cv2.imread(img_path)
    h,w = img.shape[:2]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
    undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    cv2.imshow("undistorted", undistorted_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # Create the output file name by removing the '.jpg' part
    size = len(img_path)
    new_filename = img_path[11:size - 4]
    new_filename = "undistorted/"+new_filename + '_undistorted.jpg'
        
    # Save the undistorted image
    cv2.imwrite(new_filename, undistorted_img)
if __name__ == '__main__':
    images = glob.glob('distorted/*.jpg')
    for fname in images:
        undistort(fname)