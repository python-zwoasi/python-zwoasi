#!/usr/bin/env python

import sys
import time
import zwoasi as asi

def save_control_values(filename, settings):
    with open(filename + '.txt', 'w') as f:
        for k in sorted(settings.keys()):
            f.write('%s: %s\n' % (k, str(settings[k])))
    print('Camera settings saved to %s' % filename)


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
        print('    %d: %s' % (n, cameras[n]))
    # TO DO: allow user to select a camera
    camera_id = 0
    print('Using #%d: %s' % (camera_id, cameras_found[camera_id]))

camera = asi.Camera(camera_id)
camera_info = camera.get_camera_property()

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
camera.capture(filename=filename)
print('Saved to %s' % filename)
save_control_values(filename, camera.get_control_values())


print('Capturing a single 16-bit mono image')
filename = 'image_mono16.png'
camera.set_image_type(asi.ASI_IMG_RAW16)
camera.capture(filename=filename)
print('Saved to %s' % filename)
save_control_values(filename, camera.get_control_values())

if camera_info['IsColorCam']:
    filename = 'image_color.png'
    camera.set_image_type(asi.ASI_IMG_RGB24)
    print('Capturing a single, color image')
    camera.capture(filename=filename)
    print('Saved to %s' % filename)
    save_control_values(filename, camera.get_control_values())
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
save_control_values(filename, camera.get_control_values())


print('Capturing a single 16-bit mono frame')
filename = 'image_video_mono16.png'
camera.set_image_type(asi.ASI_IMG_RAW16)
camera.capture_video_frame(filename=filename)
print('Saved to %s' % filename)
save_control_values(filename, camera.get_control_values())

if camera_info['IsColorCam']:
    print('Capturing a single, color image')
    filename = 'image_video_color.png'
    camera.set_image_type(asi.ASI_IMG_RGB24)
    camera.capture_video_frame(filename=filename)
    save_control_values(filename, camera.get_control_values())
    print('Saved to %s' % filename)
    
else:
    print('Color image not available with this camera')



    

