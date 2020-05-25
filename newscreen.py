# Imports
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import Adafruit_SSD1306
import board
import math
import digitalio
import os
import time
import RPi.GPIO as GPIO
from datetime import datetime
#from newmain import adc_queue

# GPIO info
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(19, GPIO.OUT, initial=GPIO.LOW) # LED
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # BUTTON

# Define the Reset Pin
#oled_reset = digitalio.DigitalInOut(board.D18)
oled_reset = 18

# OLED info
WIDTH = 128
HEIGHT = 64  # Change to 64 if needed
BORDER = 2

# DESIGN INFO
DIVIDER_HEIGHT = 1
DIVIDER_WIDTH = 0

STROKE_HEIGHT = 10
STROKE_WIDTH = 2

# 128x64 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=oled_reset, i2c_address=0x3D)

# Begin the OLED session
disp.begin()

# Function to clear the display
def clearDisplay():
	disp.clear()
	disp.display()

# Function to draw a diamond with equal side lengths
# draw = draw object from image canvas
# x = center x coordinate
# y = center y coordinate
# side_length = length of side of diamond
def drawDiamond(draw, x, y, inner_length):
	# Draw as top -> right -> bottom -> left ->>
	draw.polygon([(x, y + inner_length), (x + inner_length, y), (x, y - inner_length), (x - inner_length, y)], outline=255, fill=255)

# Clear initially
clearDisplay()

# Final Variables
fps = 25
fps_int = 1/fps # Interval for FPS in seconds

# Create image buffer
image = Image.new('1', (WIDTH, HEIGHT))

# Variable for tracking time
loop_count = 0
time_window = 2 # Seconds to show in the view

# Create drawing object.
draw = ImageDraw.Draw(image)

# The stroke objects stored as array pairs of [[Hand, Stroke Time]
strokes = [["L", 0.5], ["R", 0.5], ["R", 0.75], ["L", 1], ["L", 1.5]]

# The current coordinates of strokes on the timeline
recorded_strokes = []

# Load default font.
font = ImageFont.load_default()

def loopScreen(adc_queue):
	global draw
	global loop_count
	global fps
	global time_window
	global WIDTH
	global HEIGHT
	global DIVIDER_WIDTH
	global strokes
	global image
	global disp
	global font
	global fps_int

	# Begin While Loop
	while(True):
		# Clear the display
		# Clear image buffer by drawing a black filled box.
		draw.rectangle((0,0, WIDTH, HEIGHT), outline=0, fill=0)

		# Draw the static divider
		draw.rectangle((0, HEIGHT // 2, WIDTH, HEIGHT // 2), outline=255, fill=255)

		# Get the current scaled time
		scaled_time = loop_count / (fps * time_window)

		# Draw the dynamic divider on the time axis
		DIVIDER_WIDTH = math.floor(scaled_time * WIDTH)
		draw.rectangle((0, HEIGHT // 2 - DIVIDER_HEIGHT, DIVIDER_WIDTH, HEIGHT // 2 + DIVIDER_HEIGHT), outline=255, fill=255)

		# Draw the strokes dynamically
		for stroke in strokes:
			stroke_time = (stroke[1] / time_window) * WIDTH
			if stroke[0] == "L": # Top of Screen
				draw.rectangle((stroke_time, STROKE_HEIGHT, stroke_time, STROKE_HEIGHT * 2), outline=255, fill=255)
			else:
				draw.rectangle((stroke_time, (HEIGHT - STROKE_HEIGHT), stroke_time, (HEIGHT - STROKE_HEIGHT * 2)), outline=255, fill=255)

		# Draw the recorded strokes
		for stroke in recorded_strokes:
			drawDiamond(draw, stroke, HEIGHT // 2, 5) # Draw the diamond representing the stroke

		# Draw the L & R identifiers
		draw.text((2, 2), "L", font=font, fill=255)
		draw.text((2, HEIGHT - 9), "R", font=font, fill=255)

		# Check if the adc_queue is empty
		if(not adc_queue.empty()):
			adc_queue.get() # pop the first entry
			recorded_strokes.append(DIVIDER_WIDTH) # Append the current time


		# Display the image
		disp.image(image)
		disp.display()

		# check if the escape button is pressed
		if GPIO.input(12) == GPIO.HIGH:
			print("\nDrumTime Screen Interface is now exiting")
			clearDisplay()
			break

		# Reset the dynamic counter
		if loop_count >= time_window * fps:
			loop_count = 0
			recorded_strokes.clear() # Clear the recorded strokes

		loop_count += 1 # Increment the loop count
		time.sleep(fps_int) # Rest for 1/fps
