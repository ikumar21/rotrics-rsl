import sys

# Add Image Module
sys.path.insert(0, 'ImageModule')
import image_module as i_m
import cv2



def initializeCamera():
    camera0 = i_m.Camera_Object(cameraNum=0,cameraType=i_m.BIG_CAMERA)
    return camera0



def getCentralObjectDetails(camera:i_m.Camera_Object):
    #Take Image
    imgBGR = camera.GetImageBGR(undistorted=True)
    parameters = i_m.Open_CV_Parameters()
    image_analysis = i_m.Open_CV_Analysis(imgBGR, parameters)


    # for contour_middle_object in image_analysis.contour_objects:
    #     contour_middle_object:i_m.OpenCV_Contour_Data
    #     print("Color Name: ", contour_middle_object.colorName)
    #     print("Shape: ", contour_middle_object.shape)
    #     print("Color HSV value: ", contour_middle_object.color)

    # print("=======")

    sortedObjectsMiddle = sorted(image_analysis.contour_objects, key=lambda x: 
                                 ((x.centerLocation[0]-camera.dimensions[0]/2)**2+(x.centerLocation[1]-camera.dimensions[1]/2)**2),
                                   reverse=False ) 


    


    # for contour_middle_object in sortedObjectsMiddle:
    #     contour_middle_object:i_m.OpenCV_Contour_Data
    #     print("Color Name: ", contour_middle_object.colorName)
    #     print("Shape: ", contour_middle_object.shape)
    #     print("Color HSV value: ", contour_middle_object.color)

    # print("=======")



    if(len(sortedObjectsMiddle)==0):
        return None
    else:
        return sortedObjectsMiddle[0]



if __name__ == "__main__":
    #Initialize Camera:
    camera0 = initializeCamera()

    #Find the details of the object in the middle:
    contour_middle_object = getCentralObjectDetails(camera0)

    #Print details:
    if(contour_middle_object==None):
        print("Error: No objects found")
    else:
        contour_middle_object:i_m.OpenCV_Contour_Data
        print("Color Name: ", contour_middle_object.colorName)
        print("Shape: ", contour_middle_object.shape)
        print("Color HSV value: ", contour_middle_object.color)
