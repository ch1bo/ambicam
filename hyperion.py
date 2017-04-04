import base64
import cv2
import json
import numpy as np
import socket
import sys
import time

PRIORITY = 90
HOST = '192.168.1.104'
PORT = 19444

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
img = cv2.imread('out_.bmp')
rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
data = json.dumps({
    'command': 'image',
    'priority': PRIORITY,
    'imagewidth': img.shape[1],
    'imageheight': img.shape[0],
    'imagedata': base64.b64encode(rgb.tobytes()).decode('ascii')
})
s.sendall(data.encode('utf-8') + b'\n')
s.close()
