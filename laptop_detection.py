import time
import os
import numpy as np
import cv2

os.makedirs("screenshots", exist_ok = True)
# initialize the laptop webcam
cap = cv2.VideoCapture(0)

# set the frame size
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

last_frame = None  # used for comparisons
detected_motion = False
prev_detected_motion = False  # for screenshot trigger
screenshot_count = 0
frame_count = 0 # used if we want a temporary while

while True:
    ret, frame = cap.read()
    frame_count += 1

    if frame_count >= 150:
        break
    
    if not ret:
        print("Failed to grab frame from webcam")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if last_frame is None:
        last_frame = gray
        continue

    # compute the absolute difference between current and last frame
    frame_diff = cv2.absdiff(last_frame, gray)
    _, threshold = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)

    # count changed pixels
    motion_pixels = cv2.countNonZero(threshold)

    if motion_pixels > 1000:
        print("Motion detected!")
        detected_motion = True
    else:
        print("No motion")
        detected_motion = False

    # take screenshot when motion detection state changes
    if detected_motion != prev_detected_motion:
        screenshot_name = f"screenshots/screenshot_{screenshot_count}.png"
        cv2.imwrite(screenshot_name, frame)
        print(f"Saved {screenshot_name} due to motion state change")
        screenshot_count += 1

    prev_detected_motion = detected_motion
    last_frame = gray

    # show the current frame
    cv2.imshow('frame', frame)

    # break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# cleanup
cap.release()
cv2.destroyAllWindows()