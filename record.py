# Class for recording audio sampled from the microphone

import sys
from scipy.io.wavfile import write
import numpy as np

target_file = sys.argv[1] # The target file for reading text
wave_file_name = "noutput.wav" # Output file name

raw_stream = open(target_file, "r") # open the audio stream from the text file

stream_s = [] # Array for containing the samples
delta = 0 # Time of recording
count = 0 # Sample count from recording

for sample in raw_stream:
	# Check if the line starts with the date flag
	if sample.startswith("d: "):
		# Split the contant by space to remove the "d: "
		count_time = (sample.split(" ")[1]).split(",") # obtain the delta
		delta = float(count_time[0])  # The recording time
		count = int(count_time[1])	# The sample count
	else:
		stream_int = int(sample) << 6 # Convert to 16 bit from 10 bit
		stream_s.append(stream_int - 2**15) # Remove the bias and reduce the waveform around a volume of 0 at adc value 0

# Calculate the actual sampling ratea
rate = int(count / delta)

# Transform the read samples into a list type of int16
new_samples = np.array(stream_s, dtype=np.int16)

# Write the wave file to the system
write(wave_file_name, rate, new_samples)

# Output final results
print("Sample Count: " + str(count))
print("Recording Time: " + str(delta))
