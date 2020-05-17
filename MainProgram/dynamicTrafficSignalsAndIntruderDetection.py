# Importing libraries required
from threading import Thread
import datetime, time, random
import RPi.GPIO as GPIO
import cv2
import matplotlib.pyplot as plt
import cvlib as cv
from cvlib.object_detection import draw_bbox

# Initializing lists and constants required
MIN_GREEN_LIGHT_TIME = 5
MAX_GREEN_LIGHT_TIME = 30
NUMBER_OF_ROADS = 3
YELLOW_LIGHT_TIME = 2
GREENS = [17, 18, 16]
YELLOWS = [27, 23, 20]
REDS = [22, 24, 21]
DANGERS = [13, 19, 26]
TOTAL_ROAD_IMAGES = 13

globalI = 1
imageCount = 0

# Lines commented, camera support can be added
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

    # Joining with main thread  when it ends
    trafficLightsInfiniteLoopThread.join()

    # Setting all GPIO Pins LOW
    for j in range(NUMBER_OF_ROADS):
        GPIO.output(GREENS[j], GPIO.LOW)
        GPIO.output(YELLOWS[j], GPIO.LOW)
        GPIO.output(REDS[j], GPIO.LOW)
        GPIO.output(DANGERS[j], GPIO.LOW)

def trafficLightInfiniteLoop():
    # global variable to keep track of image number
    global globalI
    
    # Reading first image
    nameOfFile = f'./../Basics/RoadImages/r{globalI}.png'
    im = cv2.imread(nameOfFile)
    # Detecting objects in the first image
    bbox, label, conf = cv.detect_common_objects(im)
    
    # Running loop till out of images of photos to analyze
    while True:
#             Lines commented, used for debugging and drawing
#             detected objects on plt
#             output_image = draw_bbox(im, bbox, label, conf)
#             plt.imshow(output_image)
#             plt.show()
#             print("The global I is ", globalI)
            print("--------------------")
            # Getting the count of respective category
            numberOfCars = label.count('car')
            numberOfMotorcycles = label.count('motorcycle')
            numberOfPersons = label.count('person')
            numberOfDogs = label.count('dog')
            numberOfCats = label.count('cat')
#             print(label, numberOfCars, numberOfMotorcycles)

            # If any intruder detected, turn on danger lights
            if numberOfPersons >= 1 or numberOfDogs >= 1 or numberOfCats >= 1:
                for j in range(NUMBER_OF_ROADS):
                    GPIO.output(DANGERS[j], GPIO.HIGH)
                print("PEOPLE DETECTED ON ROAD!! STOP DRIVING IMMEDIATELY!!")
            # Else turn all danger lights LOW (turn off)
            else:
                for j in range(NUMBER_OF_ROADS):
                    GPIO.output(DANGERS[j], GPIO.LOW)
                    
            # Getting traffic count
            trafficCount = numberOfCars + numberOfMotorcycles
            
            # For now analyzing only images of 1 road and for other 2, random integer traffic counts as below
            # Can obviously be extended to more all roads if NUMBER_OF_ROADS Raspberry Pis are available
            trafficLightTimesInput = [trafficCount, random.randint(0, trafficCount), random.randint(trafficCount, 50)]
                
            # Calculating dynamic traffic signal times
            greenLightTimesList = calculateTrafficLightTime(trafficLightTimesInput)
            totalTime = sum(greenLightTimesList)
            
            # Printing information
            for i in range(NUMBER_OF_ROADS):
                print(f"Traffic count on road number {i + 1}: {trafficLightTimesInput[i]}\t Time Allocated: {greenLightTimesList[i]} sec")
            
            # Running greenLightsRoundRobin function in a separate thread till we process further images
            showLightsThread = Thread(target = greenLightsRoundRobin, args = (greenLightTimesList, ) )
            # Starting thread 
            showLightsThread.start()
            
            # Incrementing photo number
            globalI += 1
            # Returning if all photos are analyzed
            # More images can obviously be added
            if globalI > TOTAL_ROAD_IMAGES:
                print("--------------------")
                return
            
            # Image path
            nameOfFile = f'./../Basics/RoadImages/r{globalI}.png'
            
#             Path of image in which people are on road
#             Uncomment to analyze the danger lights part
#             nameOfFile = f'./../Basics/RoadImages/p1.jpeg'
#             print(nameOfFile)
            
            # Reading image
            im = cv2.imread(nameOfFile)
            # Detecting objects
            bbox, label, conf = cv.detect_common_objects(im)
            
            # Joining the show lights thread back into the main thread now that we have detected the image
            # We will proceed only after both the tasks are done with
            showLightsThread.join()
#             print("Show Traffic Lights Threading Function Joins Main Thread!")

def calculateTrafficLightTime(roadCarsCountList):
    """Function to give appropriate green light times for the roads."""

    # Initializing variables required
    minCount = min(roadCarsCountList)
    extraAllowance = MAX_GREEN_LIGHT_TIME - MIN_GREEN_LIGHT_TIME

    # Getting ratios in which to bias traffic counts
    ratios = []
    for count in roadCarsCountList:
        ratio = ( (count - minCount) / sum(roadCarsCountList) )
        ratios.append(ratio)

    # Getting times after calculating from the ratios above and MIN_GREEN_LIGHT_TIME
    greenLightTimesList = []
    for ratio in ratios:
        greenLightTime = MIN_GREEN_LIGHT_TIME + ( ratio * extraAllowance )
        greenLightTimesList.append(round(greenLightTime))

    # Returning final answer
    return greenLightTimesList

def greenLightsRoundRobin(greenLightTimesList):
    """Function to turn on appropriate GPIO traffic signals in a
       round robin fashion in the NUMBER_OF_ROADS."""

#     print("Inside Round Robin Function!")
#     print(greenLightTimesList)

    # For each road, round robin
    for i in range(NUMBER_OF_ROADS):
        greenLightTime = greenLightTimesList[i]

        # Looping over all roads
        for j in range(NUMBER_OF_ROADS):

            # Turning appropriate road light green 
            if i == j:
                GPIO.output(GREENS[j], GPIO.HIGH)
                GPIO.output(YELLOWS[j], GPIO.LOW)
                GPIO.output(REDS[j], GPIO.LOW)
            # All other road lights red
            else:
                GPIO.output(GREENS[j], GPIO.LOW)
                GPIO.output(YELLOWS[j], GPIO.LOW)
                GPIO.output(REDS[j], GPIO.HIGH)
                
        # Printing information
        print(f"Traffic Light {i + 1} Start : ", datetime.datetime.now().time())
        print(f"{greenLightTime} sec duration")
        
        # Green light time includes YELLOW_LIGHT_TIME also
        # Sleep till appropriate green light time, let the appropriate lights
        # remain as they are (green/red)
        time.sleep(greenLightTime - YELLOW_LIGHT_TIME)

        # Looping over all roads
        for j in range(NUMBER_OF_ROADS):
            
            # Turning appropriate road light yellow 
            if i == j:
                GPIO.output(GREENS[j], GPIO.LOW)
                GPIO.output(YELLOWS[j], GPIO.HIGH)
                GPIO.output(REDS[j], GPIO.LOW)
            # All other road lights red
            else:
                GPIO.output(GREENS[j], GPIO.LOW)
                GPIO.output(YELLOWS[j], GPIO.LOW)
                GPIO.output(REDS[j], GPIO.HIGH)

        # Sleep till appropriate yellow light time, let the appropriate lights
        # remain as they are (yellow/red)
        time.sleep(YELLOW_LIGHT_TIME)
        print(f"Traffic Light {i + 1} End : ", datetime.datetime.now().time())
    
    # Setting all lights low (resetting GPIO Pins) after all traffic signal times are done with
    for j in range(NUMBER_OF_ROADS):
        GPIO.output(GREENS[j], GPIO.LOW)
        GPIO.output(YELLOWS[j], GPIO.LOW)
        GPIO.output(REDS[j], GPIO.LOW)
        GPIO.output(DANGERS[j], GPIO.LOW)


def takePicture():
    """Function to take a picture using PiCamera."""

    # Initializing name of file
    nameOfFile = f'./../Basics/RoadImages/r{imageCount}.jpg'
    # Capturing image
    camera.capture(nameOfFile)
    # Incrementing photo count
    imageCount += 1

# Calling main function
if __name__ == "__main__":
    main()
