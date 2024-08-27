import RPi.GPIO as GPIO
from time import sleep
import subprocess

# Pin Definitions
in1 = 24
en = 25

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(in1, GPIO.OUT)
GPIO.setup(en, GPIO.OUT)
GPIO.output(in1, GPIO.LOW)
p = GPIO.PWM(en, 1000)
p.start(0)  # Start PWM with 0 duty cycle (fan off initially)

def get_cpu_temperature():
    try:
        output = subprocess.check_output(["vcgencmd", "measure_temp"])
        temp_str = output.decode("UTF-8").strip().split("=")[1].split("'")[0]
        return float(temp_str)
    except Exception as e:
        #print(f"Error reading temperature: {e}")
        return None

def control_fan(temperature, threshold=45):
    if temperature is not None:
        if temperature >= threshold:
            GPIO.output(in1, GPIO.HIGH)  # Turn on the fan
            p.ChangeDutyCycle(100)  # Full speed
            #print(f"Temperature is {temperature}°C. Fan is ON.")
        else:
            GPIO.output(in1, GPIO.LOW)  # Turn off the fan
            p.ChangeDutyCycle(0)  # Fan off
            #print(f"Temperature is {temperature}°C. Fan is OFF.")

try:
    while True:
        temp = get_cpu_temperature()
        control_fan(temp)
        sleep(10)  # Check temperature every 10 seconds
except KeyboardInterrupt:
    GPIO.cleanup()
    #print("Script interrupted and GPIO cleaned up.")
except Exception as e:
    GPIO.cleanup()
    #print(f"An error occurred: {e}")
