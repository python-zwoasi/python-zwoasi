#!/usr/bin/env python

import sys

import zwoasi as asi

num_cameras = asi.get_num_cameras()
print('Num cameras: ' + str(num_cameras))
if num_cameras == 0:
    print('No cameras found')
    sys.exit(0)

asi.list_cameras()

cam = asi.Camera(0)
print(cam)
print(cam.get_roi_format())
print(cam.get_roi_start_position())
print(cam.get_control_value(asi.ASI_TEMPERATURE))

cam.set_control_value(asi.ASI_GAIN, 150)
cam.set_control_value(asi.ASI_EXPOSURE, 50000)
cam.set_control_value(asi.ASI_WB_B, 99)
cam.set_control_value(asi.ASI_WB_R, 75)
cam.set_control_value(asi.ASI_GAMMA, 50)
cam.set_control_value(asi.ASI_BRIGHTNESS, 50)
cam.set_control_value(asi.ASI_FLIP, 0)

print('===')
img = cam.acquire()
print('---')
print(len(img))

cam.set_image_type(asi.ASI_IMG_RGB24)

print('===')
img = cam.acquire()
print('---')
print(len(img))
print(cam.get_roi_format())
