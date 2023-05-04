import cv2
import pytesseract
import glob
#Uncomment next line for Windows:
#pytesseract.pytesseract.tesseract_cmd=r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'


DIM=(1920,1080)
if __name__ == "__main__":
    text  =[];
    images  = glob.glob('testImages/3.jpg')
    images.sort()
    for imgName in images:
        img = cv2.imread(imgName)
        grayImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        #noise removal
        noiseRemovImg3=cv2.medianBlur(grayImg,3)
        noiseRemovImg5=cv2.medianBlur(grayImg,5)
        noiseRemovImg7=cv2.medianBlur(grayImg,7)
        
        # thresholding# converting it to binary image by Thresholding
        # this step is require if you have colored image because if you skip this part
        # then tesseract won’t able to detect text correctly and this will give incorrect #result
        thresh = cv2.threshold(grayImg, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        noiseRemovImg3=cv2.bilateralFilter(grayImg,9,1,1)
        thresh3 = cv2.threshold(noiseRemovImg3, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        thresh5 = cv2.threshold(noiseRemovImg5, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        thresh7 = cv2.threshold(noiseRemovImg7, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        cv2.imshow("thresh",thresh)
        cv2.imshow("thresh3",thresh3)
        cv2.imshow("thresh7",thresh7)
        cv2.imshow("thresh5",thresh5)
        while True:
            k = cv2.waitKey(1)
            if k%256 == 27:
                # ESC pressed
                print("Escape hit, closing...")
                break

        #Configuration
        #config = ('-l eng — oem 3 — psm 3')

        text.append(pytesseract.image_to_string(thresh))
        text.append(pytesseract.image_to_string(thresh5))
        text.append(pytesseract.image_to_string(thresh7))
    print(text)

