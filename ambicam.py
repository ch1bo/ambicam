import json
import numpy as np
import picamera
import picamera.array
import signal
import socket
import sys
import time
import cv2

HOST = '192.168.1.104'
PORT = 19444
PRIORITY = 90
RESOLUTION = (640,480)
FRAMERATE = 45
OFFSET = 10
M = np.load('M.npy')
width, height = np.load('res.npy')

def compute_map(M_inv, x, y, width, height):
    coords = []
    for j in range(int(y), int(y+height)):
        for i in range(int(x), int(x+width)):
            coords.append([i, j, 1])
    return np.dot(M_inv, np.array(coords).T).astype('float32')

class HyperionOutput(picamera.array.PiRGBAnalysis):
    def __init__(self, camera, M, width, height, offset=10):
        super(HyperionOutput, self).__init__(camera)
        self.M_inv = np.linalg.inv(M)
        self.width = int(width)
        self.height = int(height)
        self.offset = offset
        # Calculate source image maps
        self.top_map = compute_map(self.M_inv, 0, 0, width, offset)
        self.left_map = compute_map(self.M_inv, 0, 0, offset, height)
        self.right_map = compute_map(self.M_inv, width-offset, 0, offset, height)
        self.bottom_map = compute_map(self.M_inv, 0, height-offset, width, offset)
        # TODO cv2.convertMaps to make them fix-point -> faster?
        self.start= time.perf_counter()

    def analyze(self, img):
        capture = time.perf_counter()
        # Warp image map-by-map
        top = cv2.remap(img, self.top_map[0], self.top_map[1],
                        cv2.INTER_LINEAR).reshape(self.offset,self.width,3)
        left = cv2.remap(img, self.left_map[0], self.left_map[1],
                         cv2.INTER_LINEAR).reshape(self.height,self.offset,3)
        right = cv2.remap(img, self.right_map[0], self.right_map[1],
                          cv2.INTER_LINEAR).reshape(self.height,self.offset,3)
        bottom = cv2.remap(img, self.bottom_map[0], self.bottom_map[1],
                           cv2.INTER_LINEAR).reshape(self.offset,self.width,3)
        # TODO use means and areas from hyperion
        # Determine colors
        colors = []
        # bottom center -> bottom left
        for i in range(19):
            col = (self.width/2)-i*(self.width/2-self.offset)/19
            colors.extend(bottom[self.offset/2, col].tolist())
        # bottom left -> top left
        for i in range(20):
            row = (self.height-self.offset)-i*(self.height-2*self.offset)/20
            colors.extend(left[row, self.offset/2].tolist())
        # top left -> top right
        for i in range(36):
            col = self.offset+i*(self.width-2*self.offset)/36
            colors.extend(top[self.offset/2, col].tolist())
        # top left -> bottom left
        for i in range(20):
            row = self.offset+i*(self.height-2*self.offset)/20
            colors.extend(left[row, self.offset/2].tolist())
            # bottom right -> bottom center
        for i in range(17):
            col = (self.width-self.offset)-i*(self.width/2-self.offset)/17
            colors.extend(bottom[self.offset/2, col].tolist())
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


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

def sigint(signal, frame):
    data = json.dumps({'command': 'clearall'}) + '\n'
    s.sendall(data.encode('utf-8'))
    s.close()
    sys.exit(0)
signal.signal(signal.SIGINT, sigint)

with picamera.PiCamera(resolution=RESOLUTION, framerate=FRAMERATE) as camera:
    with HyperionOutput(camera, M, width, height, offset=OFFSET) as output:
        camera.start_recording(output, 'rgb')
        try:
            while True:
                camera.wait_recording(1)
        finally:
            camera.stop_recording()
