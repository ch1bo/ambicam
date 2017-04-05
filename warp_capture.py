import picamera
import picamera.array
import cv2
import time
import numpy as np
import multiprocessing as mp
import queue
import signal

def capture(q, stop, resolution=(640,480), framerate=40):
    print('Start capturing...')
    with picamera.PiCamera(resolution=resolution, framerate=framerate) as camera:
        with picamera.array.PiRGBArray(camera, size=resolution) as raw:
            time.sleep(2)
            M = np.load('M.npy')
            start = cv2.getTickCount()
            for frame in camera.capture_continuous(raw, format="bgr", use_video_port=True):
                # try:
                #     q.put(frame.array, False)
                # except queue.Full:
                #     #print('capture: full')
                #     pass
                #warped = cv2.warpPerspective(frame.array, M, (320, 240))
                raw.seek(0)
                print('capture: ' + str((cv2.getTickCount() - start) / cv2.getTickFrequency()))
                start = cv2.getTickCount()
                if stop.is_set():
                    break
    print('Capturing done')
    q.cancel_join_thread()

def process(q, stop):
    print('Start processing...')
    M = np.load('M.npy')
    # video = cv2.VideoWriter('output.avi',cv2.VideoWriter_fourcc(*'MJPG'), 30.0, (640,480))
    while not stop.is_set():
        start = cv2.getTickCount()
        frame = None
        try:
            while True: # clear queue
                frame = q.get(False)
        except queue.Empty:
            if frame is None:
                continue
            print('dequeue: ' + str((cv2.getTickCount() - start) / cv2.getTickFrequency()))
            warped = cv2.warpPerspective(frame, M, (320, 240))
            print('warp: ' + str((cv2.getTickCount() - start) / cv2.getTickFrequency()))
            # video.write(warped)
            # cv2.imshow('video', warped)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break
        #fps = cv2.getTickFrequency() / (cv2.getTickCount() - start)
        print('process: ' + str((cv2.getTickCount() - start) / cv2.getTickFrequency()))
    print('Processing done')

def main():
    q = mp.Queue(10)
    stop = mp.Event()
    def sigint(signal, frame):
        stop.set()
    signal.signal(signal.SIGINT, sigint)

    capture(q, stop)
    # p = mp.Process(target=capture, args=(q, stop))
    # p.start()
    # try:
    #     process(q, stop)
    # finally:
    #     stop.set()
    #     p.join()

if __name__ == "__main__":
    main()
