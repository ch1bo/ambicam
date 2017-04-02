import picamera
import picamera.array
import cv2
import time
import numpy
import sys

cv2.namedWindow('video', cv2.WINDOW_NORMAL)

with picamera.PiCamera() as camera:
    with picamera.array.PiYUVArray(camera, size=(640, 480)) as rawCapture:
        camera.resolution = (640, 480)
        camera.framerate = 60
        time.sleep(0.1)
        start = cv2.getTickCount()
        for frame in camera.capture_continuous(rawCapture, format='yuv', use_video_port=True):
                yuv = frame.array
                # color = frame.array
                # gray = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)
                # ret, black = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY)
                # if not ret:
                #         continue
                # edges = cv2.Canny(black, 50, 150)
                # #edges = cv2.Laplacian(black, cv2.CV_8U, 5)
                # # lines = cv2.HoughLinesP(edges, 1, numpy.pi / 180, hughThreshold, hughMinLength, hughMaxGap)
                # _, contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                # if not contours:
                #         continue
                # #out = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
                # # cont = longestContour(contours)
                # # hull = cv2.convexHull(cont)
                # #cv2.drawContours(color, contours, -1, (0,0,255), 2)
                # rect = cv2.minAreaRect(numpy.vstack(contours))
                # box = numpy.int0(cv2.boxPoints(rect))
                # #im = cv2.drawContours(out,[box],0,(0,255,0),2)

                cv2.imshow('frame', yuv)
                rawCapture.truncate(0)
                fps = cv2.getTickFrequency() / (cv2.getTickCount() - start)
                print(fps)
                start = cv2.getTickCount()
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

cv2.destroyAllWindows()
