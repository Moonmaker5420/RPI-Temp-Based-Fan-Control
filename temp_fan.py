import RPi.GPIO as GPIO
from time import sleep, time, strftime
import subprocess

# Pin Definitions
in1 = 24
en = 25
log_file = "/home/pi/fan_log.txt"  # Path to the log file

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(in1, GPIO.OUT)
GPIO.setup(en, GPIO.OUT)
GPIO.output(in1, GPIO.LOW)
p = GPIO.PWM(en, 1000)
p.start(0)  # Start PWM with 0 duty cycle (fan off initially)

def log_fan_start_time():
    with open(log_file, "a") as file:
        start_time = strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"Fan started at {start_time}\n")

def get_cpu_temperature():
    try:
        output = subprocess.check_output(["vcgencmd", "measure_temp"])
        temp_str = output.decode("UTF-8").strip().split("=")[1].split("'")[0]
        return float(temp_str)
    except Exception as e:
        #print(f"Error reading temperature: {e}")
        return None

def control_fan(temperature, threshold=40):
    if temperature is not None:
        if temperature >= threshold:
            GPIO.output(in1, GPIO.HIGH)  # Turn on the fan
            p.ChangeDutyCycle(100)  # Full speed
            log_fan_start_time()  # Log the start time
            #print(f"Temperature is {temperature}Â°C. Fan is ON.")
            return time()  # Return the current time when the fan is turned on
        else:
            GPIO.output(in1, GPIO.LOW)  # Turn off the fan
            p.ChangeDutyCycle(0)  # Fan off
            #print(f"Temperature is {temperature}Â°C. Fan is OFF.")
            return None

try:
    fan_on_time = None
    while True:
        temp = get_cpu_temperature()
        if fan_on_time:
            # Check if 3 minutes have passed
            if time() - fan_on_time >= 60:
                GPIO.output(in1, GPIO.LOW)  # Turn off the fan
                p.ChangeDutyCycle(0)  # Fan off
                fan_on_time = None  # Reset the fan_on_time
            else:
                # Continue running the fan
                pass
        else:
            # If fan is not running, control based on temperature
            fan_on_time = control_fan(temp)

        sleep(30)  # Check temperature every 30 seconds

except KeyboardInterrupt:
    GPIO.cleanup()
    #print("Script interrupted and GPIO cleaned up.")
except Exception as e:
    GPIO.cleanup()
    #print(f"An error occurred: {e}")
