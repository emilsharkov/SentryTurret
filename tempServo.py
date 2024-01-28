import RPi.GPIO as GPIO
import time

class Servo:
    def __init__(self,gpioPin,servo_range,desired_servo_range,min_pulse_micro_seconds,max_pulse_micro_seconds,frequency):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(gpioPin,GPIO.OUT)
        self.pwm = GPIO.PWM(gpioPin,frequency)
        self.currentAngle = 0 
        self.frequency = frequency
        self.angle_max_range = desired_servo_range if desired_servo_range == None else servo_range
        self.min_pulse_micro_seconds = min_pulse_micro_seconds
        self.max_pulse_micro_seconds = max_pulse_micro_seconds

    def __del__(self):
        self.pwm.stop()
        GPIO.cleanup()

    def getDutyCycle(self,degrees):
        servo_pulse_micro_seconds = 10**6 / self.frequency # (10^6 microseconds per second) / (# cycles per second) =  # seconds / cycle 
        pulse_range_micro_seconds = self.max_pulse_micro_seconds - self.min_pulse_micro_seconds
        percent_angle = degrees / self.angle_max_range
        target_pulse_micro_seconds = self.min_pulse_micro_seconds + (pulse_range_micro_seconds * percent_angle)
        dutyCycle = target_pulse_micro_seconds / servo_pulse_micro_seconds
        return dutyCycle

    def turn(self,degrees):
        if degrees + self.degrees > self.angle_max_range:
            self.degrees = self.angle_max_range
        elif degrees + self.degrees < 0:
            self.degrees = 0
        else:
            self.degrees += degrees
        
        newDutyCycle = self.getDutyCycle(self.degrees)
        self.pwm.ChangeDutyCycle(newDutyCycle)

if __name__=='__main__':
    servo = Servo(
        gpioPin=17,
        servo_range=270,
        desired_servo_range=270,
        min_pulse_micro_seconds=500,
        max_pulse_micro_seconds=2500,
        frequency=50
    )
    
    servo.turn(45)