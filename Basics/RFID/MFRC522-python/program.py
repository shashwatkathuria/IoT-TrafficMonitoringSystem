import RPi.GPIO as GPIO 
from mfrc522 import SimpleMFRC522
reader = SimpleMFRC522()

try:
    print("Hold a tag near the reader")
    id, text = reader.read()
    print("ID: %s\nText: %s" % (id,text))    
except KeyboardInterrupt:
    GPIO.cleanup()
    raise