import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import time as time

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BCM) # USE BOARD GPIO
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)

while True: # Run forever
    if GPIO.input(26) == GPIO.HIGH:
        print("Button was pushed!")
        time.sleep(1)
