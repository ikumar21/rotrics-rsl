#Add Laser Module:
import sys
sys.path.insert(0, 'LaserModule')
import laser_module as l_m

#Import Movement Module:
sys.path.insert(0, 'MovementModule')
from pydexarm import Dexarm

#Import Image Module:
sys.path.insert(0, 'ImageModule')
import image_module as i_m

def initializeCamera():
    camera1 = i_m.Camera_Object(cameraNum=1,cameraType=i_m.BIG_CAMERA)
    return camera1

def getCentralObjectDetails(camera:i_m.Camera_Object):
    #Take Image
    imgBGR = camera.GetImageBGR(undistorted=True)
    parameters = i_m.Open_CV_Parameters()
    image_analysis = i_m.Open_CV_Analysis(imgBGR, parameters)

    sortedObjectsMiddle = sorted(image_analysis.contour_objects, key=lambda x: 
                                 ((x.centerLocation[0]-camera.dimensions[0]/2)**2+(x.centerLocation[1]-camera.dimensions[1]/2)**2),
                                   reverse=False ) 

    if(len(sortedObjectsMiddle)==0):
        return None
    else:
        return sortedObjectsMiddle[0]


def EngraveCircle(laserRobot, centerLoc):

    #File Name:
    fileLocName = "LaserModule/rotricsGcode/CircleOutline.gcode";
    
    #Set laser object center, angle, height/width, laser power:
    circle_prop = l_m.Laser_Object_Properties(fixHeight=True,centerPoint=centerLoc,specifiedLength=10,laserPower=125,angle=0)
    
    #Generate G-Code:
    width, height = l_m.GcodeObjectCreation(fileLocName,circle_prop)

    #Run the Laser
    l_m.runLaser(laserRobot)

if __name__ == "__main__":
    #Settings:
    heightOfObject = 4;#mm
    yShift = 55;#mm

    #Initialize Camera:
    camera0 = initializeCamera()

    #Find the details of the object in the middle:
    contour_middle_object:i_m.OpenCV_Contour_Data = getCentralObjectDetails(camera0)

    #Find where the robot is:

    #Determine Real World Location of center:
    realWorldLocationX, realWorldLocationY = i_m.RealWorldCoordinates(contour_middle_object.centerLocation,heightOfObject,)

    #Laser a circle of 10 mm around the center: