#!/usr/bin/env python

import sys
import time
import zwoasi as asi

def save_control_values(filename, settings):
    filename += '.txt'
    with open(filename, 'w') as f:
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
filename = 'image_mono.jpg'
camera.set_image_type(asi.ASI_IMG_RAW8)
camera.capture(filename=filename)
print('Saved to %s' % filename)
save_control_values(filename, camera.get_control_values())


print('Capturing a single 16-bit mono image')
filename = 'image_mono16.jpg'
camera.set_image_type(asi.ASI_IMG_RAW16)
camera.capture(filename=filename)
print('Saved to %s' % filename)
save_control_values(filename, camera.get_control_values())

if camera_info['IsColorCam']:
    filename = 'image_color.jpg'
    camera.set_image_type(asi.ASI_IMG_RGB24)
    print('Capturing a single, color image')
    camera.capture(filename=filename)
    print('Saved to %s' % filename)
    save_control_values(filename, camera.get_control_values())
else:
    print('Color image not available with this camera')
    


# Enable video mode
try:
    # Force any single exposure to be halted
    camera.stop_exposure()
except:
    pass

print('Enabling video mode')
camera.start_video_capture()

# Restore all controls to default values
for c in controls:
    camera.set_control_value(controls[c]['ControlType'], controls[c]['DefaultValue'])

# Can autoexposure be used?
k = 'Exposure'
if 'Exposure' in controls and controls['Exposure']['IsAutoSupported']:
    print('Enabling auto-exposure mode')
    camera.set_control_value(asi.ASI_EXPOSURE,
                             controls['Exposure']['DefaultValue'],
                             auto=True)

    if 'Gain' in controls and controls['Gain']['IsAutoSupported']:
        print('Enabling automatic gain setting')
        camera.set_control_value(asi.ASI_GAIN,
                                 controls['Gain']['DefaultValue'],
                                 auto=True)

    # Keep max gain to the default but allow exposure to be increased to its maximum value if necessary
    camera.set_control_value(controls['AutoExpMaxExp']['ControlType'], controls['AutoExpMaxExp']['MaxValue'])

    print('Waiting for auto-exposure to compute correct settings ...')
    sleep_interval = 0.100
    df_last = None
    gain_last = None
    exposure_last = None
    matches = 0
    while True:
        time.sleep(sleep_interval)
        settings = camera.get_control_values()
        df = camera.get_dropped_frames()
        gain = settings['Gain']
        exposure = settings['Exposure']
        if df != df_last:
            print('   Gain {gain:d}  Exposure: {exposure:f} Dropped frames: {df:d}'.format(gain=settings['Gain'],
                                                                                        exposure=settings['Exposure'],
                                                                                        df=df))
            if gain == gain_last and exposure == exposure_last:
                matches += 1
            else:
                matches = 0
            if matches >= 5:
                break
            df_last = df
            gain_last = gain
            exposure_last = exposure

# Set the timeout, units are ms
timeout = (camera.get_control_value(asi.ASI_EXPOSURE)[0] / 1000) * 2 + 500
camera.default_timeout = timeout

if camera_info['IsColorCam']:
    print('Capturing a single color frame')
    filename = 'image_video_color.jpg'
    camera.set_image_type(asi.ASI_IMG_RGB24)
    camera.capture_video_frame(filename=filename)
else:
    print('Capturing a single 8-bit mono frame')
    filename = 'image_video_mono.jpg'
    camera.set_image_type(asi.ASI_IMG_RAW8)
    camera.capture_video_frame(filename=filename)

print('Saved to %s' % filename)
save_control_values(filename, camera.get_control_values())



    

