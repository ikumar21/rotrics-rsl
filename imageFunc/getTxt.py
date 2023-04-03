import cv2
import pytesseract
import numpy as np
import math
from PIL import Image
import time
import os
import pandas as pd
import glob
#Uncomment next line for Windows:
#pytesseract.pytesseract.tesseract_cmd=r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

if __name__ == "__main__":
    text  =[];
    images  = glob.glob('testImagesTXT/*.png')
    images.sort()
    for imgName in images:
        img = cv2.imread(imgName)
        text.append([pytesseract.image_to_string(img),imgName])
    for elem in text:
        print(elem)

