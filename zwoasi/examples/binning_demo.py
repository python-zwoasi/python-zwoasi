#!/usr/bin/env python

import argparse
import logging
import os
import sys
import zwoasi as asi


__author__ = 'Steve Marple'
__version__ = '0.0.22'
__license__ = 'MIT'


logging.basicConfig(level='DEBUG')
logger = logging.getLogger(__name__)

env_filename = os.getenv('ZWO_ASI_LIB')

parser = argparse.ArgumentParser(description='Process and save images from a camera')
parser.add_argument('filename',
                    nargs='?',
                    help='SDK library filename')
args = parser.parse_args()

# Initialize zwoasi with the name of the SDK library
if args.filename:
    asi.init(args.filename)
elif env_filename:
    asi.init(env_filename)
else:
    print('The filename of the SDK library is required (or set ZWO_ASI_LIB environment variable with the filename)')
    sys.exit(1)

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
    # camera.set_image_type(asi.ASI_IMG_RAW8)
    # camera.set_control_value(asi.ASI_MONO_BIN, 1)
else:
    camera.set_image_type(asi.ASI_IMG_RAW8)

camera.capture_video_frame(filename='bin1.jpg')

cam_info = camera.get_camera_property()
for b in (1, 2):  # cam_info['SupportedBins']:
    print('Testing binning=%d' % b)
    camera.set_roi(bins=b)
    camera.capture_video_frame(filename='bins_%d.jpg' % b, timeout=10000)
