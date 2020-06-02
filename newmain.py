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
from queue import Queue

# GPIO info
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(19, GPIO.OUT, initial=GPIO.LOW) # Red LED
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Terminate Button

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

# Control the LED flash
doFlash = True

avg_count = 0 # A count of the total
moving_avg = (2**10) / 2 # half point of a 10 bit register, the centered point
loop_counter = 1 # Count of loop iterations
sample_rate = 1000 # Sampling rate in Hz
interval = 1/sample_rate # Interval between loop iterations

# Variable for controlling the start of the program
start_program = False

# Threshold of stroke to background noise
threshold = 0.35

# Array for holding samples
samples = []

# Record start time of loop
startDate = datetime.now()

# Last Threshold cross
crossDate = datetime.now()

# Create the queue to hold the ADC captures
adc_queue = Queue()

# Print a statement that the listeining is starting
print("Starting DrumTime with fs: " + str(sample_rate) + "Hz and sensitivity threshold of " + str(threshold*100) + "%")

def loopADC():
	global threshold
	global moving_avg
	global avg_count
	global loop_counter
	global interval
	global doFlash
	global doSampling
	global crossDate
	global adc_queue
	global start_program

	while start_program:
		# Read the ADC Value
		adc_value = ReadChannel(0)

		# Check whether to turn the LED off
		if (doFlash and (datetime.now() - startDate).total_seconds()) >= 0.8:
			doFlash = False
			GPIO.output(19,GPIO.LOW)


		# Check to illuimate the LED if the threshold is crossed
		if adc_value * (1-threshold) > moving_avg and ((datetime.now() - crossDate).total_seconds() >= 0.4):
			if not doFlash:
				GPIO.output(19,GPIO.HIGH)
				doFlash = True
			adc_queue.put(1)
			crossDate = datetime.now() # Update cross time
			#print(str(adc_value) + ", " + str(moving_avg))
		else:
			avg_count += adc_value

		# # Check if loop count exceeds 1000000
		#if loop_count > 100000:
		#	loop_count = 1
		#	avg_count = 0

		# # Calculate the moving average
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
thread2 = threading.Thread(target=loopScreen,args=(adc_queue,start_program,))

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
