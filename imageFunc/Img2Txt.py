import cv2
import pytesseract
import numpy as np
import math
from PIL import Image
import time
import os
import glob

#pytesseract.pytesseract.tesseract_cmd=r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

if __name__ == "__main__":
    text  =[];
    images  = glob.glob('undistorted/*.png')
    images.sort()
    for imgName in images:
        print(imgName)
        pythonImg = cv2.imread(imgName)
        text.append(pytesseract.image_to_string(pythonImg))
    for lines in text:
        for line in lines:
            print(line)