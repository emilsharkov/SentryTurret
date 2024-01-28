import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setup(24,GPIO.OUT)

GPIO.output(24,GPIO.HIGH)
time.sleep(1)
GPIO.output(24,GPIO.LOW)
time.sleep(2)
GPIO.cleanup()
