#!/usr/bin/env python

import sys
import time
import zwoasi as asi

num_cameras = asi.get_num_cameras()
if num_cameras == 0:
    print('No cameras found')
    sys.exit(0)


camera_id = 0
camera = asi.Camera(camera_id)
camera_info = camera.get_camera_property()

if num_cameras == 1:
    print('Found one camera: %s' % camera_info['Name'])
else:
    camera_id = 0
    print('Found %d cameras' % num_cameras)
    print('\n'.join(asi.list_cameras()))
    print('Using #%d: %s' % (camera_id, camera_info['Name']))


# Get all of the camera controls
print('')
print('Camera controls:')
controls = camera.get_controls()
for cn in sorted(controls.keys()):
    print('    %s:' % cn)
    for k in sorted(controls[cn].keys()):
        print('        %s: %s' % (k, repr(controls[cn][k])))


# Set some sensible defaults. They will need adjusting depending upon
# the sensitivity, lens and lighting conditions used.
camera.disable_dark_subtract()

camera.set_control_value(asi.ASI_GAIN, 150)
camera.set_control_value(asi.ASI_EXPOSURE, 30000)
camera.set_control_value(asi.ASI_WB_B, 99)
camera.set_control_value(asi.ASI_WB_R, 75)
camera.set_control_value(asi.ASI_GAMMA, 50)
camera.set_control_value(asi.ASI_BRIGHTNESS, 50)
camera.set_control_value(asi.ASI_FLIP, 0)

print('Capturing a single 8-bit mono image')
filename = 'image_mono.png'
camera.set_image_type(asi.ASI_IMG_RAW8)
img = camera.capture(filename=filename)
print('Saved to %s' % filename)


print('Capturing a single 16-bit mono image')
filename = 'image_mono16.png'
camera.set_image_type(asi.ASI_IMG_RAW16)
camera.capture(filename=filename)
print('Saved to %s' % filename)

if camera_info['IsColorCam']:
    filename = 'image_color.png'
    camera.set_image_type(asi.ASI_IMG_RGB24)
    print('Capturing a single, color image')
    camera.capture(filename=filename)
    print('Saved to %s' % filename)
else:
    print('Color image not available with this camera')
    


# Enable video mode
try:
    # Force any signle exposure to be halted
    camera.stop_exposure()
except:
    pass

print('Enabling video mode')
camera.start_video_capture()
camera.default_timeout = 2000
# Can autoexposure be used?
k = 'Exposure'
if k in controls and controls[k]['IsAutoSupported']:
    print('Enabling auto-exposure mode')
    camera.set_control_value(asi.ASI_GAIN,
                             controls['Gain']['MinValue'],
                             auto=True)
    camera.set_control_value(asi.ASI_EXPOSURE,
                             controls['Exposure']['MinValue'],
                             auto=True)

    print('Sleeping to let auto-exposure compute correct settings')
    time.sleep(2)
    
print('Capturing a single 8-bit mono frame')
filename = 'image_video_mono.png'
camera.set_image_type(asi.ASI_IMG_RAW8)
camera.capture_video_frame(filename=filename)
print('Saved to %s' % filename)

print('Capturing a single 16-bit mono frame')
filename = 'image_video_mono16.png'
camera.set_image_type(asi.ASI_IMG_RAW16)
camera.capture_video_frame(filename=filename)
print('Saved to %s' % filename)

if camera_info['IsColorCam']:
    print('Capturing a single, color image')
    filename = 'image_video_color.png'
    camera.set_image_type(asi.ASI_IMG_RGB24)
    camera.capture_video_frame(filename=filename)
    print('Saved to %s' % filename)
else:
    print('Color image not available with this camera')



    

