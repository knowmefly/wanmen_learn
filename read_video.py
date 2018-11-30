import numpy as np
import cv2

def videoLive():
	cap = cv2.videoCapture(0)

	while (True):
		ret, frame = cap.read()
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

		cv2.imshow('frame', gray)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

	cap.release()
	cv2.destroyAllWindows()

def videoOpen():
	cap = cv2.videoCapture('video/1.mp4')

	if (cap.isOpened() == False):
		print("Error")

	while (cap.isOpened()):
		ret, frame = cap.read()
		if ret == True:
			cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
			cv2.imshow('frame', frame)

			if cv2.waitKey(25) & 0xFF==ord('e'):
				break
		else:
			break
	cap.release()

	cv2.destroyAllWindows()

if __name__ == '__main__':
	videoOpen()			
			