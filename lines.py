import cv2
import numpy as np
import sys

def nothing(x):
    pass

cv2.namedWindow('video', cv2.WINDOW_NORMAL)
cv2.createTrackbar('threshold', 'video', 58, 255, nothing)
cv2.createTrackbar('cannyLow', 'video', 50, 255, nothing)
cv2.createTrackbar('cannyHigh', 'video', 150, 255, nothing)

def longestContour(contours):
    m = 0
    longest = None
    for c in contours:
        l = cv2.arcLength(c, True)
        if l > m:
            m = l
            longest = c
    return longest

while True:
    cap = cv2.VideoCapture('test2.mp4')
    while(cap.isOpened()):
        start = cv2.getTickCount()
        ret, frame = cap.read()
        if not ret:
            break # loop video

        threshold = cv2.getTrackbarPos('threshold','video')
        cannyLow = cv2.getTrackbarPos('cannyLow','video')
        cannyHigh = cv2.getTrackbarPos('cannyHigh','video')

        # Detect lines
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret, black = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        if not ret:
            continue
        edges = cv2.Canny(black, cannyLow, cannyHigh)
        # edges = cv2.Laplacian(black, cv2.CV_8U, 5)
        # lines = cv2.HoughLinesP(edges, 1, np.pi / 180, hughThreshold, hughMinLength, hughMaxGap)
        _, contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        out = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        # longestC = longestContour(contours)
        allC = np.vstack(contours)
        hull = cv2.convexHull(allC)
        cv2.drawContours(out, [hull], 0, (0,0,255), 2)
        # corners = []
        # for i in range(1, len(hull)-1):
        #     prev = hull[i-1]
        #     p = hull[i]
        #     next = hull[i+1]
        #     ab = p - prev
        #     bc = np.transpose(next - p)
        #     angle = np.rad2deg(np.arccos(float(np.dot(ab, bc)) /
        #                                  (np.linalg.norm(ab) * np.linalg.norm(bc))))
        #     print(prev, p, next, ab, bc, angle)
        #     if abs(angle - 90) < 40:
        #         corners.append(p)
        #         cv2.circle(out, (p[0][0], p[0][1]), 10, (0,255,0), 2)

        rect = cv2.minAreaRect(np.vstack(contours))
        box = np.int0(cv2.boxPoints(rect))
        im = cv2.drawContours(out,[box],0,(0,255,0),2)

        fps = cv2.getTickFrequency() / (cv2.getTickCount() - start)
        cv2.putText(out, 'FPS: ' + str(fps), (10,30), cv2.FONT_HERSHEY_PLAIN, 2, (0,255,0), 2)
        cv2.imshow('video', out)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            sys.exit(0)
