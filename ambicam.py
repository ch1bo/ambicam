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
FRAMERATE = 20
M = np.load('M.npy')
M_ = np.linalg.inv(M)
res = np.load('res.npy')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
with picamera.PiCamera(resolution=RESOLUTION, framerate=FRAMERATE) as camera:
    camera.video_denoise = False
    print('awb_mode: ', camera.awb_mode)
    print('brightness: ', camera.brightness)
    print('contrast: ', camera.contrast)
    print('exposure_mode: ', camera.exposure_mode)
    print('exposure_speed: ', camera.exposure_speed)
    print('iso: ', camera.iso)
    print('saturation: ', camera.saturation)
    print('sensor_mode: ', camera.sensor_mode)
    print('sharpness: ', camera.sharpness)
    print('shutter_speed: ', camera.shutter_speed)
    print('video_denoise: ', camera.video_denoise)
    print('video_stabilization: ', camera.video_stabilization)
    print('zoom: ', camera.zoom)
    with picamera.array.PiRGBArray(camera, size=RESOLUTION) as raw:
        time.sleep(2)
        start = time.perf_counter()
        for frame in camera.capture_continuous(raw, format="rgb", use_video_port=True):
            img = frame.array
            raw.seek(0)
            capture = time.perf_counter()
            print('capture:', capture - start)
            # TODO use configured areas from hypercon
            width = res[0]
            height = res[1]
            offset = 5
            # Determine dst coordinates
            dst = []
            # bottom center -> bottom left
            for i in range(19):
                col = (width/2)-i*(width/2-offset)/19
                dst.append([col, height-offset, 1])
            # bottom left -> top left
            for i in range(20):
                row = (height-offset)-i*(height-2*offset)/20
                dst.append([offset, row, 1])
            # top left -> top right
            for i in range(36):
                col = offset+i*(width-2*offset)/36
                dst.append([col, offset, 1])
            # top left -> bottom left
            for i in range(20):
                row = offset+i*(height-2*offset)/20
                dst.append([offset, row, 1])
            # bottom right -> bottom center
            for i in range(17):
                col = (width-offset)-i*(width/2-offset)/17
                dst.append([col, height-offset, 1])
            # Convert to src coordinates and extract colors
            src = np.dot(M_, np.array(dst).T).T
            colors = []
            for x, y, _ in src:
                colors.extend(img[y][x].tolist())
            warp = time.perf_counter()
            print('warp:', warp - capture)
            data = (json.dumps({
                'command': 'color',
                'priority': PRIORITY,
                'color': colors
            }) + '\n').encode('utf-8')
            s.send(data)
            print('FPS: ', 1 / (time.perf_counter() - start))
            print('analog_gain: ', camera.analog_gain)
            print('digital_gain: ', camera.digital_gain)
            print('awb_gains: ', camera.awb_gains)
            start = time.perf_counter()

data = json.dumps({'command': 'clearall'}) + '\n'
s.sendall(data.encode('utf-8'))
s.close()
