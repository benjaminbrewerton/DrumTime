import os
import time
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import RPi.GPIO as GPIO

# GPIO info
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(19,GPIO.OUT)
 
# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
 
# create the cs (chip select)
cs = digitalio.DigitalInOut(board.D22)
 
# create the mcp object
mcp = MCP.MCP3008(spi, cs)
 
# create an analog input channel on pin 0
chan0 = AnalogIn(mcp, MCP.P0)

avg_count = 0 # A count of the total
moving_avg = 1.65 # half of 3.3V, the centered point
loop_count = 1 # Count of loop iterations
interval = 1/100 # Loop interval
sample_rate = 1/interval # Sampling rate in Hz

# Threshold of stroke to background noise
threshold = 0.2


while True:
	if chan0.voltage * (1-threshold) > chan0.voltage:
		GPIO.output(19,GPIO.HIGH)
		time.sleep(0.1)
		GPIO.output(19,GPIO.LOW)

	# Check if loop count exceeds 1000000
	if loop_count > 1000000:
		loop_count = 1
		avg_count = 0

	# Calculate the moving average
	avg_count += chan0.voltage	
	moving_avg = avg_count / loop_count

	print(moving_avg)
	#print('ADC Value: ' + str(chan0.value))
	#print('ADC Voltage: ' + str(chan0.voltage) + 'V')
	time.sleep(interval)
	loop_count += 1
