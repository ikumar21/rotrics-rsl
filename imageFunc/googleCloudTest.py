from typing import Sequence
from google.cloud import vision
import io
import glob
import cv2

#Terminal (Download Library): pip3 install --upgrade google-cloud-vision

#Macbook: Enter in Terminal
#export PROJECT_ID=rotricstest
#export GOOGLE_CLOUD_PROJECT=rotricstest
#export GOOGLE_CLOUD_QUOTA_PROJECT=rotricstest
#export GOOGLE_APPLICATION_CREDENTIALS=application_default_credentials.json

#Windows Terminal: Everything above(replace export with set)
#also change last Command: set GOOGLE_APPLICATION_CREDENTIALS=C:\Users\rsl\Desktop\rotrics-rsl\imageFunc\application_default_credentials.json

#Use demo to Test: https://cloud.google.com/vision#section-2

def analyze_image_from_uri(imgName, feature_types):
    client = vision.ImageAnnotatorClient()
    content = io.open(imgName, 'rb').read()
    image = vision.Image(content=content)
    features = [vision.Feature(type_=feature_type) for feature_type in feature_types]
    request = vision.AnnotateImageRequest(image=image, features=features)
    response = client.annotate_image(request=request)
    return response


def print_labels(response: vision.AnnotateImageResponse):
    print("=" * 80)
    for label in response.label_annotations:
        print(
            f"{label.score:4.0%}",
            f"{label.description:5}",
            sep=" | ",
        )
def print_text(response: vision.AnnotateImageResponse):
    print("=" * 80)
    for annotation in response.text_annotations:
        vertices = [f"({v.x},{v.y})" for v in annotation.bounding_poly.vertices]
        print(
            f"{repr(annotation.description):42}",
            ",".join(vertices),
            sep=" | ",
        )
def print_objects(response: vision.AnnotateImageResponse):
    print("=" * 80)
    for obj in response.localized_object_annotations:
        nvertices = obj.bounding_poly.normalized_vertices
        print(
            f"{obj.score:4.0%}",
            f"{obj.name:15}",
            f"{obj.mid:10}",
            ",".join(f"({v.x:.3f},{v.y:.3f})" for v in nvertices),
            sep=" | ",
        )


features = [vision.Feature.Type.TEXT_DETECTION]



def getTextImage(image):
    features = [vision.Feature.Type.TEXT_DETECTION]
    response = analyze_image_from_uri(image,features)

    firstEntry = True;
    allWords ="";
    wordList = []
    allVertices = [];
    centerPoints = []
    for annotation in response.text_annotations:
        if(firstEntry):
            allWords+=annotation.description;
            firstEntry=False;
        else:
            wordList.append(annotation.description)
            allVertices.append([(v.x,v.y) for v in annotation.bounding_poly.vertices])

    for verticesText in allVertices:
        xCenter = verticesText[0][0]+verticesText[1][0]+verticesText[2][0]+verticesText[3][0]
        yCenter = verticesText[0][1]+verticesText[1][1]+verticesText[2][1]+verticesText[3][1]
        centerPoints.append([xCenter/4,yCenter/4])
            

    

    return allWords, wordList,allVertices, centerPoints;



images  = glob.glob('testImages/40.jpg')
images.sort()
for image in images:
    
    sentence, words, allVertices, centerPoints =getTextImage(image)
    print(sentence)
    print("="*80)
    for word in words:
        print(word)

    img = cv2.imread(image)
    for verticesText in allVertices:
        print(verticesText)
        index = 0;
        for vertice in verticesText:
            index = 0 if index == len(verticesText) -1 else index+1
            cv2.line(img, vertice, verticesText[index], (0,255,0), 10) 
            print(vertice)
        print("="*80)
    for centerPoint in centerPoints:
        cv2.circle(img, (int(centerPoint[0]),int(centerPoint[1])), radius=5, color=(0, 255, 0), thickness=-1)
    cv2.imshow("text location", img)
    while True:
        k = cv2.waitKey(1)
        if k%256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break

