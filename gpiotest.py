import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setup(25,GPIO.OUT)
pwm=GPIO.PWM(25,100)
pwm.start(100)
print('Dobre')
try:
	while True:
		pwm.ChangeDutyCycle(5)
		time.sleep(1)
		
		pwm.ChangeDutyCycle(15)
		time.sleep(1)
		
		pwm.ChangeDutyCycle(25)
		time.sleep(1)
except KeyboardInterrupt:
	pwm.stop()
	GPIO.cleanup()
