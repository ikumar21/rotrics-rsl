import cv2
import pytesseract
import numpy as np
import math
from Cam_dev import *
from PIL import Image
import time


pytesseract.pytesseract.tesseract_cmd=r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
# 800*600
#Camera 1920 x 1080
if __name__ == "__main__":
    # pythonImg = cv2.imread("py.png")
    # text = pytesseract.image_to_string(pythonImg)
    # print(text)
    # video.open(1,800,600)
    # imgC1 = video.get_img(1)
    # imgC0 = video.get_img(0)
    # cv2.imwrite("robotC0.jpg", imgC0)
    # cv2.imwrite("robotC1.jpg", imgC1)
    # video.close()
    video.open(1,800,600)
    imgB1 = video.get_img(1)
    imgB0 = video.get_img(0)
    cv2.imwrite("robotC0num1.png", imgB0)
    cv2.imwrite("robotC1num2.png", imgB1)
    text = []
    time.sleep(5)
    # pythonImg = cv2.imread("robotBO.jpg")
    # text[0] =  pytesseract.image_to_string(pythonImg)
    
    
    #img1 = cv2.cvtColor(imgB0, cv2.COLOR_BGR2RGB)
    # text[1] =   pytesseract.image_to_string(Image.fromarray(imgB1))
    
    # text[3] =  pytesseract.image_to_string(imgC1)
    # text[2] =  pytesseract.image_to_string(imgC0)
    print(text)