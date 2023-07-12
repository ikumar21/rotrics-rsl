import sys

# Add Image Module
sys.path.insert(0, 'ImageModule')
import image_module as i_m
import cv2





def initializeCamera():
    camera0 = i_m.Camera_Object(cameraNum=0,cameraType=i_m.BIG_CAMERA)
    return camera0


def getMostAccurateWord(camera:i_m.Camera_Object):
    #Take Image
    imgWord = camera.GetImageBGR()
    
    #Save Image
    cv2.imwrite("imageWord.png",imgWord)
    
    #Analyze image using Google Vision API text
    imgAnalysis = i_m.Google_Analysis("imageWord.png",analyzeText=True,analyzeObjects=False)
    
    #Return None if no words found
    accurateWord = None;
    maxConfidence = 0;
    
    #Find the word that is the most accurate:
    for word_object in imgAnalysis.words:
        word_object:i_m.Google_Word
        
        #Change the word, if Google has more confident in it:
        if(word_object.confidence>maxConfidence):
            accurateWord=word_object.wordText;
            maxConfidence = word_object.confidence;

    return accurateWord;


def testText(imageFile):
    googleData=i_m.Google_Analysis(imageFile,analyzeText=True,analyzeObjects=False)
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

# testText("ExampleCode/ImageScripts/testImages/63.jpg")



if __name__ == "__main__":
    #Initialize Camera:
    camera0 = initializeCamera()
    
    #Find Word:
    wordFound = getMostAccurateWord(camera0);
    #Print Word:
    print("Most Accurate Word:", wordFound)

    #Print all words and their details:
    testText("imageWord.png")
