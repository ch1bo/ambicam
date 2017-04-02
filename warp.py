import cv2
import numpy as np
import sys

M = np.load('M.npy')

while True:
    cap = cv2.VideoCapture('test2.mp4')
    while(cap.isOpened()):
        start = cv2.getTickCount()
        ret, frame = cap.read()
        if not ret:
            break # loop video
        warped = cv2.warpPerspective(frame, M, (640, 480))
        fps = cv2.getTickFrequency() / (cv2.getTickCount() - start)
        cv2.putText(warped, 'FPS: ' + str(fps), (10,30), cv2.FONT_HERSHEY_PLAIN, 2, (0,255,0), 2)
        cv2.imshow('result', warped)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            sys.exit(0)
