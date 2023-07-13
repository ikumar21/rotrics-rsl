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
    circle_prop = l_m.Laser_Object_Properties(fixHeight=True,centerPoint=centerLoc,specifiedLength=5,laserPower=125,angle=0)
    
    #Generate G-Code:
    width, height = l_m.GcodeObjectCreation(fileLocName,circle_prop)

    #Run the Laser
    l_m.runLaser(laserRobot)

def GetRobotPosition(robotDex:Dexarm):
    x,y,z,e,_,_,_ =robotDex.get_current_position()
    return [x,y,z];


def FindLocation(robotDexarm:Dexarm,startingCoordinates):

    coordinatesMove = startingCoordinates
    incrementX = 0;
    while True:

        #Move to better view
        robotDexarm.move_to(*coordinatesMove)

        #Find the details of the object in the middle:
        contour_middle_object:i_m.OpenCV_Contour_Data = getCentralObjectDetails(camera0)

        #Find where the robot is:
        robotPos = GetRobotPosition(robotDexarm);

        #Determine Real World Location of center:
        realWorldLocationX, realWorldLocationY, solutionClose = i_m.RealWorldCoordinates(contour_middle_object.centerLocation,heightOfObject,robotPos,yShift)
        
        #If not accurate; move to another location->Try again
        if False in solutionClose:
            if(incrementX>5):
                coordinatesMove=(coordinatesMove[0]-1,coordinatesMove[1]-1,coordinatesMove[2])
            else:
                incrementX+=1;
                coordinatesMove=(coordinatesMove[0]+1,coordinatesMove[1],coordinatesMove[2])
            print("Not Found")
        else: 
            print("Found")
            break;
    return round(realWorldLocationX,2),round(realWorldLocationY,2)


if __name__ == "__main__":
    #Settings:
    heightOfObject = 23;#mm
    yShift = 48;#mm

    #Initialize Camera:
    camera0 = initializeCamera()

    #Establish connection with Laser Arm:  
    laserDexarm = Dexarm(port="COM4");
    
    #Initialize Arm:
    laserDexarm.go_home();

    # #Initialize Arduino:
    # l_m.initializeArduino()

    # #Open Laser Door:
    # l_m.LaserDoorOpen()


    #Get Location of object:
    locX, locY = FindLocation(laserDexarm, (5,366,71))

    print("Pos Found", locX,locY)

    #Get Closer to Object and find more accurate Position:
    if (locX<-67):
        locX=-67;
    else:
        locX =min(locX,45);
    locX, locY = FindLocation(laserDexarm, (locX,min(395,locY+40),25))
    print(laserDexarm.get_current_position())
    print("Pos Found", locX,locY)

    # #Close Laser Door:
    # l_m.LaserDoorClose()

    # #Laser a circle of 10 mm around the center:
    # EngraveCircle(laserDexarm,[locX,locY])

