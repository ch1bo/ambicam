import cv2
import numpy as np
import sys

def nothing(x):
    pass

cv2.namedWindow('video', cv2.WINDOW_NORMAL)
cv2.createTrackbar('threshold', 'video', 58, 255, nothing)
cv2.createTrackbar('cannyLow', 'video', 50, 255, nothing)
cv2.createTrackbar('cannyHigh', 'video', 150, 255, nothing)

def order_points(pts):
    # initialzie a list of coordinates that will be ordered
    # such that the first entry in the list is the top-left,
    # the second entry is the top-right, the third is the
    # bottom-right, and the fourth is the bottom-left
    rect = np.zeros((4, 2), dtype = "float32")

    # the top-left point will have the smallest sum, whereas
    # the bottom-right point will have the largest sum
    s = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    # now, compute the difference between the points, the
    # top-right point will have the smallest difference,
    # whereas the bottom-left will have the largest difference
    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    # return the ordered coordinates
    return rect

while True:
    cap = cv2.VideoCapture('test.mp4')
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
        _, contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        out = frame.copy()
        allC = np.vstack(contours)
        hull = cv2.convexHull(allC)
        cv2.drawContours(out, [hull], 0, (0,0,255), 2)
        rect = cv2.minAreaRect(allC)
        box = np.int0(cv2.boxPoints(rect))
        im = cv2.drawContours(out,[box],0,(0,255,0),2)
        cv2.imshow('video', out)

        corners = order_points(box)
        dst = np.array([[0, 0],
                        [639, 0],
                        [639, 479],
                        [0, 479]], dtype = "float32")
        M = cv2.getPerspectiveTransform(corners, dst)
        np.save("M", M)
        warped = cv2.warpPerspective(frame, M, (640, 480))

        fps = cv2.getTickFrequency() / (cv2.getTickCount() - start)
        cv2.putText(out, 'FPS: ' + str(fps), (10,30), cv2.FONT_HERSHEY_PLAIN, 2, (0,255,0), 2)
        cv2.imshow('result', warped)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            sys.exit(0)
