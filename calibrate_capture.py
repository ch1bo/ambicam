import picamera
import picamera.array
import cv2
import time
import numpy as np
import multiprocessing as mp
import queue
import signal

def capture(q, stop, resolution=(640,480), framerate=30):
    print('Start capturing...')
    with picamera.PiCamera(resolution=resolution, framerate=framerate) as camera:
        with picamera.array.PiRGBArray(camera, size=resolution) as raw:
            time.sleep(2)
            start = cv2.getTickCount()
            for frame in camera.capture_continuous(raw, format="bgr", use_video_port=True):
                try:
                    q.put(frame.array, False)
                except queue.Full:
                    print('capture: full')
                raw.truncate(0)
                fps =  (cv2.getTickCount() - start) / cv2.getTickFrequency() * 1000
                print('capture: ' + str(fps))
                start = cv2.getTickCount()
                if stop.is_set():
                    break
    print('Capturing done')
    q.cancel_join_thread()


def order_points(pts):
    rect = np.zeros((4, 2), dtype = "float32")

    s = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def process(q, stop):
    print('Start processing...')
    M = np.load('M.npy')
    def nothing(x):
        pass
    cv2.namedWindow('video', cv2.WINDOW_NORMAL)
    cv2.createTrackbar('threshold', 'video', 58, 255, nothing)
    cv2.createTrackbar('cannyLow', 'video', 50, 255, nothing)
    cv2.createTrackbar('cannyHigh', 'video', 150, 255, nothing)
    video = cv2.VideoWriter('output.avi',cv2.VideoWriter_fourcc(*'MJPG'), 20.0, (640,480))
    while not stop.is_set():
        start = cv2.getTickCount()
        frame = None
        try:
            while True: # clear queue
                frame = q.get(False)
        except queue.Empty:
            if frame is None:
                continue

            threshold = cv2.getTrackbarPos('threshold','video')
            cannyLow = cv2.getTrackbarPos('cannyLow','video')
            cannyHigh = cv2.getTrackbarPos('cannyHigh','video')

            frame = frame[:300, :320]
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            ret, black = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
            if not ret:
                continue
            edges = cv2.Canny(black, cannyLow, cannyHigh)
            _, contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                continue
            out = frame.copy()
            allC = np.vstack(contours)
            hull = cv2.convexHull(allC)
            cv2.drawContours(out, [hull], 0, (0,0,255), 2)
            rect = cv2.minAreaRect(allC)
            box = np.int0(cv2.boxPoints(rect))
            im = cv2.drawContours(out,[box],0,(0,255,0),2)

            corners = order_points(box)
            dst = np.array([[0, 0],
                            [639, 0],
                            [639, 479],
                            [0, 479]], dtype = "float32")
            M = cv2.getPerspectiveTransform(corners, dst)
            np.save("M", M)
            # video.write(out)
            cv2.imshow('video', out)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        fps =  (cv2.getTickCount() - start) / cv2.getTickFrequency() * 1000
        print('process: ' + str(fps))
    print('Processing done')

def main():
    q = mp.Queue(10)
    stop = mp.Event()
    def sigint(signal, frame):
        stop.set()
    signal.signal(signal.SIGINT, sigint)

    p = mp.Process(target=capture, args=(q, stop))
    p.start()
    try:
        process(q, stop)
    finally:
        stop.set()
        p.join()

if __name__ == "__main__":
    main()
