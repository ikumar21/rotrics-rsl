from pydexarm import Dexarm
import numpy as np
import math
from scipy.stats import gmean
from scipy.optimize import minimize
from statistics import mean
import sys
import cv2
import image_moduleTest as img_m

# adding folder to the system path
sys.path.insert(0, '../Test')




# setup arm for testing
dexarm = Dexarm(port="COM6")

#xpos = 0
#ypos = 300
#zpos = 75
#dexarm.go_home()

dexarm.move_to(None,None,100)#150



def imageFn(showImage=False):
    # take photo
    cam = cv2.VideoCapture(0)
    ret,img = cam.read()
    cam.release()

    # get photo dimension(s) <-- change if addit. camera
    if (img.shape[0] == 480):
        dim = img.shape

    # 640*480 Small Camera:
    CAMERA_SMALL_MATRIX = np.array([[7.9641507015667764e+02,0.,3.1577913194699374e+02],[0.,7.9661307355876215e+02, 2.1453452136833957e+02],[0.,0.,1.]])
    DIST_COEFF_SMALL = np.array([[-1.1949335317713690e+00,1.8078010700662486e+00,4.9410258870084744e-03,2.8036176641915598e-03,-2.0575845684235938e+00]])

    #mvar = 0.0015885416
    #bvar = 0.1356770833

    # undistort/HSV image
    img = cv2.undistort(img, CAMERA_SMALL_MATRIX, DIST_COEFF_SMALL, None)
    imgHSV = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

    # gray, blur, thresh
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(5,5),0) 
    thresh = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY_INV,51,7)#7,7

    # find contours
    contours,hierarchy = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    # return variables
    list = []

    # display image
    disp = img

    # iterates for each contour
    for i in range(1,len(contours)):
        # contour points, area
        approx = cv2.approxPolyDP(contours[i], 0.01 * cv2.arcLength(contours[i],True),True)
        Ai = cv2.contourArea(approx)
        
        # ignore large/small contours
        contourPercentage = 100*Ai/(dim[0]*dim[1])
        if contourPercentage >= 95 or contourPercentage <= 0.3:
            continue

        # new return variable
        listi = [None] * 3

        # SHAPE ANALYSIS
        # calculate area of bounding rectangle/circle/triangle
        Rcenter,Rdim,Rang = cv2.minAreaRect(approx)
        Ccenter,Crad = cv2.minEnclosingCircle(approx)

        TA,Tpnts = cv2.minEnclosingTriangle(approx)
        RA = Rdim[0]*Rdim[1]
        CA = np.pi*Crad**2

        # % error between contour area and bounding shapes
        error = [abs(Ai-RA)/Ai*100,abs(Ai-TA)/Ai*100,abs(Ai-CA)/Ai*100]

        # compare % error to identify shape
        if error[0] < error[1] and error[0] < error[2]:
            # assign return values
            listi[0] = 'Square'
            listi[1] = round(Rang,2)
            
            # box vertices/center
            rect = cv2.boxPoints(cv2.minAreaRect(approx))
            rect = np.int0(rect)
            center = np.int0(Rcenter)

            # draw centerpoint and contour
            cv2.circle(disp,center,0,(0,0,255),2)
            cv2.drawContours(disp,[rect],0,(0,0,255),2)
        elif error[1] < error[0] and error[1] < error[2]:
            #assign return values
            listi[0] = 'Triangle'
            listi[1] = round(Rang,2)

            # center
            center = np.int0([np.sum(Tpnts[:,:,0])/3,np.sum(Tpnts[:,:,1])/3])

            # draw centerpoint and contour
            cv2.circle(disp,center,0,(0,0,255),2)
            cv2.drawContours(disp,[np.int0(Tpnts[:,0,:])],0,(0,0,255),2)
        else:
            # assign return values
            listi[0] = 'Circle'
            listi[1] = 0
            
            # center
            center = np.int0(Ccenter)

            # draw centerpoint and contour
            cv2.circle(disp,center,0,(0,0,255),2)
            cv2.circle(disp,center,np.int0(Crad),(0,0,255),2)

        # COLOR ANALYSIS
        # select sample of HSV values
        color = []
        cnt = 0
        for j in range(2,5):
            for q in range(0,33):
                # vary along different radii from center
                stp = 2*np.pi/35
                x = int(Crad/j * np.cos(q*stp) + Ccenter[1])
                y = int(Crad/j * np.sin(q*stp) + Ccenter[0])

                # check if pixel coordinates within image
                if x <= 0 or x >= dim[0]:
                    continue
                if y <= 0 or y >= dim[1]:
                    continue

                color.append(np.int0(imgHSV[x,y]))
                cnt = cnt + 1
        color = np.array(color)

        # exclude outlier data (2 std devs)
        mnHSV = np.zeros(3)
        for j in range(0,3):
            mn = np.mean(color[:,j])
            sd = np.std(color[:,j])
            
            color = np.delete(color, np.where(color[:,j] > mn+2*sd),axis=0)
            color = np.delete(color, np.where(color[:,j] < mn-2*sd),axis=0)
            
            mnHSV[j] = round(np.mean(color[:,j]),2)

        # return value <--- CHANGE LATER TO IF STATEMENTS W/ RANGES
        listi[2] = mnHSV

        '''
        ratio = mvar*zpos + bvar
        xypos = [ratio*(center[0]-dim[1]/2)-xpos, ypos-ratio*(center[1]-dim[0]/2)-50]
        '''

        # append contour values
        list.append(listi)

    #show image until user presses ESC:
    if showImage:
        while True:
            cv2.imshow("Display",disp)
            k = cv2.waitKey(1)
            if k%256 == 27:
                break
    
    return list







list = imageFn(True)
for i in range(0,len(list)):
    print(list[i])





#dexarm.move_to(xypos[0],xypos[1],30)
#print(dexarm.get_current_position())





'''
cam = cv2.VideoCapture(0)
cv2.namedWindow("test")
img_counter = 0
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
        img_name = "opencv_frame_{}.png".format(img_counter)
        cv2.imwrite(img_name, frame)
        print("{} written!".format(img_name))
        img_counter += 1
cam.release()
cv2.destroyAllWindows()
'''


'''
import pathlib
desktop = pathlib.Path('C:/Users/rsl/Desktop/rotrics-rsl/Test/cImages')
for item in desktop.iterdir():
    print(f"{item} - {'dir' if item.is_dir() else 'file'}")
'''
'''
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

#print(D[0][0])
#print(D)
'''