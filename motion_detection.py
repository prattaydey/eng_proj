import time
import os
import numpy as np
import cv2
from picamera2 import Picamera2
from gpiozero import LED

# Set up the LED using gpiozero
LED_PIN = 25
led = LED(LED_PIN)

# Create the 'screenshots' folder if it doesn't exist
os.makedirs("screenshots", exist_ok=True)

# Initialize the Raspberry Pi camera
picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())
picam2.start()

last_frame = None
detected_motion = False
prev_detected_motion = False
screenshot_count = 0
frame_count = 0

while True:
    frame = picam2.capture_array()
    frame_count += 1
    
    if screenshot_count >= 5:  # Optional stopping condition, adjust if needed
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if last_frame is None:
        last_frame = gray
        continue

    frame_diff = cv2.absdiff(last_frame, gray)
    _, threshold = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)

    motion_pixels = cv2.countNonZero(threshold)

    if motion_pixels > 1000:  # Adjust the threshold based on your needs
        print("Motion detected!")
        detected_motion = True
        led.on()  # Turn on the LED when motion is detected
    else:
        print("No motion")
        detected_motion = False
        led.off()  # Turn off the LED when no motion is detected

    if detected_motion != prev_detected_motion:
        screenshot_name = f"screenshots/screenshot_{screenshot_count}.png"
        cv2.imwrite(screenshot_name, frame)
        print(f"Saved {screenshot_name} due to motion state change")
        screenshot_count += 1

    prev_detected_motion = detected_motion
    last_frame = gray

    # Commented out because we're running headlessly (no display)
    # resized_frame = cv2.resize(frame, (320, 240))
    # cv2.imshow('frame', resized_frame)

    # Commented out to avoid needing user input in a headless environment
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break

    time.sleep(1)  # Add a small delay to reduce CPU usage

# Cleanup
led.off()
picam2.stop()

# No need to use cv2.destroyAllWindows() since we don't have a GUI

