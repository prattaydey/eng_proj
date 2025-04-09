import time
import os
import numpy as np
import cv2
from picamera2 import Picamera2
from gpiozero import LED  # Import LED from gpiozero

# Set up the LED using gpiozero
LED_PIN = 25  # GPIO pin 25 to control the LED
led = LED(LED_PIN)  # Create an LED object to control GPIO pin 25

# Create the 'screenshots' folder if it doesn't exist
os.makedirs("screenshots", exist_ok=True)

# Initialize the Raspberry Pi camera (v1.3) using Picamera2
picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())
picam2.start()

last_frame = None  # used for comparisons
detected_motion = False
prev_detected_motion = False  # to track changes in motion state
screenshot_count = 0
frame_count = 0

while True:
    # Capture a frame from the Pi camera
    frame = picam2.capture_array()
    
    frame_count += 1
    print(
    if frame_count >= 100:  # keep for XXX seconds (adjust if needed)
        break

    # Convert to grayscale and blur to reduce noise
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if last_frame is None:
        last_frame = gray
        continue

    # Compute the absolute difference between the current frame and the previous frame
    frame_diff = cv2.absdiff(last_frame, gray)
    _, threshold = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)

    # Count the number of white pixels (i.e., regions of change/motion)
    motion_pixels = cv2.countNonZero(threshold)

    # Update the motion flag based on a threshold (here, 1000 pixels)
    if motion_pixels > 1000:
        print("Motion detected!")
        detected_motion = True
        led.on()  # Turn LED on (set GPIO pin 25 to LOW to power the cathode)
    else:
        print("No motion")
        detected_motion = False
        led.off()  # Turn LED off (set GPIO pin 25 to HIGH to cut power to the cathode)

    # Take a screenshot when the motion detection state changes
    if detected_motion != prev_detected_motion:
        screenshot_name = f"screenshots/screenshot_{screenshot_count}.png"
        cv2.imwrite(screenshot_name, frame)
        print(f"Saved {screenshot_name} due to motion state change")
        screenshot_count += 1

    # Update the previous state and the last frame for the next iteration
    prev_detected_motion = detected_motion
    last_frame = gray
    
    # Resize the frame to make it smaller (ex 640x480)
    resized_frame = cv2.resize(frame, (320, 240))

    # Display the current frame for debugging
    cv2.imshow('frame', resized_frame)

    # Exit if the user presses 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup resources
led.off()
picam2.stop()
cv2.destroyAllWindows()


