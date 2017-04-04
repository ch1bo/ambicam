import base64
import cv2
import json
import numpy as np
import picamera
import picamera.array
import socket
import sys
import time

PRIORITY = 90
HOST = '192.168.1.104'
PORT = 19444
RESOLUTION = (640,480)
FRAMERATE = 10
M = np.load('M.npy')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
with picamera.PiCamera(resolution=RESOLUTION, framerate=FRAMERATE) as camera:
    with picamera.array.PiRGBArray(camera, size=RESOLUTION) as raw:
        time.sleep(2)
        start = cv2.getTickCount()
        for frame in camera.capture_continuous(raw, format="bgr", use_video_port=True):
            print('captured: ' + str((cv2.getTickCount() - start) / cv2.getTickFrequency()))
            warped = cv2.warpPerspective(frame.array, M, RESOLUTION)
            print('warped: ' + str((cv2.getTickCount() - start) / cv2.getTickFrequency()))
            rgb = cv2.cvtColor(warped, cv2.COLOR_BGR2RGB)
            print('converted: ' + str((cv2.getTickCount() - start) / cv2.getTickFrequency()))
            # data = json.dumps({
            #     'command': 'image',
            #     'priority': PRIORITY,
            #     'imageheight': rgb.shape[0],
            #     'imagewidth': rgb.shape[1],
            #     'imagedata': base64.b64encode(rgb.tobytes()).decode('ascii')
            # }) + '\n'
            data = b'{"command":"image",' + \
                   b'"priority":' + str(PRIORITY).encode('utf-8') + b',' \
                   b'"imageheight":' + str(rgb.shape[0]).encode('utf-8') + b',' \
                   b'"imagewidth":' + str(rgb.shape[1]).encode('utf-8') + b',' \
                   b'"imagedata":"' + base64.b64encode(rgb.tobytes()) + b'"' + \
                   b'}' + '\n'.encode('utf-8')
            print('encoded: ' + str((cv2.getTickCount() - start) / cv2.getTickFrequency()))
            s.send(data)
            print('sent: ' + str((cv2.getTickCount() - start) / cv2.getTickFrequency()))
            raw.seek(0)
            fps = cv2.getTickFrequency() / (cv2.getTickCount() - start)
            print('FPS: ' + str(fps))
            start = cv2.getTickCount()

data = json.dumps({'command': 'clearall'}) + '\n'
s.sendall(data.encode('utf-8'))
s.close()
