import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

try:
    text = input("Enter data to be written into tag : ")
    print("Now place tag to write : ")
    reader.write(text)
    print("Written")
finally:
    GPIO.cleanup()
