import cv2
import numpy
import sys

def nothing(x):
    pass

cv2.namedWindow('video', cv2.WINDOW_NORMAL)
cv2.createTrackbar('rho', 'video', 1, 500, nothing)
cv2.createTrackbar('phi', 'video', 1, 359, nothing)
cv2.createTrackbar('threshold', 'video', 35, 200, nothing)
cv2.createTrackbar('minLength', 'video', 40, 255, nothing)
cv2.createTrackbar('maxGap', 'video', 50, 255, nothing)

while True:
    cap = cv2.VideoCapture('test3.mp4')
    while(cap.isOpened()):
        ret, frame = cap.read()
        if not ret:
            break # loop video

        rho = cv2.getTrackbarPos('rho','video')
        if rho <= 0:
            rho = 1
        phi = cv2.getTrackbarPos('phi','video')
        if phi <= 0:
            phi = 1
        threshold = cv2.getTrackbarPos('threshold','video')
        minLength = cv2.getTrackbarPos('minLength','video')
        maxGap = cv2.getTrackbarPos('maxGap','video')

        # Detect lines
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        # lines = cv2.HoughLinesP(edges, rho, phi * numpy.pi / 180, threshold, minLength, maxGap)
        # if lines is not None:
        #     for line in lines:
        #         x1,y1,x2,y2 = line[0]
        #         cv2.line(frame, (x1,y1), (x2,y2), (0,0,255), 2)

        cv2.imshow('video', edges)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            sys.exit(0)
