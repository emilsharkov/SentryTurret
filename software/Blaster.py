import RPi.GPIO as GPIO
import time

class Blaster:
    def __init__(self,gpioPin):
        self.isBlasting = False
        self.gpioPin = gpioPin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpioPin,GPIO.OUT)
    
    def __del__(self):
        GPIO.cleanup()

    def toggleShoot(self,isBlasting):
        self.isBlasting = isBlasting
        voltageOutput = GPIO.HIGH if self.isBlasting else GPIO.LOW
        GPIO.output(self.gpioPin,voltageOutput)

if __name__=='__main__':
    blaster = Blaster(23)
    blaster.toggleShoot(True)
    time.sleep(1)
    blaster.toggleShoot(False)