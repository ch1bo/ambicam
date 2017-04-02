import cv2
import numpy
import sys

def nothing(x):
    pass

cv2.namedWindow('video', cv2.WINDOW_NORMAL)
cv2.createTrackbar('threshold', 'video', 58, 255, nothing)
cv2.createTrackbar('cannyLow', 'video', 50, 255, nothing)
cv2.createTrackbar('cannyHigh', 'video', 150, 255, nothing)
cv2.createTrackbar('hughThreshold', 'video', 35, 200, nothing)
cv2.createTrackbar('hughMinLength', 'video', 40, 255, nothing)
cv2.createTrackbar('hughMaxGap', 'video', 15, 255, nothing)

while True:
    cap = cv2.VideoCapture('test3.mp4')
    while(cap.isOpened()):
        start = cv2.getTickCount()
        ret, frame = cap.read()
        if not ret:
            break # loop video

        threshold = cv2.getTrackbarPos('threshold','video')
        cannyLow = cv2.getTrackbarPos('cannyLow','video')
        cannyHigh = cv2.getTrackbarPos('cannyHigh','video')
        hughThreshold = cv2.getTrackbarPos('hughThreshold','video')
        hughMinLength = cv2.getTrackbarPos('hughMinLength','video')
        hughMaxGap = cv2.getTrackbarPos('hughMaxGap','video')

        # Detect lines
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret, black = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        if not ret:
            continue
        edges = cv2.Canny(black, cannyLow, cannyHigh)
        # edges = cv2.Laplacian(black, cv2.CV_8U, 5)
        # lines = cv2.HoughLinesP(edges, 1, numpy.pi / 180, hughThreshold, hughMinLength, hughMaxGap)
        # Intersect (naiive) and draw lines
        out = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        # corners = []
        if lines is not None:
            for line in lines:
                x1,y1,x2,y2 = line[0]
                cv2.line(out, (x1,y1), (x2,y2), (0,0,255), 2)
                for line2 in lines:
                    x3,y3,x4,y4 = line2[0]
                    # TODO rewrite using dot and scalar product
                    denom = (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)
                    if denom != 0:
                        xc = ((x1*y2-y1*x2)*(x3-x4)-(x1-x2)*(x3*y4-y3*x4) / denom)
                        yc = ((x1*y2-y1*x2)*(y3-y4)-(y1-y2)*(x3*y4-y3*x4) / denom)
                        # corners.append([xc, yc])
                        cv2.circle(out, (int(xc),int(yc)), 3, (0,255,0), 2)

        fps = cv2.getTickFrequency() / (cv2.getTickCount() - start)
        cv2.putText(out, 'FPS: ' + str(fps), (10,30), cv2.FONT_HERSHEY_PLAIN, 2, (0,255,0), 2)
        cv2.imshow('video', out)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            sys.exit(0)
