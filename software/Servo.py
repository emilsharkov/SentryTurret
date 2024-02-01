import RPi.GPIO as GPIO
import time

class Servo:
    def __init__(self,gpioPin,servo_range,desired_servo_range,min_pulse_micro_seconds,max_pulse_micro_seconds,frequency):
        self.currentAngle = 0 
        self.frequency = frequency
        self.angle_max_range = desired_servo_range if desired_servo_range == None else servo_range
        self.min_pulse_micro_seconds = min_pulse_micro_seconds
        self.max_pulse_micro_seconds = max_pulse_micro_seconds
        self.gpioPin = gpioPin
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(gpioPin,GPIO.OUT)
        self.pwm = GPIO.PWM(gpioPin,frequency)
        self.pwm.start(self.getDutyCycle(self.currentAngle))

    def __del__(self):
        self.pwm.stop()
        GPIO.cleanup()

    def getDutyCycle(self,degrees):
        servo_pulse_micro_seconds = 10**6 / self.frequency # (10^6 microseconds per second) / (# cycles per second) =  # seconds / cycle 
        pulse_range_micro_seconds = self.max_pulse_micro_seconds - self.min_pulse_micro_seconds
        percent_angle = degrees / self.angle_max_range
        target_pulse_micro_seconds = self.min_pulse_micro_seconds + (pulse_range_micro_seconds * percent_angle)
        dutyCycle = (target_pulse_micro_seconds / servo_pulse_micro_seconds) * 100
        return dutyCycle

    def turn(self,degrees):
        if degrees + self.currentAngle > self.angle_max_range:
            self.currentAngle = self.angle_max_range
        elif degrees + self.currentAngle < 0:
            self.currentAngle = 0
        else:
            self.currentAngle += degrees
        
        newDutyCycle = self.getDutyCycle(self.currentAngle)
        self.pwm.ChangeDutyCycle(newDutyCycle)

if __name__=='__main__':
    servo1 = Servo(
        gpioPin=17,
        servo_range=270,
        desired_servo_range=80,
        min_pulse_micro_seconds=500,
        max_pulse_micro_seconds=2500,
        frequency=50
    )

    servo2 = Servo(
        gpioPin=24,
        servo_range=270,
        desired_servo_range=180,
        min_pulse_micro_seconds=500,
        max_pulse_micro_seconds=2500,
        frequency=50
    )
    
    servo1.turn(40)
    servo2.turn(90)
    time.sleep(1)
    servo1.turn(40)
    servo2.turn(90)
    time.sleep(1)
    servo1.turn(-90)
    servo2.turn(-180)
    time.sleep(1)