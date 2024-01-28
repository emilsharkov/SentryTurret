import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.OUT)
pwm=GPIO.PWM(17,50)
pwm.start(12.5)
print('Dobre')
try:
	while True:
		pwm.ChangeDutyCycle(2.5)
		time.sleep(1)
		
		pwm.ChangeDutyCycle(7.5)
		time.sleep(1)
		
		pwm.ChangeDutyCycle(12.5)
		time.sleep(1)
except:
	pwm.stop()
	GPIO.cleanup()
