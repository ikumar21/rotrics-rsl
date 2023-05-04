import numpy as np
import os
import glob
import contour
import cv2
from google.cloud import vision
import io

#Use demo to Test: https://cloud.google.com/vision#section-2

#Google Cloud:
client = vision.ImageAnnotatorClient()


#1920*1080 camera:
#Import Undistortion constants
K = np.load("cImages/K.npy", mmap_mode=None, allow_pickle=False, fix_imports=True, encoding='ASCII')
D = np.load("cImages/D.npy", mmap_mode=None, allow_pickle=False, fix_imports=True, encoding='ASCII')
map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, (1920,1080), cv2.CV_16SC2)


# 640*480 Small Camera:
cameraMatrixSmall = np.array([
                        [ 7.9641507015667764e+02, 0., 3.1577913194699374e+02], 
                        [0.,7.9661307355876215e+02, 2.1453452136833957e+02], 
                        [0., 0., 1. ]
                        ])

distCoeffsSmall = np.array([
                    [ -1.1949335317713690e+00,
                    1.8078010700662486e+00,
                    4.9410258870084744e-03, 
                    2.8036176641915598e-03,
                    -2.0575845684235938e+00]
                    ])  


class Camera_Object():#Initialize Camera-> Get undistorted/distorted Images in BGR Format
    numberCameras = 0 #Number of connected cameras
    BIG_CAMERA = 0;#1920 by 1080 pixels
    SMALL_CAMERA = 1;#640 by 480 pixels
    camera = None;
    dimensions = None;
    def __init__(self,cameraNum=0,cameraType = BIG_CAMERA):
        self.Scan()#Finds connnected cameras
        self.InitializeCamera(cameraNum);
        self.cameraType = cameraType;#Big or small camera
        pass
    def Scan(self):#Finds connnected cameras
        self.numberCameras=0
        for i in range(10):
            try:
                temp_cap = cv2.VideoCapture(i)
                if temp_cap.isOpened():
                    self.numberCameras+=1
                    temp_cap.release()
            except:
                pass
    def InitializeCamera(self, cameraNum):#Choose camera num/type, set dimensions, and open camera feed
        if(self.numberCameras==0):#No cameras found->return error
            raise NameError("No Cameras found!")
        elif(self.numberCameras>=cameraNum):
            raise NameError("Wrong Camera Index")
        else:#Correct Camera
            self.camera = cv2.VideoCapture(cameraNum)#Start Capture
            if(self.cameraType==self.BIG_CAMERA):
                self.dimensions = (1920,1080)
            else:
                self.dimensions = (640,480)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.dimensions[0])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.dimensions[1])
    def Undistort(self,img):#Undistort Image
        if(self.cameraType==self.BIG_CAMERA):
            undistortedImg = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        else:
            undistortedImg = cv2.undistort(img, cameraMatrixSmall, distCoeffsSmall, None)
        return undistortedImg; 
    def GetImageBGR(self, undistorted=True):#Get undistorted/distorted image in BGR format
        ret, distortedImage = self.camera.read()
        if(undistorted):
            return self.Undistort(distortedImage)
        else:
            return distortedImage;




class Google_Data():
    centerLocation = None; #Center Location in Pixels -> [x,y]
    confidence = None;#Confidence in that word or object identification
    rectangularVertices = [];#Vertices of Rectangular box that encloses object/text ->[[x1,y1],..,[x4,y4]]
class Google_Word(Google_Data):
    #Includes Google_Data properties -> Center Location, rectangular vertices, confidence
    wordText = "";#Word that Google is reading
class Google_Real_Object(Google_Data):
    #Includes Google_Data properties -> Center Location, rectangular vertices, confidence
    objectDescription = None;#Description of what google Cloud thinks object is    
    color = None; 


class Google_Analysis():
    imageFile=None;#Image File Name 

    real_world_objects = [];#List of Google_Real_Object Objects 

    words = [];#List of Word Objects 
    allText = None;#String containing all text
    allTextConfidence = None;#Confidence in acccuracy of all image text

    def __init__(self, imageFile, analyzeText = True, analyzeObjects = True, dimensions=[1920,1080]):
        self.imageFile=imageFile;
        if(analyzeObjects): self.AnalyzeObjects(dimensions)
        if(analyzeText): self.AnalyzeText()
    def AnalyzeText(self):
        #Get Text Response for Google Cloud Vision API
        image = vision.Image(content=io.open(self.imageFile, 'rb').read())
        text_detection_params = vision.TextDetectionParams(enable_text_detection_confidence_score=True)
        image_context = vision.ImageContext(text_detection_params=text_detection_params)
        response = client.text_detection(image=image, image_context=image_context)

        #Get all the text in Image:
        self.allText=response.full_text_annotation.text
        #First page's confidence:
        self.allTextConfidence= next(iter(response.full_text_annotation.pages), None).confidence

        #Get the text, confidence, enclosing rectangular box, and center for each word in the image 
        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    for word in paragraph.words:
                        dataOfWord = Google_Word();
                        dataOfWord.confidence=word.confidence;
                        dataOfWord.rectangularVertices=[[v.x,v.y] for v in word.bounding_box.vertices]

                        #Get the Center Point:
                        xCenter = sum(vertice[0] for vertice in dataOfWord.rectangularVertices)
                        yCenter = sum(vertice[1] for vertice in dataOfWord.rectangularVertices)
                        dataOfWord.centerLocation=[xCenter/4,yCenter/4];

                        #Get all Letters
                        for symbol in word.symbols: dataOfWord.wordText+=symbol.text;

                        #Add to list of Words:
                        self.words.append(dataOfWord)

    def AnalyzeObjects(self, dimensions):
        #Get Object Response for Google Cloud Vision API
        image = vision.Image(content=io.open(self.imageFile, 'rb').read())
        request = vision.AnnotateImageRequest(image=image, features=[vision.Feature(type_=vision.Feature.Type.OBJECT_LOCALIZATION)])
        response = client.annotate_image(request=request)
        for real_object in response.localized_object_annotations:
            realWorldObject = Google_Real_Object();
            realWorldObject.confidence=real_object.score
            realWorldObject.objectDescription=real_object.name  
            realWorldObject.rectangularVertices=[[int(v.x*dimensions[0]),int(v.y*dimensions[1])] for v in real_object.bounding_poly.normalized_vertices]
            
            #Get the Center Point:
            xCenter = sum(vertice[0] for vertice in realWorldObject.rectangularVertices)
            yCenter = sum(vertice[1] for vertice in realWorldObject.rectangularVertices)
            realWorldObject.centerLocation=[xCenter/4,yCenter/4];
            self.real_world_objects.append(realWorldObject)

class OpenCV_Contour_Data():
    centerLocation = None; #Center Location in Pixels -> [x,y]
    width, height, area = None, None, None; #Details of box that encloses object
    color = [];
    shape = [];
    number = None;
    insideObjects = None;

class Open_CV_Analysis():#Call this to get opencv data for objects in undistorted image
    contour_objects = [];
    contours=[];
    SIMPLE_FAST_COLOR  = 0;
    COMPLEX_FAST_COLOR = 1;
    SIMPLE_SLOW_COLOR  = 2;
    COMPLEX_SLOW_COLOR = 3;
    def __init__(self, imageBGR, colorRecogType = SIMPLE_FAST_COLOR, whiteBackground = True):
        self.imageBGR= imageBGR;
        self.colorRecogType = colorRecogType;
        self.whiteBackground = whiteBackground;
        self.thresholdBGR, self.thresholdGray = self.GetThresholdImage()
        self.GetContour()
        self.DrawContours()
        
    def GetThresholdImage(self, kSize = (5,5), sigmaX =0, threshType =  cv2.THRESH_BINARY | cv2.THRESH_OTSU):
        #Necessary Input: undistorted image in BGR Format
        #Other Optional Inputs: parameters to change thresholding
        #Outputs: thresholded image in BGR, thresholded image in gray
        
        grayImg = cv2.cvtColor(self.imageBGR, cv2.COLOR_BGR2GRAY)
        blurredImg = cv2.GaussianBlur(grayImg, kSize,sigmaX) 
        threshImageGray = cv2.threshold(blurredImg, 0, 255, threshType)[1]

        #Opencv needs black backgroun and white objects, so invert image if needed
        if(self.whiteBackground): threshImageGray = cv2.bitwise_not(threshImageGray)

        threshImageBGR = cv2.cvtColor(threshImageGray,cv2.COLOR_GRAY2BGR)
        return threshImageBGR, threshImageGray;

    def GetContour(self, cMode = cv2.RETR_TREE, cMethod = cv2.CHAIN_APPROX_SIMPLE):
        #Find Contours:
        contours,_ = cv2.findContours(image=self.thresholdGray, mode=cMode, method=cMethod)
        
        #Get pixel dimensions
        dimensions = self.imageBGR.shape
        
        contourNum =0;
        for contour in contours:
            
            #Get Width, Height, Area of each contour
            x,y,width, height = cv2.boundingRect(contour)
            area= width*height*1.0;
            contourPercentage = 100.0*(area)/(dimensions[0]*dimensions[1]*1.0)
            
            #Ignore huge or very small contours
            if(0.3<=contourPercentage<=95):
                #Create contour Object:
                self.contours.append(contour)
                contour_data = OpenCV_Contour_Data()
                self.contour_objects.append(contour_data)
                
                #Insert width, height, area, number data
                contour_data.width, contour_data.height= width, height
                contour_data.area = area
                contour_data.number=contourNum

                #Find Center of Contour
                M = cv2.moments(contour)
                if M["m00"] != 0:#Found Center, don't divide by 0
                    contour_data.centerLocation = [int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])]

                contourNum +=1;

    def DrawContours(self, contourColor=(0,255,0),centerColor = (0,0,255)):
        self.contourImage = self.imageBGR.copy()
        #Draw Contours:
        cv2.drawContours(self.contourImage, self.contours, -1, contourColor, 2)

        #Draw center for each contour on the image
        for contourObject in self.contour_objects:
            centerX = contourObject.centerLocation[0]
            centerY = contourObject.centerLocation[1]
            cv2.circle(self.contourImage, contourObject.centerLocation, 7, centerColor, -1)
            cv2.putText(self.contourImage, "Center_"+str(contourObject.number), (centerX - 20, centerY - 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, centerColor, 2)

def testText(imageFile):
    googleData = Google_Analysis(imageFile, analyzeObjects=False)
    print("All Words:")
    print(googleData.allText)
    print("Confidence:",googleData.allTextConfidence)
    print("="*100)
    for word in googleData.words:
        print("Word:", word.wordText)
        print("Confidence:",word.confidence)
        print("Vertices:",word.rectangularVertices)
        print("Centerpoint:",word.centerLocation)
        print("="*100)

def testObjects(imageFile):
    googleData=Google_Analysis(imageFile, analyzeText=False)
    img = cv2.imread(imageFile)
    for realObject in googleData.real_world_objects:
        print("Description:", realObject.objectDescription)
        print("Confidence:",realObject.confidence)
        print("Vertices:",realObject.rectangularVertices)
        print("Centerpoint:",realObject.centerLocation)
        print("="*100)
        index = 0;
        for vertice in realObject.rectangularVertices:
            index = 0 if index == len(realObject.rectangularVertices) -1 else index+1
            cv2.line(img, vertice, realObject.rectangularVertices[index], (0,255,0), 2) 
        cv2.circle(img, (int(realObject.centerLocation[0]),int(realObject.centerLocation[1])), radius=3, color=(0, 255, 0), thickness=-1)
    cv2.imshow("Objects", img)
    while True:
        k = cv2.waitKey(1)
        if k%256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break


def RealWorldCoordinates():
    #Returns real world coordinates pixel location
    pass

# testText('testImages/4.jpg');
# testObjects('testImages/48.jpg');


img_path = "testImages/35.jpg"
imgBGR = cv2.imread(img_path)
image1Data = Open_CV_Analysis(imgBGR)

cv2.imshow('Thresh', image1Data.thresholdBGR)
cv2.imshow('SRC_Image', image1Data.imageBGR)
cv2.imshow('Contour_Image', image1Data.contourImage)

for contourObject in image1Data.contour_objects:
    print("Contour:", contourObject.number)
    print(contourObject.centerLocation)
    print("width, height, area:", contourObject.width, contourObject.height, contourObject.area)
    print("-"*100)



while True:
    k = cv2.waitKey(1)
    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break


# # Read First Image
# img1 = cv2.imread('GFG.png')
  
# # Read Second Image
# img2 = cv2.imread('GFG.png')
  
  
# # concatenate image Horizontally
# Hori = np.concatenate((img1, img2), axis=1)
  
# # concatenate image Vertically
# Verti = np.concatenate((img1, img2), axis=0)
  
# cv2.imshow('HORIZONTAL', Hori)
# cv2.imshow('VERTICAL', Verti)
  
# cv2.waitKey(0)
# cv2.destroyAllWindows()