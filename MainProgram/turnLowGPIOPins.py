import RPi.GPIO as GPIO

NUMBER_OF_ROADS = 3
GREENS = [17, 25, 16] 
YELLOWS = [27, 8, 20] 
REDS = [22, 7, 21]
DANGERS = [13, 19, 26]

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
