# Interactive preview module, run with python -i
import cv2
import numpy as np
import picamera
import picamera.array
import sys
import multiprocessing as mp

RESOLUTION = (640,480)
FRAMERATE = 5
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
        self.finished = mp.Event()
        self.M_inv = np.linalg.inv(M)
        self.width = int(width)
        self.height = int(height)
        self.offset = offset
        # Calculate source image maps
        self.top_map = compute_map(self.M_inv, 0, 0, width, offset)
        self.left_map = compute_map(self.M_inv, 0, offset, offset, height-2*offset)
        self.right_map = compute_map(self.M_inv, width-offset, offset, offset, height-2*offset)
        self.bottom_map = compute_map(self.M_inv, 0, height-offset, width, offset)
        # TODO cv2.convertMaps to make them fix-point -> faster?

    def analyze(self, img):
        # warped = cv2.warpPerspective(img, M, (width,10))
        # Warp image map-by-map
        top = cv2.remap(img, self.top_map[0], self.top_map[1],
                        cv2.INTER_LINEAR).reshape(self.offset,self.width,3)
        left = cv2.remap(img, self.left_map[0], self.left_map[1],
                         cv2.INTER_LINEAR).reshape(self.height-2*self.offset,self.offset,3)
        right = cv2.remap(img, self.right_map[0], self.right_map[1],
                          cv2.INTER_LINEAR).reshape(self.height-2*self.offset,self.offset,3)
        bottom = cv2.remap(img, self.bottom_map[0], self.bottom_map[1],
                           cv2.INTER_LINEAR).reshape(self.offset,self.width,3)
        # Stitch and preview
        cv2.imshow('original', img)
        warped = np.zeros((self.height, self.width, 3), dtype='uint8')
        warped[:self.offset,:] += top
        warped[self.offset:-self.offset,:self.offset] += left
        warped[self.offset:-self.offset,self.width-self.offset:] += right
        warped[self.height-self.offset:,:] += bottom
        cv2.imshow('warped', warped)
        if cv2.waitKey(100) & 0xFF == ord("q"):
            self.finished.set()

def settings(camera):
    print('analog_gain: ', camera.analog_gain)
    print('awb_mode: ', camera.awb_mode)
    print('awb_gains: ', camera.awb_gains)
    print('brightness: ', camera.brightness)
    print('contrast: ', camera.contrast)
    print('digital_gain: ', camera.digital_gain)
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


with picamera.PiCamera(resolution=RESOLUTION, framerate=FRAMERATE) as camera:
    settings(camera)
    with HyperionOutput(camera, M, width, height, offset=OFFSET) as output:
        camera.start_recording(output, 'bgr')
        while not output.finished.wait(100):
            pass
        camera.stop_recording()
