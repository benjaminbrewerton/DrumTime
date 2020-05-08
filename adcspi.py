import spidev
import time
import os
from datetime import datetime
 
# Open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 50000
 
# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7
def ReadChannel(channel):
    adc = spi.xfer2([1,(8+channel)<<4,0])
    data = ((adc[1]&3) << 8) + adc[2]
    return data

samples = []

before = datetime.now()

for x in range(0,100):
    samples.append(ReadChannel(0))
    # Wait before repeating loop
    time.sleep(1/100)

after = datetime.now()

for sample in samples:
    print(sample)

delta = after-before

print("Time: " + str(delta.total_seconds()))
