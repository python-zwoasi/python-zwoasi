#!/usr/bin/env python

"""Interface to ZWO ASI range of USB cameras."""

__author__ = 'Steve Marple'
__version__ = '0.0.5'
__license__ = 'PSF'

import ctypes as c
import logging
import os
import time

import cv2
import numpy as np


def get_num_cameras():
    return zwolib.ASIGetNumOfConnectedCameras();


def _get_camera_property(id):
    prop = _ASI_CAMERA_INFO()
    r = zwolib.ASIGetCameraProperty(prop, id)
    if r:
        raise zwo_errors[r]
    return prop.get_dict()


def _open_camera(id):
    r = zwolib.ASIOpenCamera(id)
    if r:
        raise zwo_errors[r]
    return


def _init_camera(id):
    r = zwolib.ASIInitCamera(id)
    if r:
        raise zwo_errors[r]
    return
   

def _close_camera(id):
    r = zwolib.ASICloseCamera(id)
    if r:
        raise zwo_errors[r]
    return


def _get_num_controls(id):
    num = c.c_int()
    r = zwolib.ASIGetNumOfControls(id, num)
    if r:
        raise zwo_errors[r]
    return num.value


def _get_control_caps(id, control_index):
    caps = _ASI_CONTROL_CAPS()
    r = zwolib.ASIGetControlCaps(id, control_index, caps)
    if r:
        raise zwo_errors[r]
    return caps.get_dict()


def _get_control_value(id, control_type):
    value = c.c_long()
    auto = c.c_int()
    r = zwolib.ASIGetControlValue(id, control_type, value, auto)
    if r:
        raise zwo_errors[r]
    return [value.value, bool(auto.value)]


def _set_control_value(id, control_type, value, auto):
    r = zwolib.ASISetControlValue(id, control_type, value, auto)
    if r:
        raise zwo_errors[r]
    return


def _get_roi_format(id):
    roi_width = c.c_int()
    roi_height = c.c_int()
    bins = c.c_int()
    image_type = c.c_int()
    r = zwolib.ASIGetROIFormat(id, roi_width, roi_height, bins, image_type)
    if r:
        raise zwo_errors[r]
    return [roi_width.value, roi_height.value, bins.value, image_type.value]


def _set_roi_format(id, width, height, bins, image_type):
    cam_info = _get_camera_property(id)

    if width < 8:
        raise ValueError('ROI width too small')
    elif width > cam_info['MaxWidth'] / bins:
        raise ValueError('ROI width larger than binned sensor width')
    elif width % 8 != 0:
        raise ValueError('ROI width must be multiple of 8')

    if height < 2:
        raise ValueError('ROI height too small')
    elif height > cam_info['MaxHeight'] / bins:
        raise ValueError('ROI width larger than binned sensor height')
    elif height % 2 != 0:
        raise ValueError('ROI height must be multiple of 2')

    if (cam_info['Name'] in ['ZWO ASI120MM', 'ZWO ASI120MC']
        and (width * height) % 1024 != 0):
        raise ValueError('ROI width * height must be multiple of 1024 for ' +
                         cam_info['Name'])
    r = zwolib.ASISetROIFormat(id, width, height, bins, image_type)
    if r:
        raise zwo_errors[r]
    return


def _get_start_position(id):
    start_x = c.c_int()
    start_y = c.c_int()
    r = zwolib.ASIGetStartPos(id, start_x, start_y)
    if r:
        raise zwo_errors[r]
    return [start_x.value, start_y.value]


def _set_start_position(id, start_x, start_y):
    if start_x < 0:
        raise ValueError('x start position too small')
    if start_y < 0:
        raise ValueError('y start position too small')

    r = zwolib.ASISetStartPos(id, start_x, start_y)
    if r:
        raise zwo_errors[r]
    return


def _get_dropped_frames(id):
    dropped_frames = c.c_int()
    r = zwo_errors.ASIGetDroppedFrames(id, dropped_frames)
    if r:
        raise zwo_errors[r]
    return dropped_frames.value

    
def _enable_dark_subtract(id, filename):
    r = zwolib.ASIEnableDarkSubtract(id, filename)
    if r:
        raise zwo_errors[r]
    return


def _disable_dark_subtract(id):
    r = zwolib.ASIDisableDarkSubtract(id)
    if r:
        raise zwo_errors[r]
    return
    

def _start_video_capture(id):
    r = zwolib.ASIStartVideoCapture(id)
    if r:
        raise zwo_errors[r]
    return
    

def _stop_video_capture(id):
    r = zwolib.ASIStopVideoCapture(id)
    if r:
        raise zwo_errors[r]
    return


def _get_video_data(id, timeout, buffer=None):
    if buffer is None:
        whbi = _get_roi_format(id)
        sz = whbi[0] * whbi[1]
        if whbi[3] == ASI_IMG_RGB24:
            sz *= 3
        elif whbi[3] == ASI_IMG_RAW16:
            sz *= 2
        buffer = bytearray(sz)
    else:
        if not isinstance(buffer, bytearray):
            raise TypeError('supplied buffer must be a bytearray')
        sz = len(buffer)
    
    cbuf_type = c.c_char * len(buffer)
    cbuf = cbuf_type.from_buffer(buffer)
    r = zwolib.ASIGetVideoData(id, cbuf, sz, timeout)
    
    if r:
        raise zwo_errors[r]
    return buffer


def _pulse_guide_on(id, direction):
    r = zwolib.ASIPulseGuideOn(id, direction)
    if r:
        raise zwo_errors[r]
    return


def _pulse_guide_off(id, direction):
    r = zwolib.ASIPulseGuideOff(id, direction)
    if r:
        raise zwo_errors[r]
    return


def _start_exposure(id, is_dark):
    r = zwolib.ASIStartExposure(id, is_dark)
    if r:
        raise zwo_errors[r]
    return


def _stop_exposure(id):
    r = zwolib.ASIStopExposure(id)
    if r:
        raise zwo_errors[r]
    return


def _get_exposure_status(id):
    status = c.c_int()
    r = zwolib.ASIGetExpStatus(id, status)
    if r:
        raise zwo_errors[r]
    return status.value


def _get_data_after_exposure(id, buffer=None):
    if buffer is None:
        whbi = _get_roi_format(id)
        sz = whbi[0] * whbi[1]
        if whbi[3] == ASI_IMG_RGB24:
            sz *= 3
        elif whbi[3] == ASI_IMG_RAW16:
            sz *= 2
        buffer = bytearray(sz)
    else:
        if not isinstance(buffer, bytearray):
            raise TypeError('supplied buffer must be a bytearray')
        sz = len(buffer)
    
    cbuf_type = c.c_char * len(buffer)
    cbuf = cbuf_type.from_buffer(buffer)
    r = zwolib.ASIGetDataAfterExp(id, cbuf, sz)
    
    if r:
        raise zwo_errors[r]
    return buffer


def _get_id(id):
    id2 = _ASI_ID()
    r = zwolib.ASIGetID(id, id2)
    if r:
        raise zwo_errors[r]
    return id2.get_id()

# TO DO: need to confirm correct function call parameters
#def _set_id(id, id_str):
#     pass


def _get_gain_offset(id):
    offset_highest_DR = c.c_int()
    offset_unity_gain = c.c_int()
    gain_lowest_RN = c.c_int()
    offset_lowest_RN = c.c_int()
    r = zwolib.ASIGetGainOffset(id, offset_highest_DR, offset_unity_gain,
                                gain_lowest_RN, offset_lowest_RN)
    if r:
        raise zwo_errors[r]
    return [offset_highest_DR.value, offset_unity_gain.value,
            gain_lowest_RN.value, offset_lowest_RN.value]


def list_cameras():
    r = []
    for id in range(get_num_cameras()):
        prop = _get_camera_property(id)
        r.append('Camera #%d: %s' % (id, prop['Name']))
    return r


class ZWO_Exception(Exception):
    pass
    

class Camera(object):
    def __init__(self,
                 id=None):
        if not isinstance(id, int):
            raise TypeError('id must be an integer')
        elif id >= get_num_cameras() or id < 0:
            raise IndexError('invalid id')
        self.id = id
        self.default_timeout = 2000
        try:
            _open_camera(id)
            self.closed = False

            _init_camera(id)
        except:
            self.closed = True
            _close_camera(id)
        
    def get_camera_property(self):
        return _get_camera_property(self.id)

    def get_num_controls(self):
        return _get_num_controls(self.id)

    def get_controls(self):
        r = {}
        for i in range(self.get_num_controls()):
            d = _get_control_caps(self.id, i)
            r[d['Name']] = d
        return r

    def set_controls(self):
        pass

    def get_roi_format(self):
        return _get_roi_format(self.id)

    def set_roi_format(self, width, height, bins, image_type):
        _set_roi_format(self.id, width, height, bins, image_type)

    def get_roi_start_position(self):
        return _get_start_position(self.id)
        
    def set_roi_start_position(self, start_x, start_y):
        _set_start_position(self.id, start_x, start_y)

    def get_dropped_frames(self):
        return _get_dropped_frames(self.id)
         
    def close(self):
        try:
            _close_camera(self.id)
        finally:
            self.is_closed = True

    def get_roi(self):
        xywh = self.get_roi_start_position()
        whbi = self.get_roi_format()
        xywh.extend(whbi[0:2])
        return xywh

    def set_roi(self, start_x=None, start_y=None, width=None, height=None, bins=None, image_type=None):
        xy = self.get_roi_start_position()
        whbi = self.get_roi_format()

        if bins is None:
            bins = whbi[2]

        if image_type is None:
            image_type = whbi[3]
            
        if width is None:
            width = cam_info['MaxWidth'] / bins

        if height is None:
            height = cam_info['MaxHeight'] / bins

        if start_x is None:
            start_x = (cam_info['MaxWidth'] - width) / 2
        if start_x + width > cam_info['MaxWidth'] / 2:
            raise ValueError('ROI and start position larger than binned sensor width')
        if start_y is None:
            start_y = (cam_info['MaxHeight'] - height) / 2
        if start_y + height > cam_info['MaxHeight'] / 2:
            raise ValueError('ROI and start position larger than binned sensor height')

        self.set_roi_format(width, height, bins, image_type)
        self.set_roi_start_position(start_x, start_y)
                

    def get_control_value(self, control_type):
        return _get_control_value(self.id, control_type)

    def set_control_value(self, control_type, value, auto=False):
        _set_control_value(self.id, control_type, value, auto)
    
    def get_bin(self):
        return self.get_roi_format()[2]

    def start_exposure(self, is_dark=False):
        _start_exposure(self.id, is_dark)

    def stop_exposure(self, is_dark=False):
        _stop_exposure(self.id, is_dark)
        
    def get_exposure_status(self):
        return _get_exposure_status(self.id)

    def get_data_after_exposure(self, buffer=None):
        return _get_data_after_exposure(self.id, buffer)

    def enable_dark_subtract(self, filename):
        _enable_dark_subtract(self.id, filename)

    def disable_dark_subtract(self):
        _disable_dark_subtract(self.id)
        
    def start_video_capture(self):
        return _start_video_capture(self.id)
    
    def stop_video_capture(self):
        return _stop_video_capture(self.id)

    def get_video_data(self, timeout=None, buffer=None):
        if timeout is None:
            timeout = self.default_timeout
        return _get_video_data(self.id, timeout, buffer)

    def pulse_guide_on(self, direction):
        _pulse_guide_on(self.id, direction)
        return
    
    def pulse_guide_off(self, direction):
        _pulse_guide_off(self.id, direction)
        return

    def get_id(self):
        return _get_id(self.id)
    
    # Helper functions
    def get_image_type(self):
        return self.get_roi_format()[3]

    def set_image_type(self, image_type):
         whbi = self.get_roi_format()
         whbi[3] = image_type
         self.set_roi_format(*whbi)
         # self.set_roi_format(whbi[0], whbi[1], whbi[2], whbi[3])


    def capture(self, initial_sleep=0.01, poll=0.01, buffer=None,
                filename=None):
        self.start_exposure()
        if initial_sleep:
            time.sleep(initial_sleep)
        while self.get_exposure_status() == ASI_EXP_WORKING:
            if poll:
                time.sleep(poll)
            pass

        data = self.get_data_after_exposure(buffer)
        whbi = self.get_roi_format()
        shape = [whbi[1], whbi[0]]
        if whbi[3] == ASI_IMG_RAW8 or whbi[3] == ASI_IMG_Y8:
            img = np.frombuffer(data, dtype=np.uint8)
        elif whbi[3] == ASI_IMG_RAW16:
            img = np.frombuffer(data, dtype=np.uint16)
        elif whbi[3] == ASI_IMG_RGB24:
            img = np.frombuffer(data, dtype=np.uint8)
            shape.append(3)
        else:
            raise Exception('Unsupported image type')
        img = img.reshape(shape)

        if filename is not None:
            cv2.imwrite(filename, img)
            logger.debug('wrote %s', filename)
        return img
         
    '''Capture a single frame from video.

    Video mode must have been started previously.
    '''
    def capture_video_frame(self, buffer=None, filename=None, timeout=1000):
        data = self.get_video_data(buffer=buffer, timeout=timeout)
        
        whbi = self.get_roi_format()
        shape = [whbi[1], whbi[0]]
        if whbi[3] == ASI_IMG_RAW8 or whbi[3] == ASI_IMG_Y8:
            img = np.frombuffer(data, dtype=np.uint8)
        elif whbi[3] == ASI_IMG_RAW16:
            img = np.frombuffer(data, dtype=np.uint16)
        elif whbi[3] == ASI_IMG_RGB24:
            img = np.frombuffer(data, dtype=np.uint8)
            shape.append(3)
        else:
            raise Exception('Unsupported image type')
        img = img.reshape(shape)

        if filename is not None:
            cv2.imwrite(filename, img)
            logger.debug('wrote %s', filename)
        return img
        
   
class _ASI_CAMERA_INFO(c.Structure):
    _fields_ = [
        ('Name', c.c_char * 64),
        ('CameraID', c.c_int),
        ('MaxHeight', c.c_long),
        ('MaxWidth', c.c_long),
        ('IsColorCam', c.c_int),
        ('BayerPattern', c.c_int),
        ('SupportedBins', c.c_int * 16),
        ('SupportedVideoFormat', c.c_int * 8),
        ('PixelSize', c.c_double), # in um
        ('MechanicalShutter', c.c_int),
        ('ST4Port', c.c_int),
        ('IsCoolerCam', c.c_int),
        ('IsUSB3Host', c.c_int),
        ('IsUSB3Camera', c.c_int),
        ('ElecPerADU', c.c_float),
        ('Unused', c.c_char * 24),
    ]
    
    def get_dict(self):
        r = {}
        for k, _ in self._fields_:
            r[k] = getattr(self, k)
        del r['Unused']
        
        r['SupportedBins'] = []
        for i in range(len(self.SupportedBins)):
            if self.SupportedBins[i]:
                r['SupportedBins'].append(self.SupportedBins[i])
            else:
                break
        r['SupportedVideoFormat'] = []
        for i in range(len(self.SupportedVideoFormat)):
            if self.SupportedVideoFormat[i] == ASI_IMG_END:
                break;
            r['SupportedVideoFormat'].append(self.SupportedVideoFormat[i])

        for k in ('IsColorCam', 'MechanicalShutter', 'IsCoolerCam',
                  'IsUSB3Host', 'IsUSB3Camera'):
            r[k] = bool(getattr(self, k))
        return r


class _ASI_CONTROL_CAPS(c.Structure):
    _fields_ = [
        ('Name', c.c_char * 64),
        ('Description', c.c_char * 128),
        ('MaxValue', c.c_long),
        ('MinValue', c.c_long),
        ('DefaultValue', c.c_long),
        ('IsAutoSupported', c.c_int),
        ('IsWritable', c.c_int),
        ('ControlType', c.c_int),
        ('Unused', c.c_char * 32),
        ]

    def get_dict(self):
        r = {}
        for k, _ in self._fields_:
            r[k] = getattr(self, k)
        del r['Unused']
        for k in ('IsAutoSupported', 'IsWritable'):
            r[k] = bool(getattr(self, k))
        return r


class _ASI_ID(c.Structure):
    _fields_ = [('id', c.c_char * 8)]

    def get_id(self):
        return self.id
    
logger = logging.getLogger(__name__)

# ASI_BAYER_PATTERN
ASI_BAYER_RG = 0
ASI_BAYER_BG = 1
ASI_BAYER_GR = 2
ASI_BAYER_RB = 3

# ASI_IMGTYPE
ASI_IMG_RAW8 = 0
ASI_IMG_RGB24 = 1
ASI_IMG_RAW16 = 2
ASI_IMG_Y8 = 3
ASI_IMG_END = -1

# ASI_GUIDE_DIRECTION
ASI_GUIDE_NORTH = 0
ASI_GUIDE_SOUTH = 1
ASI_GUIDE_EAST = 2
ASI_GUIDE_WEST = 3

ASI_GAIN = 0
ASI_EXPOSURE = 1
ASI_GAMMA = 2
ASI_WB_R = 3
ASI_WB_B = 4
ASI_BRIGHTNESS = 5
ASI_BANDWIDTHOVERLOAD = 6
ASI_OVERCLOCK = 7
ASI_TEMPERATURE = 8 # return 10*temperature
ASI_FLIP = 9
ASI_AUTO_MAX_GAIN = 10
ASI_AUTO_MAX_EXP = 11
ASI_AUTO_MAX_BRIGHTNESS = 12
ASI_HARDWARE_BIN = 13
ASI_HIGH_SPEED_MODE = 14
ASI_COOLER_POWER_PERC = 15
ASI_TARGET_TEMP = 16 # not need *10
ASI_COOLER_ON = 17
ASI_MONO_BIN = 18 # lead to less grid at software bin mode for color camera
ASI_FAN_ON = 19
ASI_PATTERN_ADJUST = 20

# ASI_EXPOSURE_STATUS
ASI_EXP_IDLE = 0
ASI_EXP_WORKING = 1
ASI_EXP_SUCCESS = 2
ASI_EXP_FAILED = 3

# Mapping of error numbers to exceptions. Zero is used for success.
zwo_errors = [None,
              ZWO_Exception('Invalid index'),
              ZWO_Exception('Invalid ID'),
              ZWO_Exception('Invalid control type'),
              ZWO_Exception('Camera closed'),
              ZWO_Exception('Camera removed'),
              ZWO_Exception('Invalid path'),
              ZWO_Exception('Invalid file format'),
              ZWO_Exception('Invalidbyref( size'),
              ZWO_Exception('Invalid image type'),
              ZWO_Exception('Outside of boundary'),
              ZWO_Exception('Timeout'),
              ZWO_Exception('Invalid sequence'),
              ZWO_Exception('Buffer too small'),
              ZWO_Exception('Video mode active'),
              ZWO_Exception('Exposure in progress'),
              ZWO_Exception('General error'),
              ]

zwolib_file = os.getenv('ZWO_ASI_LIB') or 'libASICamera2.so'
zwolib = c.cdll.LoadLibrary(zwolib_file)

zwolib.ASIGetNumOfConnectedCameras.argtypes = []
zwolib.ASIGetNumOfConnectedCameras.restype = c.c_int

zwolib.ASIGetCameraProperty.argtypes = [c.POINTER(_ASI_CAMERA_INFO), c.c_int]
zwolib.ASIGetCameraProperty.restype = c.c_int

zwolib.ASIOpenCamera.argtypes = [c.c_int]
zwolib.ASIOpenCamera.restype = c.c_int

zwolib.ASIInitCamera.argtypes = [c.c_int]
zwolib.ASIInitCamera.restype = c.c_int

zwolib.ASICloseCamera.argtypes = [c.c_int]
zwolib.ASICloseCamera.restype = c.c_int

zwolib.ASIGetNumOfControls.argtypes = [c.c_int, c.POINTER(c.c_int)]
zwolib.ASIGetNumOfControls.restype = c.c_int

zwolib.ASIGetControlCaps.argtypes = [c.c_int, c.c_int,
                                     c.POINTER(_ASI_CONTROL_CAPS)]
zwolib.ASIGetControlCaps.restype = c.c_int

zwolib.ASIGetControlValue.argtypes = [c.c_int,
                                      c.c_int,
                                      c.POINTER(c.c_long),
                                      c.POINTER(c.c_int)]
zwolib.ASIGetControlValue.restype = c.c_int

zwolib.ASISetControlValue.argtypes = [c.c_int, c.c_int, c.c_long, c.c_int]
zwolib.ASISetControlValue.restype = c.c_int

zwolib.ASIGetROIFormat.argtypes = [c.c_int,
                                   c.POINTER(c.c_int),
                                   c.POINTER(c.c_int),
                                   c.POINTER(c.c_int),
                                   c.POINTER(c.c_int)]
zwolib.ASIGetROIFormat.restype = c.c_int

zwolib.ASISetROIFormat.argtypes = [c.c_int, c.c_int, c.c_int, c.c_int, c.c_int]
zwolib.ASISetROIFormat.restype = c.c_int

zwolib.ASIGetStartPos.argtypes = [c.c_int,
                                  c.POINTER(c.c_int),
                                  c.POINTER(c.c_int)]
zwolib.ASIGetStartPos.restype = c.c_int

zwolib.ASISetStartPos.argtypes = [c.c_int, c.c_int, c.c_int]
zwolib.ASISetStartPos.restype = c.c_int

zwolib.ASIGetDroppedFrames.argtypes = [c.c_int, c.POINTER(c.c_int)]
zwolib.ASIGetDroppedFrames.restype = c.c_int

zwolib.ASIEnableDarkSubtract.argtypes = [c.c_int, c.POINTER(c.c_char)]
zwolib.ASIEnableDarkSubtract.restype = c.c_int

zwolib.ASIDisableDarkSubtract.argtypes = [c.c_int]
zwolib.ASIDisableDarkSubtract.restype = c.c_int

zwolib.ASIStartVideoCapture.argtypes = [c.c_int]
zwolib.ASIStartVideoCapture.restype = c.c_int

zwolib.ASIStopVideoCapture.argtypes = [c.c_int]
zwolib.ASIStopVideoCapture.restype = c.c_int

zwolib.ASIGetVideoData.argtypes = [c.c_int,
                                   c.POINTER(c.c_char),
                                   c.c_long,
                                   c.c_int]
zwolib.ASIGetVideoData.restype = c.c_int

zwolib.ASIPulseGuideOn.argtypes = [c.c_int, c.c_int]
zwolib.ASIPulseGuideOn.restype = c.c_int

zwolib.ASIPulseGuideOff.argtypes = [c.c_int, c.c_int]
zwolib.ASIPulseGuideOff.restype = c.c_int

zwolib.ASIStartExposure.argtypes = [c.c_int, c.c_int]
zwolib.ASIStartExposure.restype = c.c_int

zwolib.ASIStopExposure.argtypes = [c.c_int]
zwolib.ASIStopExposure.restype = c.c_int

zwolib.ASIGetExpStatus.argtypes = [c.c_int, c.POINTER(c.c_int)]
zwolib.ASIGetExpStatus.restype = c.c_int

zwolib.ASIGetDataAfterExp.argtypes = [c.c_int, c.POINTER(c.c_char), c.c_long]
zwolib.ASIGetDataAfterExp.restype = c.c_int

zwolib.ASIGetID.argtypes = [c.c_int, c.POINTER(_ASI_ID)]
zwolib.ASIGetID.restype = c.c_int

# Include file suggests:
# zwolib.ASISetID.argtypes = [c.c_int, _ASI_ID]
#
# Suspect it should really be
# zwolib.ASISetID.argtypes = [c.c_int, c.POINTER(_ASI_ID)]
#
# zwolib.ASISetID.restype = c.c_int
#
# Leave out support for ASISetID for now


zwolib.ASIGetGainOffset.argtypes = [c.c_int,
                                    c.POINTER(c.c_int),
                                    c.POINTER(c.c_int),
                                    c.POINTER(c.c_int),
                                    c.POINTER(c.c_int)]
zwolib.ASIGetGainOffset.restype = c.c_int
