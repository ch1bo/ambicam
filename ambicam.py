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
res = np.load('res.npy')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
with picamera.PiCamera(resolution=RESOLUTION, framerate=FRAMERATE) as camera:
    with picamera.array.PiRGBArray(camera, size=RESOLUTION) as raw:
        time.sleep(2)
        start = cv2.getTickCount()
        for frame in camera.capture_continuous(raw, format="bgr", use_video_port=True):
            width = res[0]
            height = res[1]
            offset = 5
            warped = cv2.warpPerspective(frame.array, M, (width,height))
            # TODO use configured areas from hypercon
            colors = []
            # bottom center -> bottom left
            for i in range(19):
                col = int((width/2)-i*(width/2-offset)/19)
                colors.append(int(warped[width-2*offset][col][2])) # r
                colors.append(int(warped[width-2*offset][col][1])) # g
                colors.append(int(warped[width-2*offset][col][0])) # b
            # bottom left -> top left
            for i in range(20):
                row = int((height-offset)-i*(height-2*offset)/20)
                colors.append(int(warped[row][offset][2])) # r
                colors.append(int(warped[row][offset][1])) # g
                colors.append(int(warped[row][offset][0])) # b
            # top left -> top right
            for i in range(36):
                col = int(offset+i*(width-2*offset)/36)
                colors.append(int(warped[offset][col][2])) # r
                colors.append(int(warped[offset][col][1])) # g
                colors.append(int(warped[offset][col][0])) # b
            # top left -> bottom left
            for i in range(20):
                row = int(offset+i*(height-2*offset)/20)
                colors.append(int(warped[row][offset][2])) # r
                colors.append(int(warped[row][offset][1])) # g
                colors.append(int(warped[row][offset][0])) # b
            # bottom right -> bottom center
            for i in range(17):
                col = int((width-offset)-i*(width/2-offset)/17)
                colors.append(int(warped[width-2*offset][col][2])) # r
                colors.append(int(warped[width-2*offset][col][1])) # g
                colors.append(int(warped[width-2*offset][col][0])) # b
            # rgb = cv2.cvtColor(warped, cv2.COLOR_BGR2RGB)
            print('converted: ' + str((cv2.getTickCount() - start) / cv2.getTickFrequency()))
            data = (json.dumps({
                'command': 'color',
                'priority': PRIORITY,
                'color': colors
            }) + '\n').encode('utf-8')
            print('encoded: ' + str((cv2.getTickCount() - start) / cv2.getTickFrequency()))
            a = cv2.getTickCount()
            print(len(data))
            s.send(data)
            print('sent: ' + str((cv2.getTickCount() - a) / cv2.getTickFrequency()))
            raw.seek(0)
            fps = cv2.getTickFrequency() / (cv2.getTickCount() - start)
            print('FPS: ' + str(fps))
            start = cv2.getTickCount()

data = json.dumps({'command': 'clearall'}) + '\n'
s.sendall(data.encode('utf-8'))
s.close()
