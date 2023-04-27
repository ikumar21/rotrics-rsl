from typing import Sequence
from google.cloud import vision
import io
import glob


#Terminal (Download Library): pip3 install --upgrade google-cloud-vision

#Macbook: Enter in Terminal
#export PROJECT_ID=rotricstest
#export GOOGLE_CLOUD_PROJECT=rotricstest
#export GOOGLE_CLOUD_QUOTA_PROJECT=rotricstest
#export GOOGLE_APPLICATION_CREDENTIALS="application_default_credentials.json"

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
    for annotation in response.text_annotations:
        if(firstEntry):
            allWords+=annotation.description;
            firstEntry=False;
        else:
            wordList.append(annotation.description)

    return allWords, wordList;



images  = glob.glob('testImages/3.jpg')
images.sort()
for image in images:
    
    sentence, words =getTextImage(image)
    print(sentence)
    print("="*80)
    for word in words:
        print(word)
