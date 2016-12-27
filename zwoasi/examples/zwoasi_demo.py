#!/usr/bin/env python

import sys

import zwoasi as asi

num_cameras = asi.get_num_cameras()
if num_cameras == 0:
    print('No cameras found')
    sys.exit(0)

cam = asi.Camera(0)
cam_info = cam.get_camera_property()

if num_cameras == 1:
    print('Found one camera: %s' % cam_info['Name'])
else:
    print('Found %d cameras, using #0' % num_cameras)
    print('\n'.join(asi.list_cameras()))

# Set some sensible defaults. They will need adjusting depending upon
# the sensitiy, lens and lighting conditions used.

cam.set_control_value(asi.ASI_GAIN, 150)
cam.set_control_value(asi.ASI_EXPOSURE, 30000)
cam.set_control_value(asi.ASI_WB_B, 99)
cam.set_control_value(asi.ASI_WB_R, 75)
cam.set_control_value(asi.ASI_GAMMA, 50)
cam.set_control_value(asi.ASI_BRIGHTNESS, 50)
cam.set_control_value(asi.ASI_FLIP, 0)

print('Acquiring a single 8-bit mono image')
filename = 'image_mono.png'
cam.set_image_type(asi.ASI_IMG_RAW8)
img = cam.acquire(filename=filename)
print('Saved to %s' % filename)


print('Acquiring a single 16-bit mono image')
filename = 'image_mono16.png'
cam.set_image_type(asi.ASI_IMG_RAW16)
cam.acquire(filename=filename)
print('Saved to %s' % filename)

if cam_info['IsColorCam']:
    filename = 'image_color.png'
    cam.set_image_type(asi.ASI_IMG_RGB24)
    print('Acquiring a single, color image')
    cam.acquire(filename=filename)
    print('Saved to %s' % filename)
else:
    print('Color image not available with this camera')
    
