import sys

# Add Image Module
sys.path.insert(0, 'ImageModule')
import image_module as i_m

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

testText("ExampleCode/ImageScripts/testImages/63.jpg")