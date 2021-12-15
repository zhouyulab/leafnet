import platform
import os
import ctypes
import numpy as np
from skimage.filters import threshold_otsu
import cv2

def cast_1d_float_array_into_pointer(input_array):
    array_len = input_array.shape[0]
    C_ARRAY = (ctypes.c_float * array_len)(*input_array)
    C_POINTER = ctypes.cast(C_ARRAY, ctypes.POINTER(ctypes.c_float))
    return C_POINTER

def cast_1d_pointer_into_float_array(input_pointer, array_len):
    return (np.ctypeslib.as_array(input_pointer, shape = [array_len])).copy()

class denoiser:
    def __init__(self, denoise_level = 50):
        if platform.system() == 'Windows':
            gegl_denoise_dll = ctypes.CDLL(os.path.join(os.path.dirname(__file__),'gegl_denoise.dll'))
        elif platform.system() == 'Darwin':
            gegl_denoise_dll = ctypes.CDLL(os.path.join(os.path.dirname(__file__),'gegl_denoise.osx.so'))
        else:
            gegl_denoise_dll = ctypes.cdll.LoadLibrary(os.path.join(os.path.dirname(__file__),'gegl_denoise.so'))
            
        self.gegl_denoise = gegl_denoise_dll.gegl_denoise
        self.gegl_denoise.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.c_int, ctypes.c_int, ctypes.c_int]
        self.iteration = (denoise_level*16)//100

    def denoise(self, source_img):
        denoised_image = source_img.copy()
        r_max, c_max = denoised_image.shape
        img_gray_threshold = threshold_otsu(denoised_image)
        
        gray_mask = denoised_image.copy()
        brighter_gray_mean = 200
        gray_mask[np.where(gray_mask<=img_gray_threshold)] = brighter_gray_mean
        gray_mask = cv2.blur(gray_mask, (100,100))
        denoised_image = (denoised_image.astype(float) * brighter_gray_mean) / gray_mask.astype(float)
        denoised_image[np.where(denoised_image<0)] = 0
        denoised_image[np.where(denoised_image>255)] = 255
        denoised_image = denoised_image.astype(np.uint8)
        
        if (self.iteration>0):
            SOURCE_POINTER = cast_1d_float_array_into_pointer(denoised_image.flatten())
            self.gegl_denoise(SOURCE_POINTER, r_max, c_max, self.iteration)
            filtered_1d_array = cast_1d_pointer_into_float_array(SOURCE_POINTER, r_max*c_max)
            denoised_image = filtered_1d_array.reshape((r_max, c_max)).astype(np.uint8)

        return denoised_image