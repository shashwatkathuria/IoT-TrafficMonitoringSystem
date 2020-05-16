import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

try:
    print("Hold tag near reader : ")
    id, text = reader.read()
    print(id)
    print(text)
except KeyboardInterrupt:
    GPIO.cleanup()
    raise
