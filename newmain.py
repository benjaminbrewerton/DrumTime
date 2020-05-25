import os
import time
import RPi.GPIO as GPIO
from datetime import datetime
import spidev
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import board
import digitalio
import threading
from newscreen import loopScreen

# GPIO info
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(19, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Define the Reset Pin
oled_reset = digitalio.DigitalInOut(board.D18)

# Open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 1000000

# OLED info
WIDTH = 128
HEIGHT = 64  # Change to 64 if needed
BORDER = 5

# Variables
doSampling = False

# Function to query the ADC
def ReadChannel(channel):
	# Transfer 1000 to read channel 0 with the D0-D2 bits
    adc = spi.xfer2([1, (8+channel) << 4 , 0])
	# Receive the bits b0-b9 from the adc sample
    data = ((adc[1] & 3) << 8) + adc[2]
    return data


doFlash = True
# Function to flash the LED for 0.4 seconds
def flashLED():
	while True:
		if doFlash:
			GPIO.output(19,GPIO.HIGH)
			time.sleep(0.3)
			GPIO.output(19,GPIO.LOW)
			doFlash = False

# Define a thread for the LED to flash on
led_thread = threading.Thread(target=flashLED)
# Start the thread
led_thread.start()

avg_count = 0 # A count of the total
moving_avg = (2**10) / 2 # half point of a 10 bit register, the centered point
loop_counter = 1 # Count of loop iterations
sample_rate = 1000 # Sampling rate in Hz
interval = 1/sample_rate # Interval between loop iterations

# Threshold of stroke to background noise
threshold = 0.3

# Array for holding samples
samples = []

# Record start time of loop
startDate = datetime.now()

# Print a statement that the listeining is starting
print("Starting DrumTime with fs: " + str(sample_rate) + "Hz and sensitivity threshold of " + str(threshold*100) + "%")

def loopADC():
	global threshold
	global moving_avg
	global avg_count
	global loop_counter
	global interval
	global doFlash


	while True:
		# Read the ADC Value
		adc_value = ReadChannel(0)

		# Check to illuimate the LED if the threshold is crossed
		if adc_value * (1-threshold) > moving_avg:
			doFlash = True

		# # Check if loop count exceeds 1000000
		#if loop_count > 100000:
		#	loop_count = 1
		#	avg_count = 0

		# # Calculate the moving average
		avg_count += adc_value
		moving_avg = avg_count / loop_counter
		loop_counter += 1

		#print(adc_value)
		#print(moving_avg)

		# Append the 10 bit voltage value
		if doSampling:
			samples.append(adc_value)

		# check if the escape button is pressed
		if GPIO.input(12) == GPIO.HIGH:
			print("\nDrumTime ADC is now exiting")
			break

		# End of Loop
		time.sleep(interval)

thread1 = threading.Thread(target=loopADC)
thread2 = threading.Thread(target=loopScreen)

# Start the threads
thread1.start()
thread2.start()

# Record the end time of the loop
endDate = datetime.now()

if doSampling:
	# check if output exists and delete if it does
	if os.path.exists("output.txt"):
		os.remove("output.txt")

	# Write output to file
	f = open("output.txt", "a")
	deltaDate = endDate - startDate
	# Write the time in seconds of recording
	f.write("d: " + str(deltaDate.total_seconds()) + "," + str(loop_counter) + "\n")
	# Continue writing the data
	for sample in samples:
		f.write(str(sample) + "\n")
	f.close()

# Print the final data
print("count " + str(loop_counter) + " samples")
print("time: " + str(deltaDate.total_seconds()) + "s")
