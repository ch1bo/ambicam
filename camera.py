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

def process(q, stop):
    print('Start processing...')
    # cv2.namedWindow('video', cv2.WINDOW_NORMAL)
    out = cv2.VideoWriter('output.avi',cv2.VideoWriter_fourcc(*'MJPG'), 20.0, (640,480))
    while not stop.is_set():
        start = cv2.getTickCount()
        frame = None
        try:
            while True: # clear queue
                frame = q.get(False)
        except queue.Empty:
            if frame is None:
                continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            ret, black = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)
            if not ret:
                continue
            edges = cv2.Canny(black, 50, 150)
            _, contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            rect = cv2.minAreaRect(np.vstack(contours))
            print(rect)
            out.write(frame)
            # cv2.imshow('video', gray)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break
        fps =  (cv2.getTickCount() - start) / cv2.getTickFrequency() * 1000
        print('process: ' + str(fps))
    # cv2.destroyAllWindows()
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
