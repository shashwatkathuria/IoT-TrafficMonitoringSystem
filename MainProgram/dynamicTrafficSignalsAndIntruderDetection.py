# Importing libraries required
from threading import Thread
import time, random
import RPi.GPIO as GPIO
import cv2
import matplotlib.pyplot as plt
import cvlib as cv
from cvlib.object_detection import draw_bbox

# Initializing constants required
MIN_GREEN_LIGHT_TIME = 5
MAX_GREEN_LIGHT_TIME = 30
NUMBER_OF_ROADS = 3
YELLOW_LIGHT_TIME = 2
roundRobinInProcess = False
GREENS = [17, 18, 16]
YELLOWS = [27, 23, 20]
REDS = [22, 24, 21]
DANGERS = [13, 19, 26]

globalI = 1
imageCount = 0

# import picamera
# camera = picamera.PiCamera()

def main():

    # Setting up GPIO
    GPIO.setwarnings(False)
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)

    # Setting up GPIO Pins
    for i in range(NUMBER_OF_ROADS):
        GPIO.setup(GREENS[i], GPIO.OUT)
        GPIO.setup(YELLOWS[i], GPIO.OUT)
        GPIO.setup(REDS[i], GPIO.OUT)
        GPIO.setup(DANGERS[i], GPIO.OUT)

    # GPIO Pins all LOW initially
    for j in range(NUMBER_OF_ROADS):
        GPIO.output(GREENS[j], GPIO.LOW)
        GPIO.output(YELLOWS[j], GPIO.LOW)
        GPIO.output(REDS[j], GPIO.LOW)
        GPIO.output(DANGERS[j], GPIO.LOW)

    # Starting trafficLightInfiniteLoop as a thread
    # Always running
    trafficLightsInfiniteLoopThread = Thread(target = trafficLightInfiniteLoop)
    trafficLightsInfiniteLoopThread.start()

    # Starting detectingAndCountingInfiniteLoopThread as a thread
    # Always running
    # detectingAndCountingInfiniteLoopThread = Thread(target = detectIntrudersAndCountCars, args = (True,))
    # detectingAndCountingInfiniteLoopThread.start()

    # Joining threads
    trafficLightsInfiniteLoopThread.join()
    # detectingAndCountingInfiniteLoopThread.join()

    # Setting all GPIO Pins LOW
    for j in range(NUMBER_OF_ROADS):
        GPIO.output(GREENS[j], GPIO.LOW)
        GPIO.output(YELLOWS[j], GPIO.LOW)
        GPIO.output(REDS[j], GPIO.LOW)
        GPIO.output(DANGERS[j], GPIO.LOW)

# def detectIntrudersAndCountCars(showOutputImage = False):
#     """Function to report counts of cars and detect intruders on the road."""
# 
#     print("Detecting cars and people now")
#     im = cv2.imread('./../Basics/PersonDetection/people_2.jpeg')
#     bbox, label, conf = cv.detect_common_objects(im)
#     print("Done detecting.")
#     if showOutputImage == True:
#         print("Drawing contours now.")
#         output_image = draw_bbox(im, bbox, label, conf)
#         plt.imshow(output_image)
#         plt.show()
#     numberOfCars = label.count('car')
#     numberOfPersons = label.count('person')
#     numberOfDogs = label.count('dog')
#     numberOfCats = label.count('cat')
#     print(label)
#     print('Number of cars in the image is ', numberOfCars)
#     print('Number of persons in the image is ', numberOfPersons)
# 
#     if numberOfPersons >= 1 or numberOfDogs >= 1 or numberOfCats >= 1:
#         for j in range(NUMBER_OF_ROADS):
#             GPIO.output(DANGERS[j], GPIO.HIGH)
#         print("PEOPLE DETECTED ON ROAD!! STOP DRIVING IMMEDIATELY!!")
#     else:
#         for j in range(NUMBER_OF_ROADS):
#             GPIO.output(DANGERS[j], GPIO.LOW)

def trafficLightInfiniteLoop():
    global roundRobinInProcess, globalI
    
    
    nameOfFile = f'./../Basics/RoadImages/r{globalI}.png'
    im = cv2.imread(nameOfFile)
    bbox, label, conf = cv.detect_common_objects(im)
    while True:
        if roundRobinInProcess == False:
            roundRobinInProcess = True
#             output_image = draw_bbox(im, bbox, label, conf)
#             plt.imshow(output_image)
#             plt.show()
#             print("The global I is ", globalI)
            numberOfCars = label.count('car')
            numberOfMotorcycles = label.count('motorcycle')
            numberOfPersons = label.count('person')
            numberOfDogs = label.count('dog')
            numberOfCats = label.count('cat')
#             print(label, numberOfCars, numberOfMotorcycles)
            if numberOfPersons >= 1 or numberOfDogs >= 1 or numberOfCats >= 1:
                for j in range(NUMBER_OF_ROADS):
                    GPIO.output(DANGERS[j], GPIO.HIGH)
                print("PEOPLE DETECTED ON ROAD!! STOP DRIVING IMMEDIATELY!!")
            else:
                for j in range(NUMBER_OF_ROADS):
                    GPIO.output(DANGERS[j], GPIO.LOW)
            trafficCount = numberOfCars + numberOfMotorcycles
            trafficLightTimesInput = [trafficCount, random.randint(0, trafficCount), random.randint(trafficCount, 50)]
            greenLightTimesList = calculateTrafficLightTime(trafficLightTimesInput)
            totalTime = sum(greenLightTimesList)
            for i in range(NUMBER_OF_ROADS):
                print(f"Traffic count on road number {i + 1}: {trafficLightTimesInput[i]}\t Time Allocated: {greenLightTimesList[i]} sec")
#             print(trafficLightTimesInput, greenLightTimesList, totalTime)
            showLightsThread = Thread(target = greenLightsRoundRobin, args = (greenLightTimesList, ) )
            showLightsThread.start()
            globalI += 1
            if globalI == 14:
                return
            nameOfFile = f'./../Basics/RoadImages/r{globalI}.png'
#             nameOfFile = f'./../Basics/RoadImages/p1.jpeg'
            im = cv2.imread(nameOfFile)
            bbox, label, conf = cv.detect_common_objects(im)
            showLightsThread.join()
#             print("Show Traffic Lights Threading Function Joins Main Thread!")
            roundRobinInProcess = False
            


def calculateTrafficLightTime(roadCarsCountList):
    """Function to give appropriate green light times for the roads."""

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
    """Function to turn on appropriate GPIO traffic signals in a
       round robin fashion in the NUMBER_OF_ROADS."""

#     print("Inside Round Robin Function!")
#     print(greenLightTimesList)
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
        print(f"Traffic Light {i + 1} Start : ", time.time())
        print(f"{greenLightTime} sec duration")
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
        print(f"Traffic Light {i + 1} End : ", time.time())
    for j in range(NUMBER_OF_ROADS):
        GPIO.output(GREENS[j], GPIO.LOW)
        GPIO.output(YELLOWS[j], GPIO.LOW)
        GPIO.output(REDS[j], GPIO.LOW)
        GPIO.output(DANGERS[j], GPIO.LOW)


def takePicture():
    """Function to take a picture using PiCamera."""
    nameOfFile = f'./../Basics/RoadImages/r{imageCount}.jpg'
    camera.capture(nameOfFile)
    imageCount += 1

# Calling main function
if __name__ == "__main__":
    main()
