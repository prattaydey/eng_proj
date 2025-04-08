import time
import numpy as np
import cv2
from picamera2 import Picamera2

# Initialize the camera
picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())
picam2.start()

# Video writer setup
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

last_frame = None
detected_motion = False
frame_rec_count = 0

while True:
    # Capture an image from the camera
    frame = picam2.capture_array()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if last_frame is None:
        last_frame = gray
        continue

    # Compute the absolute difference between the current frame and the previous frame
    frame_diff = cv2.absdiff(last_frame, gray)
    _, threshold = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)

    # Count non-zero pixels in the threshold image (motion)
    motion_pixels = cv2.countNonZero(threshold)
    if motion_pixels > 1000:
        print("Motion detected!")
        detected_motion = True

    last_frame = gray  # Update the last frame

    # Start recording once motion is detected
    if detected_motion:
        out.write(frame)
        frame_rec_count += 1

    # Show the current frame for debugging
    cv2.imshow('frame', frame)

    # Stop after recording for 240 frames or on 'q' key press
    if (cv2.waitKey(1) & 0xFF == ord('q')) or frame_rec_count == 240:
        break

# Release resources
picam2.stop()
out.release()
cv2.destroyAllWindows()

