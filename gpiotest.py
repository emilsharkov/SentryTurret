import subprocess

def start_pigpiod():
    try:
        # Starting pigpiod as a sudo command
        subprocess.run(['sudo', 'pigpiod'], check=True)
        print("pigpiod started successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while starting pigpiod: {e}")

# Call the function to start pigpiod
start_pigpiod()

servo = Servo(gpio, min_value=0, max_value=270, min_pulse=0.5, max_pulse=2.5, frequency=50)
