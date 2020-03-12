from threading import Thread


import time
import RPi.GPIO as GPIO

MIN_GREEN_LIGHT_TIME = 3
MAX_GREEN_LIGHT_TIME = 12
NUMBER_OF_ROADS = 3
NUMBER_OF_LANES = 3

GREENS = [17, 27, 22]
REDS = [16, 20, 21]

"""import picamera
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
    numberOfPersons = label.count('person')
    print('Number of cars in the image is ', numberOfCars)
    print('Number of persons in the image is ', numberOfPersons)
    
    calculateTrafficLightTime([numberOfCars, 10, 15]) # Number Of Roads = 3
    if numberOfPersons >= 1:
        # Find the half in which the person is
        # Danger Light on in those lanes
        pass
"""

def calculateTrafficLightTime(roadCarsCountList):
    minCount = min(roadCarsCountList)
    extraAllowance = MAX_GREEN_LIGHT_TIME - MIN_GREEN_LIGHT_TIME
    
    ratios = []
    for count in roadCarsCountList:
        ratio = ( (count - minCount) / sum(roadCarsCountList) )
        ratios.append(ratio)
    
    greenLightTimesList = []
    for ratio in ratios:
        greenLightTime = MIN_GREEN_LIGHT_TIME + ( ratio * extraAllowance )
        greenLightTimesList.append(round(greenLightTime))
    
    return greenLightTimesList

def greenLightsRoundRobin(greenLightTimesList):
    print("Inside Round Robin Function!")
    print(greenLightTimesList)
    for i in range(NUMBER_OF_ROADS):
        greenLightTime = greenLightTimesList[i]
        
        for j in range(NUMBER_OF_ROADS):
            if i == j:
                GPIO.output(GREENS[j], GPIO.HIGH)
                GPIO.output(REDS[j], GPIO.LOW)
            else:
                GPIO.output(GREENS[j], GPIO.LOW)
                GPIO.output(REDS[j], GPIO.HIGH)
        print("Start : ", time.time())
        print(greenLightTime)
        time.sleep(greenLightTime)
        print("End : ", time.time())
    for j in range(NUMBER_OF_ROADS):
        GPIO.output(GREENS[j], GPIO.LOW)
        GPIO.output(REDS[j], GPIO.LOW)


def main():

    GPIO.setwarnings(False)
    
    GPIO.cleanup()
    
    GPIO.setmode(GPIO.BCM)
    
    for i in range(NUMBER_OF_ROADS):
        GPIO.setup(GREENS[i], GPIO.OUT)
        GPIO.setup(REDS[i], GPIO.OUT)
    
    greenLightTimesList = calculateTrafficLightTime([25, 10, 15])
    totalTime = sum(greenLightTimesList)
    print(greenLightTimesList, totalTime)
    thread = Thread(target = greenLightsRoundRobin, args = (greenLightTimesList, ) )
    thread.start()
    thread.join()
    print("Threading Function Ends!")
    
        
    # start = time.time()

    # Turn Lights on in round robin fashion and then continue

"""def dangerLane(laneNumbers):
    # Turn on red lights in these lanes
    pass
choice = 1

while choice == 1:
    takePicture()
    detectAndCount(True)
    choice = int(input("Enter choice 1 to continue else anything else : "))
"""

if __name__ == "__main__":
    main()
