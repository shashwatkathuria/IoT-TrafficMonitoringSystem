from threading import Thread


import time
import RPi.GPIO as GPIO

MIN_GREEN_LIGHT_TIME = 5
MAX_GREEN_LIGHT_TIME = 30  
NUMBER_OF_ROADS = 3
NUMBER_OF_LANES = 3
YELLOW_LIGHT_TIME = 2
roundRobinInProcess = False
GREENS = [17, 18, 16] 
YELLOWS = [27, 23, 20] 
REDS = [22, 24, 21]
DANGERS = [13, 19, 26]

# import picamera
# camera = picamera.PiCamera()

import cv2
import matplotlib.pyplot as plt
import cvlib as cv
from cvlib.object_detection import draw_bbox

def takePicture():
    camera.capture('snapshot.jpg')
    print("Just took the photo")
    
def detectIntrudersAndCountCars(showOutputImage = False):
    print("Detecting cars and people now")
    im = cv2.imread('./../Basics/PersonDetection/people_2.jpeg')
    # im = cv2.imread('./../RoadImages/cars_1.jpeg')
    bbox, label, conf = cv.detect_common_objects(im)
    print("Done detecting.")
    if showOutputImage == True:
        print("Drawing contours now.")
        output_image = draw_bbox(im, bbox, label, conf)
        plt.imshow(output_image)
        plt.show()
    numberOfCars = label.count('car')
    numberOfPersons = label.count('person')
    numberOfDogs = label.count('dog')
    numberOfCats = label.count('cat')
    print(label)
    print('Number of cars in the image is ', numberOfCars)
    print('Number of persons in the image is ', numberOfPersons)
    
    if numberOfPersons >= 1:
        # Find the half in which the person is
        # Danger Light on in those lanes
        for j in range(NUMBER_OF_ROADS):
            GPIO.output(DANGERS[j], GPIO.HIGH)
        print("PEOPLE DETECTED ON ROAD!! STOP DRIVING IMMEDIATELY!!")
    elif numberOfPersons == 0:
        for j in range(NUMBER_OF_ROADS):
            GPIO.output(DANGERS[j], GPIO.LOW)
            
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
                GPIO.output(YELLOWS[j], GPIO.LOW)
                GPIO.output(REDS[j], GPIO.LOW)
            else:
                GPIO.output(GREENS[j], GPIO.LOW)
                GPIO.output(YELLOWS[j], GPIO.LOW)
                GPIO.output(REDS[j], GPIO.HIGH)
        print("Start : ", time.time())
        print(greenLightTime)
        time.sleep(greenLightTime - YELLOW_LIGHT_TIME)
        
        for j in range(NUMBER_OF_ROADS):
            if i == j:
                GPIO.output(GREENS[j], GPIO.LOW)
                GPIO.output(YELLOWS[j], GPIO.HIGH)
                GPIO.output(REDS[j], GPIO.LOW)
            else:
                GPIO.output(GREENS[j], GPIO.LOW)
                GPIO.output(YELLOWS[j], GPIO.LOW)
                GPIO.output(REDS[j], GPIO.HIGH)
        
        time.sleep(YELLOW_LIGHT_TIME)
        print("End : ", time.time())
    for j in range(NUMBER_OF_ROADS):
        GPIO.output(GREENS[j], GPIO.LOW)
        GPIO.output(YELLOWS[j], GPIO.LOW)
        GPIO.output(REDS[j], GPIO.LOW)
        GPIO.output(DANGERS[j], GPIO.LOW)


def trafficLightInfiniteLoop():
    global roundRobinInProcess
    while True:
        if roundRobinInProcess == False:
            roundRobinInProcess = True
            trafficLightTimesInput = [ int(element) for element in input("Enter space separated road traffic counts : ").split(" ")]
            greenLightTimesList = calculateTrafficLightTime(trafficLightTimesInput)
            totalTime = sum(greenLightTimesList)
            print(greenLightTimesList, totalTime)
            showLightsThread = Thread(target = greenLightsRoundRobin, args = (greenLightTimesList, ) )
            showLightsThread.start()
            showLightsThread.join()
            print("Threading Function Ends!")
            roundRobinInProcess = False
    

def main():

    GPIO.setwarnings(False)
    
    GPIO.cleanup()
    
    GPIO.setmode(GPIO.BCM)
    
    for i in range(NUMBER_OF_ROADS):
        GPIO.setup(GREENS[i], GPIO.OUT)
        GPIO.setup(YELLOWS[i], GPIO.OUT)
        GPIO.setup(REDS[i], GPIO.OUT)
        GPIO.setup(DANGERS[i], GPIO.OUT)
        
    for j in range(NUMBER_OF_ROADS):
        GPIO.output(GREENS[j], GPIO.LOW)
        GPIO.output(YELLOWS[j], GPIO.LOW)
        GPIO.output(REDS[j], GPIO.LOW)
        GPIO.output(DANGERS[j], GPIO.LOW)
    
    trafficLightsInfiniteLoopThread = Thread(target = trafficLightInfiniteLoop)
    trafficLightsInfiniteLoopThread.start()
    """for i in range(5):
        print("Hello")
        time.sleep(1)"""
    
    detectingAndCountingInfiniteLoopThread = Thread(target = detectIntrudersAndCountCars, args = (True,))
    detectingAndCountingInfiniteLoopThread.start()
    
    # When we want to stop thread from executing
    trafficLightsInfiniteLoopThread.join()
    detectingAndCountingInfiniteLoopThread.join()
    
    for j in range(NUMBER_OF_ROADS):
        GPIO.output(GREENS[j], GPIO.LOW)
        GPIO.output(YELLOWS[j], GPIO.LOW)
        GPIO.output(REDS[j], GPIO.LOW)
        GPIO.output(DANGERS[j], GPIO.LOW)
    
    
    
    
        
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
