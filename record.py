# Class for recording audio sampled from the microphone

import sys
import wave

target_file = sys.argv[0] # The target file for reading text
buffer_size = 1024 # Size of a page to write from
channels = 1 # Monosound
rate = 7500 # Samples per second
wave_file_name = "output.wav" # Output file name

raw_stream = open(target_file, "r") # open the audio stream from the text file

stream = [] # Array for containing the samples

for sample in raw_stream:
    stream.append(sample) # Append to the stream

wf = wave.open(wave_file_name, 'wb')
wf.setnchannels(channels)
wf.setsampwidth(2)
wf.setframerate(rate)
wf.writeframes(b''.join(stream))
wf.close()
