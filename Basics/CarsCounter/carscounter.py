import picamera
camera = picamera.PiCamera()

import cv2
import matplotlib.pyplot as plt
import cvlib as cv
from cvlib.object_detection import draw_bbox

def takePicture():
    camera.capture('snapshot.jpg')
    print("Just took the photo")
    
def detectAndCount(showOutputImage = False):
    print("Detecting cars now")
    im = cv2.imread('./../RoadImages/cars_2.jpg')
    bbox, label, conf = cv.detect_common_objects(im)
    print("Done detecting. Drawing contours now.")
    if showOutputImage == True:
        output_image = draw_bbox(im, bbox, label, conf)
        plt.imshow(output_image)
        plt.show()
    numberOfCars = label.count('car')
    print('Number of cars in the image is ', numberOfCars)
    

choice = 1

while choice == 1:
    takePicture()
    detectAndCount(True)
    choice = int(input("Enter choice 1 to continue else anything else : "))