# Imports
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import Adafruit_SSD1306
import board
import math
import digitalio
import os
import time
import math
import RPi.GPIO as GPIO
from datetime import datetime
import adafruit_dotstar as dotstar


# 24 and 23
# Using a DotStar Digital LED Strip with 28 LEDs connected to digital pins
dots = dotstar.DotStar(board.SCK, board.MOSI, 28, brightness=0.2)
# Clear the strip
dots.fill(0)

# GPIO info
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(22, GPIO.OUT, initial=GPIO.LOW) # Green LED

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

STATIC_WINDOW_BORDER = 9 # Where the canvas should not draw to due to the placement of static images

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
	# Draw as top -> right -> bottom -> left ->> top
	draw.polygon([(x, y + inner_length), (x + inner_length, y), (x, y - inner_length), (x - inner_length, y)], outline=255, fill=255)

NAV_SEPARATION = 15 # Actually 2x this amount of separation
PLAY_PAUSE_LOC = WIDTH // 2 - NAV_SEPARATION
STOP_LOC = WIDTH // 2 + NAV_SEPARATION
NAV_BUTTON_HEIGHT = 6

# Functions to draw the navigation Functions
def drawPlay(draw):
	# Draw a rotated triangle
	# Defined from the bottom point of the play button
	draw.polygon([(PLAY_PAUSE_LOC, HEIGHT), (PLAY_PAUSE_LOC, HEIGHT - NAV_BUTTON_HEIGHT), (PLAY_PAUSE_LOC + NAV_BUTTON_HEIGHT, HEIGHT - (NAV_BUTTON_HEIGHT // 2))], outline=255, fill = 255)
# Function to draw the pause button
def drawPause(draw):
	# Draw rectangles from top left to bottom right corners
	# Left hand vertical line
	draw.rectangle((PLAY_PAUSE_LOC - NAV_BUTTON_HEIGHT // 2, HEIGHT - NAV_BUTTON_HEIGHT, PLAY_PAUSE_LOC - NAV_BUTTON_HEIGHT // 2 + 1, HEIGHT), outline=255, fill=255)
	# Right hand vertical line
	draw.rectangle((PLAY_PAUSE_LOC + NAV_BUTTON_HEIGHT // 2, HEIGHT - NAV_BUTTON_HEIGHT, PLAY_PAUSE_LOC + NAV_BUTTON_HEIGHT // 2 - 1, HEIGHT), outline=255, fill=255)
def drawStop(draw):
	# Draw a solid square
	draw.rectangle((STOP_LOC, HEIGHT - NAV_BUTTON_HEIGHT, STOP_LOC + NAV_BUTTON_HEIGHT, HEIGHT), outline=255, fill=255)


LED_COUNT = 28
# Functions for controlling the LED Strip
def showRightStroke():
	for i in range(LED_COUNT // 2):
		dots[i] = (62, 168, 50)
def clearRightStroke():
	for i in range(LED_COUNT // 2):
		dots[i] = (0, 0, 0)
def showLeftStroke():
	for i in range(LED_COUNT // 2, LED_COUNT):
		dots[i] = (62, 168, 50)
def clearLeftStroke():	
        for i in range(LED_COUNT // 2, LED_COUNT):
                dots[i] = (0, 0, 0)

# Clear initially
clearDisplay()

# Final Variables
fps = 30
fps_int = 1/fps # Interval for FPS in seconds

# Create image buffer
image = Image.new('1', (WIDTH, HEIGHT))

# Variable for tracking time
loop_count = 0
time_window = 2 # Seconds to show in the view
stroke_illuminate_sensitivity = 0.05 # How sensitive should it be to light up the stroke now LED

# Create drawing object.
draw = ImageDraw.Draw(image)

# The stroke objects stored as array pairs of [[Hand, Stroke Time]
strokes = [["L", 0.5], ["R", 0.5], ["R", 0.75], ["L", 1], ["L", 1.5]]

# The current coordinates of strokes on the timeline
recorded_strokes = []

# Load default font.
font = ImageFont.load_default()

# Draw default images
# Draw the L & R identifiers
draw.text((2, 0), "L", font=font, fill=255)
draw.text((2, HEIGHT - 9), "R", font=font, fill=255)
# Draw the pause and stop buttons
drawStop(draw)
drawPause(draw)

# LED Stopping Boolean
LEDStop = False
RightStop = False
LeftStop = False
Stoppers = []
for stroke in strokes:
	Stoppers.append([stroke[1], [stroke[0], False]]) # Append each stroke to the array
# Store as [Time, [L/R, LED Status]]

# Define a function to search through the Stoppers for a time
def getStopper(index): # Hand type, 1 = left, 2 = right
	queries = []
	for i in range(len(Stoppers)):
		if Stoppers[i][0] == index:
			queries.append([Stoppers[i][1][0], i]) # append the query as [Stroke (L/R), index]
	if len(queries) < 2:
		return [queries[0][1]] # Return the index
	else:
		return [queries[0][1], queries[1][1]]
	return []

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
	global LEDStop
	global LeftStop
	global RightStop
	global Stoppers

	# Begin While Loop
	while(True):
		# Clear the display
		# Clear image buffer by drawing a black filled box.
		# Exclude the bottom and top sections where static images are drawn
		draw.rectangle((0, STATIC_WINDOW_BORDER, WIDTH, HEIGHT - STATIC_WINDOW_BORDER), outline=0, fill=0)

		# Draw the static divider
		draw.rectangle((0, HEIGHT // 2, WIDTH, HEIGHT // 2), outline=255, fill=255)

		raw_time = loop_count / fps

		# Get the current scaled time
		scaled_time = raw_time / time_window

		# Draw the dynamic divider on the time axis
		DIVIDER_WIDTH = math.floor(scaled_time * WIDTH)
		draw.rectangle((0, HEIGHT // 2 - DIVIDER_HEIGHT, DIVIDER_WIDTH, HEIGHT // 2 + DIVIDER_HEIGHT), outline=255, fill=255)

		#LEDStop = False # Set the LED to be stopped if needed
		#LeftStop = False
		#RightStop = False
		# Draw the strokes dynamically
		for stroke in strokes:
			stroke_time = (stroke[1] / time_window) * WIDTH
			if stroke[0] == "L": # Top of Screen
				draw.rectangle((stroke_time, STROKE_HEIGHT, stroke_time, STROKE_HEIGHT * 2), outline=255, fill=255)
			else:
				draw.rectangle((stroke_time, (HEIGHT - STROKE_HEIGHT), stroke_time, (HEIGHT - STROKE_HEIGHT * 2)), outline=255, fill=255)
			
			
			diff_back = stroke[1] - stroke_illuminate_sensitivity # The bounds of sensing a stroke timing
			diff_for = stroke[1] + stroke_illuminate_sensitivity
			
			# Stopper Information about the LEDs
			Stopper_query = getStopper(stroke[1])

			for stopper in Stopper_query:
				Stopper_hand = Stoppers[stopper][1][0]
				Stopper_bool = Stoppers[stopper][1][1]

				if raw_time >= diff_back and raw_time <= diff_for:
					if not LEDStop:
						GPIO.output(22, GPIO.HIGH) # Output green to the LED
						LEDStop = True
					if len(Stopper_query) > 1 and not Stopper_bool:
						showLeftStroke()
						showRightStroke()
						Stoppers[stopper][1][1] = True
					elif not Stopper_bool:
						if (stroke[0] == "L" and Stopper_hand == "L"):
							showLeftStroke()
						if (stroke[0] == "R" and Stopper_hand == "R"):
							showRightStroke()
						Stoppers[stopper][1][1] = True # Update the LED to be triggered
				else:
					if LEDStop:
						GPIO.output(22, GPIO.LOW) # Turn off when out of bounds
						LEDStop = False
					if Stopper_bool:
                                       		if stroke[0] == "L" and Stopper_hand == "L":
                                                	clearLeftStroke()
                                        	if stroke[0] == "R" and Stopper_hand == "R":
                                                	clearRightStroke()
                                        	Stoppers[stopper][1][1] = False # Update the LED to be triggered


		# Draw the recorded strokes
		for stroke in recorded_strokes:
			drawDiamond(draw, stroke, HEIGHT // 2, 5) # Draw the diamond representing the stroke

		# Check if the adc_queue is empty
		if(not adc_queue.empty()):
			val = adc_queue.get() # pop the first entry
			
			if val == 1:
				recorded_strokes.append(DIVIDER_WIDTH) # Append the current time
			elif val == 2:
				drawPlay() # Display the play button
			elif val == 3:
				drawPause() # Display the Pause Button


		# Display the image
		disp.image(image)
		disp.display()

		# check if the escape button is pressed
		if GPIO.input(12) == GPIO.HIGH:
			print("\nDrumTime Screen Interface is now exiting")
			clearDisplay()
			dots.fill(0)
			break

		# Reset the dynamic counter
		if loop_count >= time_window * fps:
			loop_count = 0
			recorded_strokes.clear() # Clear the recorded strokes

		loop_count += 1 # Increment the loop count
		time.sleep(fps_int) # Rest for 1/fps
