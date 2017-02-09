#!/usr/bin/env python

import logging
import numpy as np
import sys
import time
import zwoasi as asi


__author__ = 'Steve Marple'
__version__ = '0.0.20'
__license__ = 'MIT'


logging.basicConfig(level='DEBUG')
logger = logging.getLogger(__name__)

num_cameras = asi.get_num_cameras()
if num_cameras == 0:
    print('No cameras found')
    sys.exit(0)

cameras_found = asi.list_cameras()  # Models names of the connected cameras

if num_cameras == 1:
    camera_id = 0
    print('Found one camera: %s' % cameras_found[0])
else:
    print('Found %d cameras' % num_cameras)
    for n in range(num_cameras):
        print('    %d: %s' % (n, cameras_found[n]))
    # TO DO: allow user to select a camera
    camera_id = 0
    print('Using #%d: %s' % (camera_id, cameras_found[camera_id]))

camera = asi.Camera(camera_id)
camera_info = camera.get_camera_property()

# Enable auto-exposure and white balance for convenience
camera.auto_exposure()
camera.auto_wb()

# Auto-exposure/wb requires video captures
camera.start_video_capture()

if camera_info['IsColorCam']:
    camera.set_image_type(asi.ASI_IMG_RGB24)
    # Use mono binning
    #camera.set_image_type(asi.ASI_IMG_RAW8)
    #camera.set_control_value(asi.ASI_MONO_BIN, 1)
else:
    camera.set_image_type(asi.ASI_IMG_RAW8)



camera.capture_video_frame(filename='bin1.jpg')

cam_info = camera.get_camera_property()
for b in (1, 2): # cam_info['SupportedBins']:
    print('Testing binning=%d' % b)
    camera.set_roi(bins=b)
    camera.capture_video_frame(filename='bins_%d.jpg' % b, timeout=10000)
