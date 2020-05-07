import RPi.GPIO as GPIO
import time

pin = 5

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

while True:
	print("On")
	GPIO.output(pin, GPIO.HIGH)
	time.sleep(2)
	print("Off")
	GPIO.output(pin, GPIO.LOW)
	time.sleep(2)
