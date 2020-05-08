import os
import time
import RPi.GPIO as GPIO
from datetime import datetime
import spidev

# GPIO info
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(19, GPIO.OUT)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 50000

# Function to query the ADC
def ReadChannel(channel):
	# Transfer 1000 to read channel 0 with the D0-D2 bits
    adc = spi.xfer2([1, (8+channel) << 4 , 0])
	# Receive the bits b0-b9 from the adc sample
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

avg_count = 0 # A count of the total
moving_avg = (2**10) / 2 # half point of a 10 bit register, the centered point
loop_count = 1 # Count of loop iterations
sample_rate = 10000 # Sampling rate in Hz
interval = 1/sample_rate # Interval between loop iterations

# Threshold of stroke to background noise
threshold = 0.2

# Array for holding samples
samples = []

# Record start time of loop
startDate = datetime.now()

while True:
	# Read the ADC Value
	adc_value = ReadChannel(0)

	# Check to illuimate the LED if the threshold is crossed
	if adc_value * (1-threshold) > moving_avg:
		GPIO.output(19,GPIO.HIGH)
		time.sleep(0.1)
		GPIO.output(19,GPIO.LOW)

	# # Check if loop count exceeds 1000000
	# if loop_count > 1000:
		loop_count = 1
		avg_count = 0

	# # Calculate the moving average
	avg_count += adc_value	
	moving_avg = avg_count / loop_count
	loop_count += 1

	# Append the 10 bit voltage value
	samples.append(adc_value)
	
	# check if the escape button is pressed
	if GPIO.input(12) == GPIO.HIGH:
		print("\n\nDrumTime is now exiting")
		break

	# End of Loop
	time.sleep(interval)

# Record the end time of the loop
endDate = datetime.now()

# check if output exists and delete if it does
if os.path.exists("output.txt"):
	os.remove("output.txt")

# Write output to file
f = open("output.txt", "a")
deltaDate = endDate - startDate
# Write the time in seconds of recording
f.write("d: " + str(deltaDate.total_seconds()) + "," + str(loop_count) + "\n")
# Continue writing the data
for sample in samples:
	f.write(str(sample) + "\n")
f.close()

# Print the final data
print("count " + str(loop_count) + " samples")
print("time: " + str(deltaDate.total_seconds()) + "s")
