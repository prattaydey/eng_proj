import time
import os
import numpy as np
import cv2
from picamera2 import Picamera2

os.makedirs("screenshots", exist_ok=True)

# Raspberry Pi camera (v1.3)
picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())
picam2.start()

last_frame = None  # used for comparisons
detected_motion = False
prev_detected_motion = False  # to track changes in motion state
screenshot_count = 0
start_time = time.time()

while True:
    # capture a frame from the Pi camera
    frame = picam2.capture_array()
    
    # check how much time has passed (10s for now)
    if time.time() - start_time >= 10:  
        break

    # convert to grayscale and blur to reduce noise
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if last_frame is None:
        last_frame = gray
        continue

    # compute the absolute difference between the current frame and the previous frame
    frame_diff = cv2.absdiff(last_frame, gray)
    _, threshold = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)

    # count the number of white pixels (i.e., regions of change/motion)
    motion_pixels = cv2.countNonZero(threshold)

    # update the motion flag based on a threshold (here, 1000 pixels)
    if motion_pixels > 1000:
        print("Motion detected!")
        detected_motion = True
    else:
        print("No motion")
        detected_motion = False

    # take a screenshot when the motion detection state changes
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

picam2.stop()
cv2.destroyAllWindows()
