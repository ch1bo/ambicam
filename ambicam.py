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
FRAMERATE = 18
M = np.load('M.npy')
M_ = np.linalg.inv(M)
res = np.load('res.npy')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
with picamera.PiCamera(resolution=RESOLUTION, framerate=FRAMERATE) as camera:
    with picamera.array.PiRGBArray(camera, size=RESOLUTION) as raw:
        time.sleep(2)
        start = cv2.getTickCount()
        for frame in camera.capture_continuous(raw, format="rgb", use_video_port=True):
            img = frame.array
            raw.seek(0)
            #warped = cv2.warpPerspective(frame.array, M, (width,height))
            # TODO use configured areas from hypercon
            width = res[0]
            height = res[1]
            offset = 5
            colors = []
            # bottom center -> bottom left
            for i in range(19):
                col = (width/2)-i*(width/2-offset)/19
                x_, y_, _ = np.dot(M_, [col, height-offset, 1])
                colors.extend(img[y_][x_].tolist())
            # bottom left -> top left
            for i in range(20):
                row = (height-offset)-i*(height-2*offset)/20
                x_, y_, _ = np.dot(M_, [offset, row, 1])
                colors.extend(img[y_][x_].tolist())
            # top left -> top right
            for i in range(36):
                col = offset+i*(width-2*offset)/36
                x_, y_, _ = np.dot(M_, [col, offset, 1])
                colors.extend(img[y_][x_].tolist())
            # top left -> bottom left
            for i in range(20):
                row = offset+i*(height-2*offset)/20
                x_, y_, _ = np.dot(M_, [offset, row, 1])
                colors.extend(img[y_][x_].tolist())
            # bottom right -> bottom center
            for i in range(17):
                col = (width-offset)-i*(width/2-offset)/17
                x_, y_, _ = np.dot(M_, [col, height-offset, 1])
                colors.extend(img[y_][x_].tolist())
            print('converted: ' + str((cv2.getTickCount() - start) / cv2.getTickFrequency()))
            data = (json.dumps({
                'command': 'color',
                'priority': PRIORITY,
                'color': colors
            }) + '\n').encode('utf-8')
            print('encoded: ' + str((cv2.getTickCount() - start) / cv2.getTickFrequency()))
            a = cv2.getTickCount()
            s.send(data)
            print('sent: ' + str((cv2.getTickCount() - a) / cv2.getTickFrequency()))
            fps = cv2.getTickFrequency() / (cv2.getTickCount() - start)
            print('FPS: ' + str(fps))
            start = cv2.getTickCount()

data = json.dumps({'command': 'clearall'}) + '\n'
s.sendall(data.encode('utf-8'))
s.close()
