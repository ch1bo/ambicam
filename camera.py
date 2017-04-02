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
            start = cv2.getTickCount()
            for frame in camera.capture_continuous(raw, format="bgr", use_video_port=True):
                print('got frame')
                try:
                    q.put(frame.array, False)
                except queue.Full:
                    print('capture: full')
                raw.truncate(0)
                fps = cv2.getTickFrequency() / (cv2.getTickCount() - start)
                print('capture: ' + str(fps))
                start = cv2.getTickCount()
                if stop.is_set():
                    break
                print('loop')
    print('Capturing done')

def process(q, stop):
    print('Start processing...')
    while not stop.is_set():
        start = cv2.getTickCount()
        try:
            frame = q.get(False)
        except queue.Empty:
            print('process: empty')
            time.sleep(0.1)
        else:
            #cv2.imshow('video', frame)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break
            time.sleep(0.03) # simulate 30ms processing
            fps = cv2.getTickFrequency() / (cv2.getTickCount() - start)
            print('process: ' + str(fps))
    cv2.destroyAllWindows()
    print('Processing done')

def main():
    q = mp.Queue(10)
    stop = mp.Event()
    def sigint(signal, frame):
        stop.set()
    signal.signal(signal.SIGINT, sigint)

    p = mp.Process(target=capture, args=(q, stop))
    p.start()
    process(q, stop)

    print('Shutdown')
    stop.set()
    q.close()
    q.join_thread()
    p.join() # TODO locks up

if __name__ == "__main__":
    main()
