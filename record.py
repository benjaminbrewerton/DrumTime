# Class for recording audio sampled from the microphone

import sys
import wave
from scipy.io.wavfile import write
import numpy as np

target_file = sys.argv[1] # The target file for reading text
buffer_size = 1024 # Size of a page to write from
channels = 1 # Monosound
rate = 750 # Samples per second
wave_file_name = "noutput.wav" # Output file name

raw_stream = open(target_file, "r") # open the audio stream from the text file

stream_s = [] # Array for containing the samples
delta = 0 # Time of recording
count = 0

for sample in raw_stream:
	if sample.startswith("d: "):
		count_time = (sample.split(" ")[1]).split(",") # obtain the delta
		delta = float(count_time[0])
		count = int(count_time[1])
	else:
		stream_int = int(sample) << 6 # Convert to 16 bit from 10 bit
		#stream_s.append(stream_int.to_bytes(2, "little")) # Append to the stream
		stream_s.append(stream_int - 2**15)
		print(stream_int - 2**15)

new_samples = np.array(stream_s, dtype=np.int16)
write(wave_file_name, int(count / delta), new_samples)

#wf = wave.open(wave_file_name, 'wb')
#wf.setnchannels(channels)
#wf.setsampwidth(2)
#wf.setframerate(rate)
#wf.writeframes(b''.join(stream_s))
#wf.close()

print("count: " + str(count))
