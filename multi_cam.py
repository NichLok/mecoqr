# pip install imutils
# ref: https://www.pyimagesearch.com/2016/01/18/multiple-cameras-with-the-raspberry-pi-and-opencv/

from imutils.video import VideoStream
import cv2

picam = VideoStream(usePiCamera=True).start()
webcam = VideoStream(src=1).start()

frame_webcam = webcam.read()
frame_picam = picam.read()

cv2.imwrite('/home/pi/Desktop/testwebcam.jpg', frame_webcam)
cv2.imwrite('/home/pi/Desktop/testpicam.jpg', frame_picam)

webcam.stop()
picam.stop()