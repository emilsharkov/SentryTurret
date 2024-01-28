import RPi.GPIO as GPIO
import time

# Define servo specifications
max_range_degrees = 270
min_pulse = 0.5  # Minimum pulse width in milliseconds
max_pulse = 2.5  # Maximum pulse width in milliseconds
frequency = 50  # PWM frequency in Hz

# Calculate the duty cycle range based on the servo specifications
duty_cycle_range = 100.0  # 0% to 100%

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
pwm = GPIO.PWM(17, frequency)

try:
    pwm.start(0)  # Start at 0 degrees

    while True:
        for position in [0, 135, 270, 135]:
            duty_cycle = (min_pulse * frequency) + (position / max_range_degrees) * duty_cycle_range
            pwm.ChangeDutyCycle(duty_cycle)
            time.sleep(2)

except KeyboardInterrupt:
    print("Ctrl+C pressed. Exiting...")
except Exception as e:
    print("An error occurred: ", str(e))
finally:
    pwm.stop()
    GPIO.cleanup()
