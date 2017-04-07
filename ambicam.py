import json
import numpy as np
import picamera
import picamera.array
import signal
import socket
import sys
import time

PRIORITY = 90
HOST = '192.168.1.104'
PORT = 19444
RESOLUTION = (640,480)
FRAMERATE = 30
M = np.load('M.npy')
M_ = np.linalg.inv(M)
res = np.load('res.npy')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

def sigint(signal, frame):
    data = json.dumps({'command': 'clearall'}) + '\n'
    s.sendall(data.encode('utf-8'))
    s.close()
signal.signal(signal.SIGINT, sigint)

class HyperionOutput(picamera.array.PiRGBAnalysis):
    def __init__(self, camera):
        super(HyperionOutput, self).__init__(camera)
        self.start = time.perf_counter()

    def analyze(self, img):
        capture = time.perf_counter()
        print('capture:', capture - self.start)
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
        print('FPS: ', 1 / (time.perf_counter() - self.start))
        print('analog_gain: ', camera.analog_gain)
        print('digital_gain: ', camera.digital_gain)
        print('awb_gains: ', camera.awb_gains)
        self.start = time.perf_counter()

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
    with HyperionOutput(camera) as output:
        camera.start_recording(output, 'rgb')
        try:
            while True:
                camera.wait_recording(1)
        finally:
            camera.stop_recording()
