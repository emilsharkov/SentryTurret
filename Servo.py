import RPi.GPIO as GPIO
import time



class Servo:
    def __init__(self,gpioPin,servo_range,desired_max_range,min_pulse_micro_seconds,max_pulse_micro_seconds,frequency):
        
        self.degrees = 0 
        self.frequency = frequency
        self.max_range = desired_max_range

    def calculateDutyCycle(self,degrees):
        servo_pulse_width_micro_seconds = self.frequency / 10**6


    def turn(self,degrees):
        if degrees + self.degrees > self.max_range:
            self.degrees = self.max_range
        else:
            self.degrees += degrees
        
        self.servo.write(self.degrees)

if __name__=='__main__':
    servo = Servo(
                gpioPin=17,
                servo_range=270,
                desired_max_range=270,
                min_pulse=0.5,
                max_pulse=2.5,
                frequency=50
            )
    
    servo.turn(30)