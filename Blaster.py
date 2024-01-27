import RPIO as GPIO

class Blaster:
    def __init__(self,gpioPin):
        self.isBlasting = False
        self.gpioPin = gpioPin
        RPIO.setup(self.gpioPin, RPIO.OUT, initial=RPIO.LOW)
    
    def toggleShoot(self,isBlasting):
        self.isBlasting = isBlasting
        voltageOutput = RPIO.HIGH if self.isBlasting else RPIO.LOW
        RPIO.output(self.gpioPin,voltageOutput)