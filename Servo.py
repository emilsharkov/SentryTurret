from piservo import Servo
import time

class Servo:
    def __init__(self,gpioPin,servo_range,desired_max_range,min_pulse,max_pulse,frequency):
        self.servo = Servo(
                           gpioPin, 
                           min_value=0, 
                           max_value=servo_range, 
                           min_pulse=min_pulse, 
                           max_pulse=max_pulse, 
                           frequency=frequency
                        )
        self.degrees = 0 
        self.max_range = desired_max_range

    def turn(self,degrees):
        if degrees + self.degrees > self.max_range:
            self.degrees = self.max_range
        else:
            self.degrees += degrees
        
        self.servo.write(self.degrees)

