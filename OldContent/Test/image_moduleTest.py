import sys
# adding folder to the system path
#sys.path.insert(0, '../Test')
sys.path.insert(0, 'C:/Users/rsl/Desktop/rotrics-rsl/Test')


import numpy as np
import os
import glob
import cv2
#from google.cloud import vision
import io
from statistics import mean
from scipy.optimize import fsolve
import math



#Initializes constants used in module
def InitializeConstants():
    global K,D, FISHEYE_K1,FISHEYE_K2,FISHEYE_K3,FISHEYE_K4,FISHEYE_FX,FISHEYE_FY,FISHEYE_CX,FISHEYE_CY;
    global MAP_1,MAP_2, CAMERA_SMALL_MATRIX, DIST_COEFF_SMALL, SIMPLE_FAST_COLOR, COMPLEX_FAST_COLOR, SIMPLE_SLOW_COLOR  
    global COMPLEX_SLOW_COLOR, Z_DISTANCE_TABLE_CAMERA, BIG_CAMERA, SMALL_CAMERA 
    
    #1920*1080 camera:
    #Import Undistortion constants

    K = np.load("C:/Users/rsl/Desktop/rotrics-rsl/Test/cImages/K.npy", mmap_mode=None, allow_pickle=False, fix_imports=True, encoding='ASCII')
    D = np.load("C:/Users/rsl/Desktop/rotrics-rsl/Test/cImages/D.npy", mmap_mode=None, allow_pickle=False, fix_imports=True, encoding='ASCII')


    FISHEYE_K1 = D[0][0];
    FISHEYE_K2 = D[1][0];
    FISHEYE_K3 = D[2][0];
    FISHEYE_K4 = D[3][0];
    FISHEYE_FX = K[0][0]
    FISHEYE_FY = K[1][1]
    FISHEYE_CX = K[0][2]
    FISHEYE_CY = K[1][2]

    MAP_1, MAP_2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, (1920,1080), cv2.CV_16SC2)


    # 640*480 Small Camera:
    CAMERA_SMALL_MATRIX = np.array([
                            [ 7.9641507015667764e+02, 0., 3.1577913194699374e+02], 
                            [0.,7.9661307355876215e+02, 2.1453452136833957e+02], 
                            [0., 0., 1. ]
                            ])

    DIST_COEFF_SMALL = np.array([
                        [ -1.1949335317713690e+00,
                        1.8078010700662486e+00,
                        4.9410258870084744e-03, 
                        2.8036176641915598e-03,
                        -2.0575845684235938e+00]
                        ])  


    #Constants Used:
    SIMPLE_FAST_COLOR  = 0;
    COMPLEX_FAST_COLOR = 1;
    SIMPLE_SLOW_COLOR  = 2;
    COMPLEX_SLOW_COLOR = 3;
    BIG_CAMERA = 0;#1920 by 1080 pixels
    SMALL_CAMERA = 1;#640 by 480 pixels

    Z_DISTANCE_TABLE_CAMERA = 78;
InitializeConstants();

#Equations used to calculate real world coordinates based on fisheye distortion:
def FisheyeEquations(x, u_adjusted,v_adjusted ):
     k1,k2,k3,k4 = FISHEYE_K1, FISHEYE_K2, FISHEYE_K3, FISHEYE_K4 
     return [x[0] -np.arctan(x[2]),
             x[1]-x[0]*(1+k1*x[0]**2+k2*x[0]**4+k3*x[0]**6+k4*x[0]**8),
             x[2]**2-x[3]**2-x[4]**2,
             u_adjusted-x[1]*x[3]/x[2],
             v_adjusted-x[1]*x[4]/x[2]]

def RealWorldCoordinates(centerLocation, heightObject, robotPosition):
    #Returns real world coordinates from pixel location
    #Input: center location in pixels: [x,y]; height of object (mm), position of rotrics arm: [x,y,z]
    #Output: returns real world coordinates in mm [x,y]

    #Add check to see if within image dimensions
    centerX, centerY = centerLocation[0], centerLocation[1]
    u_adjusted = (centerX*1.0-FISHEYE_CX)/FISHEYE_FX
    v_adjusted = (centerY*1.0-FISHEYE_CY)/FISHEYE_FY
    sol = fsolve(FisheyeEquations, [1, 1,1,1,1], args=(u_adjusted, v_adjusted))
    print(np.isclose(FisheyeEquations(sol, u_adjusted, v_adjusted), [0.0, 0.0,0.0,0.0,0.0]))
    
    
    #z Distance from object to camera:
    z_c = Z_DISTANCE_TABLE_CAMERA-heightObject+robotPosition[2]

    x_c = sol[3]*z_c;
    y_c = sol[4]*z_c;

    x_e = x_c*1.0;
    y_e = -y_c*1.0-61.0;#y axis is flipped and translated upwards 
    z_e = 0.0;#dummy z

    P_e = np.array([[x_e],[y_e], [z_e], [1]])
    theta = np.arcsin(robotPosition[0]/math.sqrt(robotPosition[0]**2+robotPosition[1]**2))        
    T_r_e=np.array([[np.cos(theta), np.sin(theta), 0.0,robotPosition[0]*1.0], 
        [-np.sin(theta), np.cos(theta), 0.0,robotPosition[1]*1.0], 
        [0.0, 0.0, 1.0, robotPosition[2]*1.0],
        [0.0, 0.0, 0.0, 1.0]])
    
    #print(T_r_e)
    #print(P_e)
    P_r = np.matmul(T_r_e,P_e);#Multiply homogeneous transform by position in end-effector frame to get position in robot/global frame
    print(P_r[0],P_r[1])
    #print("="*80)
    return P_r[0][0], P_r[1][0]

def CorrectHSV(hsvArray):
    #Returns tuple : (H,S,V) in correct format: 0-360degrees, 0-100%, 0-100%
    return round(hsvArray[0]*2.0), round(100.0*hsvArray[1]/255.0,1), round(100.0*hsvArray[2]/255.0,1)
def ColorRecog(hsv):
    #Input hsv value -> [H,S,V]
    #output: color in string all capitilized
    hVal = hsv[0]
    sVal = hsv[1]
    vVal = hsv[2]
    if(sVal<10):#Could be white, Gray or white
        if(vVal >=90):
            return "WHITE"
        elif(vVal<=6):
            return "BLACK"
        else:
            return "GRAY"
    if(0<=hVal<=30 or 330<=hVal<=360):
        return "RED"
    elif(30<=hVal<=50):
        return "ORANGE"
    elif(50<=hVal<=90):
        return "YELLOW"
    elif(90<=hVal<=150):
        return "GREEN"
    elif(150<=hVal<=210):
        return "CYAN"
    elif(210<=hVal<=270):
        return "BLUE"
    elif(270<=hVal<=330):
        return "MAGENTA"
    else:
        return "ERROR"
def MeanHSV(yPixelLocationsArr,xPixelLocationsArr, imgHSV):
        #Gives mean HSV for the pixel locations and their color name
        #imgHSV[yPixelLocation][xPixelLocation]= [H,S,V]
        #Outputs corrected color in HSV and and color Name
        
        #IF input is empty ->returns None
        if(len(yPixelLocationsArr)==0):
            return None, None;

        avgH = mean([float(imgHSV[yPixelLocationsArr[indexPixel]][xPixelLocationsArr[indexPixel]][0]) for indexPixel in range(len(yPixelLocationsArr))])
        avgS = mean([float(imgHSV[yPixelLocationsArr[indexPixel]][xPixelLocationsArr[indexPixel]][1]) for indexPixel in range(len(yPixelLocationsArr))])
        avgV = mean([float(imgHSV[yPixelLocationsArr[indexPixel]][xPixelLocationsArr[indexPixel]][2]) for indexPixel in range(len(yPixelLocationsArr))])
        colorHSV = [avgH,avgS,avgV];
        return colorHSV, ColorRecog(CorrectHSV(colorHSV))

def HSV2_BGR(colorHSV):
    colorImg = np.uint8([[colorHSV]]) 
    colorBGR = cv2.cvtColor(colorImg, cv2.COLOR_HSV2BGR)
    return colorBGR

def CropImg(vertices, img):
    #Get min x, y and max x,y of vertices for cropping
    minY = min([elem[0][1] for elem in vertices])
    maxY = max([elem[0][1] for elem in vertices])
    maxX = max([elem[0][0] for elem in vertices])
    minX = min([elem[0][0] for elem in vertices])

    imgCrop = img[minY:maxY, minX:maxX].copy()
    return imgCrop;


def CropImgInner(contour, vertices, imgBGR, backgroundColorBGR=(128,151,166)):
    
    #Get min x, y and max x,y of vertices for cropping
    minY = min([elem[0][1] for elem in vertices])
    maxY = max([elem[0][1] for elem in vertices])
    maxX = max([elem[0][0] for elem in vertices])
    minX = min([elem[0][0] for elem in vertices])

    #Create a gray image mask and fill in the contour with white, rest is black
    mask = np.zeros_like(cv2.cvtColor(imgBGR, cv2.COLOR_BGR2GRAY))
    cv2.drawContours(mask, [contour], 0, color=255, thickness=-1)

    #Crop mask Image:
    mask = mask[minY:maxY, minX:maxX];
    
    #Crop actual image in BGR format:
    imgCropBGR = imgBGR[minY:maxY, minX:maxX].copy()

    #Find where pixels where contour is not add (Find background):
    pixels = np.where(mask != 255)
    yPixelLocationsArr,xPixelLocationsArr = pixels[0],pixels[1]

    #Replace background with certain color:
    imgCropBGR = imgBGR[minY:maxY, minX:maxX].copy()
    for indexPixel in range(len(yPixelLocationsArr)):
        imgCropBGR[yPixelLocationsArr[indexPixel]][xPixelLocationsArr[indexPixel]]=backgroundColorBGR;
    
    #show image until user presses space:
    cv2.imshow("New Image", imgCropBGR);
    while True:
        k = cv2.waitKey(1)
        if k%256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break


    return imgCropBGR



class Camera_Object():#Initialize Camera-> Get undistorted/distorted Images in BGR Format
    numberCameras = 0 #Number of connected cameras
    camera = None;
    dimensions = None;
    def __init__(self,cameraNum=0,cameraType = BIG_CAMERA):
        self.cameraType = cameraType;#Big or small camera
        self.Scan()#Finds connnected cameras
        self.InitializeCamera(cameraNum);
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
        elif(self.numberCameras<cameraNum+1):
            raise NameError("Wrong Camera Index")
        else:#Correct Camera
            self.camera = cv2.VideoCapture(cameraNum)#Start Capture
            if(self.cameraType==BIG_CAMERA):
                self.dimensions = (1920,1080)
            else:
                self.dimensions = (640,480)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.dimensions[0])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.dimensions[1])
    def Undistort(self,img):#Undistort Image
        if(self.cameraType==BIG_CAMERA):
            undistortedImg = cv2.remap(img, MAP_1, MAP_2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        else:
            undistortedImg = cv2.undistort(img, CAMERA_SMALL_MATRIX, DIST_COEFF_SMALL, None)
        return undistortedImg; 
    def GetImageBGR(self, undistorted=True):#Get undistorted/distorted image in BGR format
        ret, distortedImage = self.camera.read()
        if(undistorted):
            return self.Undistort(distortedImage)
        else:
            return distortedImage;
class Google_Data():
    def __init__(self):
        self.centerLocation = None; #Center Location in Pixels -> [x,y]
        self.confidence = None;#Confidence in that word or object identification
        self.rectangularVertices = [];#Vertices of Rectangular box that encloses object/text ->[[x1,y1],..,[x4,y4]]
class Google_Word(Google_Data):
    #Includes Google_Data properties -> Center Location, rectangular vertices, confidence
    def __init__(self):
        self.wordText = "";#Word that Google is reading
class Google_Real_Object(Google_Data):
    #Includes Google_Data properties -> Center Location, rectangular vertices, confidence

    def __init__(self):
        self.objectDescription = None;#Description of what google Cloud thinks object is    
        self.color = None; 



class OpenCV_Contour_Data():
    def __init__(self):
        self.contourOpenCV = None; #open cv contour
        self.centerLocation = None; #Center Location in Pixels -> [x,y]
        self.width, self.height, self.area = None, None, None; #Details of box that encloses object
        self.vertices = [];
        self.color = [];
        self.shape = None;
        self.number = None;
        
        
        self.colorName = None;
        self.insideObjects = [];#Open_CV_Analysis Objects from running a crop of contour image
        self.centerRealWorld = None;#This will not change unless you change it yourself
        self.cropImgGray = None
        self.pixelsInCropImg = None;
        self.cropImgBGR = None;


class Open_CV_Parameters():
    def __init__(self):
        self.colorRecogType = SIMPLE_FAST_COLOR;
        self.whiteBackground = True;

        #Thresh Image Parameters:
        self.kSize,self.sigmaX, self.threshType  = (5,5), 0, cv2.THRESH_BINARY | cv2.THRESH_OTSU

        #Finding Contour Parameters:
        self.cMode, self.cMethod = cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE

        #Drawing Contour Parameters:
        self.contourColor,self.centerColor = (0,255,0), (0,0,255) #default green, red

        #What Functions to Run:
        self.runThreshImg = True;
        self.runGetContour = True;
        self.runDrawContour = True;
        self.runFindColorContour = True;


default_parameters = Open_CV_Parameters()

class Open_CV_Analysis():#Call this to get opencv data for contours in undistorted image
    def __init__(self, imageBGR, analysis_parameters: Open_CV_Parameters =  default_parameters):

        #Initialize contour object lists:
        self.contour_objects= []

        #Store images in different formats &store parameters for analysis:
        self.imageBGR= imageBGR;
        self.imageHSV = cv2.cvtColor(self.imageBGR, cv2.COLOR_BGR2HSV)
        self.colorRecogType = analysis_parameters.colorRecogType;
        self.whiteBackground = analysis_parameters.whiteBackground;
        self.param = analysis_parameters;

        #Threshold Image:
        if (self.param.runThreshImg): self.thresholdBGR, self.thresholdGray = self.GetThresholdImage()

        #Get appropiate Contours and their information
        if (self.param.runGetContour): self.GetContour()

        #Create an image with contours and their centers
        if (self.param.runDrawContour): self.DrawContours()

        #Find color for all contours:
        if (self.param.runFindColorContour): self.ColorContour()

    def GetThresholdImage(self):
        #Necessary Input: undistorted image in BGR Format
        #Other Optional Inputs: parameters to change thresholding
        #Outputs: thresholded image in BGR, thresholded image in gray
        
        #Parameters for Threshing:
        kSize, sigmaX, threshType = self.param.kSize, self.param.sigmaX, self.param.threshType
        
        #Threshold Images:
        grayImg = cv2.cvtColor(self.imageBGR, cv2.COLOR_BGR2GRAY)
        blurredImg = cv2.GaussianBlur(grayImg, kSize,sigmaX) 
        threshImageGray = cv2.threshold(blurredImg, 0, 255, threshType)[1]

        #Opencv needs black background and white objects, so invert image if needed
        if(self.whiteBackground): threshImageGray = cv2.bitwise_not(threshImageGray)

        threshImageBGR = cv2.cvtColor(threshImageGray,cv2.COLOR_GRAY2BGR)
        return threshImageBGR, threshImageGray;

    def GetContour(self):
        #Stores all relevant contours and their properties in contour_objects list

        #Parameters for Threshing:
        cMode, cMethod = self.param.cMode, self.param.cMethod

        #Find Contours:
        contours,_ = cv2.findContours(image=self.thresholdGray, mode=cMode, method=cMethod)
        
        #Get pixel dimensions
        dimensions = self.imageBGR.shape
        
        contourNum =0;
        for contourOpenCV in contours:
            
            #Get Width, Height, Area of each contour
            x,y,width, height = cv2.boundingRect(contourOpenCV)
            area= width*height*1.0;
            contourPercentage = 100.0*(area)/(dimensions[0]*dimensions[1]*1.0)
            
            #Ignore huge or very small contours
            if(0.3<=contourPercentage<=95):
                #Create contour Object:
                contour_data = OpenCV_Contour_Data()
                self.contour_objects.append(contour_data)
                contour_data.contourOpenCV= contourOpenCV

                #Insert width, height, area, number data
                contour_data.width, contour_data.height= width, height
                contour_data.area = area
                contour_data.number=contourNum

                #Find Center of Contour
                M = cv2.moments(contourOpenCV)
                if M["m00"] != 0:#Found Center, don't divide by 0
                    contour_data.centerLocation = [int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])]

                #Find Shape of Contour
                self.ShapeContour(contour_data)

                contourNum +=1;

    def DrawContours(self):

        #Parameters for Threshing:
        contourColor, centerColor = self.param.contourColor, self.param.centerColor

        #Creates an image with all contours and their centers drawn
        self.contourImageBGR = self.imageBGR.copy()

        #Draw Contours:
        allContours = [contourObject.contourOpenCV for contourObject in self.contour_objects]
        cv2.drawContours(self.contourImageBGR,allContours , -1, contourColor, 2)

        #Draw center for each contour on the image
        for contourObject in self.contour_objects:
            centerX = contourObject.centerLocation[0]
            centerY = contourObject.centerLocation[1]
            cv2.circle(self.contourImageBGR, contourObject.centerLocation, 7, centerColor, -1)
            cv2.putText(self.contourImageBGR, "Center_"+str(contourObject.number), (centerX - 20, centerY - 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, centerColor, 2)

    def ShapeContour(self, contour_data):
        #Input: single contour object 
        #Fill shape property in contour object
 
        def shapeFromVertices(vertices, contour_data):
            numVertices = len(vertices);
            if(numVertices==3):
                contour_data.shape = "TRIANGLE"
            elif(numVertices==4):
                contour_data.shape = "RECTANGLE"
            else:
                contour_data.shape =str(numVertices)+" EDGES"

        perimeter = cv2.arcLength(contour_data.contourOpenCV, True)
        vertices = cv2.approxPolyDP(contour_data.contourOpenCV, 0.04 * perimeter, True);
        contour_data.vertices = vertices;
        shapeFromVertices(vertices, contour_data)

    def PixelsInContour(self):
        #Input: All contour objects -> Max 255 objects
        #Adds Pixel Locations to object

        # Create a mask image that contains the contour filled in
        cimg = np.zeros_like(self.imageBGR)
        #cimg = np.full((1080, 1920, 3), 0, dtype=np.int32)
        
        #Fill color for each contour starting with 255, 254, 253 ... 
        colorContour = 255;
        for contourObject in self.contour_objects:
            contourObject:OpenCV_Contour_Data
            #Fill in the contour with specific color
            cv2.drawContours(cimg, [contourObject.contourOpenCV],0, color=colorContour, thickness=-1)
            
            #Crop Image to avoid looking at entire image:
            cropImgGray = CropImg(contourObject.vertices, cimg)
            contourObject.cropImgHSV= CropImg(contourObject.vertices, self.imageHSV)

            # Look at the HSV crop image ad find where contours are:
            contourObject.pixelsInCropImg = np.where(cropImgGray == colorContour)

            #Change color:
            colorContour-=1
       
       
        # allContours = [contourObject.contourOpenCV for contourObject in self.contour_objects]
        # cv2.drawContours(cimg, allContours, contour_data.number, color=255, thickness=-1)

        # #cv2.imshow("object{}".format(i+1),cimg)

        # cropImgGray = CropImg(contour_data.vertices, cimg)
        # contour_data.cropImgHSV= CropImg(contour_data.vertices, self.imageHSV)
        # # Access the image pixels and create a 1D numpy array then add to list
        # contour_data.pixelsInCropImg = np.where(cropImgGray == 255)

        #cv2.drawContours(emptyImg, contours, i, color=0, thickness=-1)#reset

    def ColorContour(self):
        #Finds color for each contour depending on the color recognition algo 
        if(self.colorRecogType==SIMPLE_SLOW_COLOR):#Get mean HSV from all pixels in contour
            self.PixelsInContour()
            for contourObject in self.contour_objects: 
                contourObject.color, contourObject.colorName= MeanHSV(contourObject.pixelsInCropImg[0],contourObject.pixelsInCropImg[1], contourObject.cropImgHSV)
        else:
            return 0;

    def FindCropImgBGR(self):
        for contour_obj in self.contour_objects:
            contour_obj.cropImgBGR = CropImg(contour_obj.vertices,self.imageBGR);






# testText('testImages/4.jpg');
# testObjects('testImages/48.jpg');


# img_path = "testImages/48.jpg"
# imgBGR = cv2.imread(img_path)
# image1Data = Open_CV_Analysis(imgBGR,colorRecogType=SIMPLE_SLOW_COLOR)

# cv2.imshow('Thresh', image1Data.thresholdBGR)
# cv2.imshow('SRC_Image', image1Data.imageBGR)
# cv2.imshow('Contour_Image', image1Data.contourImageBGR)

# for contourObject in image1Data.contour_objects:
#     print("Contour", contourObject.number)
#     print(contourObject.centerLocation)
#     print("width, height, area:", contourObject.width, contourObject.height, contourObject.area)
#     print("Shape:", contourObject.shape)
#     print("Corrected HSV:", CorrectHSV(contourObject.color))
#     print("Color:", contourObject.colorName)
#     print("-"*100)
#     x,y = RealWorldCoordinates(contourObject.centerLocation, 30, [0,300,167])
#     print(x,y)


# while True:
#     k = cv2.waitKey(1)
#     if k%256 == 27:
#         # ESC pressed
#         print("Escape hit, closing...")
#         break


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