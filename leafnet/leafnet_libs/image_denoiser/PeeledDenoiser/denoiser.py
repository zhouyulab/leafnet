import platform
import os
import ctypes
import numpy as np
from skimage.filters import threshold_otsu
import cv2
import time

class denoiser:
    '''
    Denoiser designed for peeled image.
    '''
    def __init__(self, denoise_level = 50):
        self.iteration = int((denoise_level*16)//100)

    def denoise(self, source_img:np.ndarray)->np.ndarray:
        src_buf = np.zeros((source_img.shape[0]+2, source_img.shape[1]+2), dtype=np.float32)
        center = src_buf[1:-1, 1:-1]
        offsets = [
            src_buf[0:-2, 0:-2], src_buf[0:-2, 1:-1], src_buf[0:-2, 2:],
            src_buf[1:-1, 0:-2],                      src_buf[1:-1, 2:],
            src_buf[2:, 0:-2],   src_buf[2:, 1:-1],   src_buf[2:, 2:],
        ]
        # References to decide the current smooth status
        metric_reference = list()
        axis_reference = list()
        for axis in range(4):
            metric_reference.append(np.zeros(center.shape, dtype=np.float32))
            axis_reference.append(np.zeros(center.shape, dtype=np.float32))
        # Smoothing
        sum = np.zeros(center.shape, dtype=np.float32)
        count = np.zeros(center.shape, dtype=np.int32)
        direction_value = np.zeros(center.shape, dtype=np.float32)
        direction_valid = np.zeros(center.shape, dtype=np.bool)
        directional_temp_mertric = np.zeros(center.shape, dtype=np.float32)
        directional_temp_valid = np.zeros(center.shape, dtype=np.bool)

        dst_buf = source_img.copy().astype(np.float32) / 255
        for i in range(self.iteration):
            src_buf[...] = np.pad(dst_buf, ((1,1),(1,1)), mode='edge')
            # References to decide the current smooth status
            for axis in range(4):
                np.add(offsets[axis], offsets[7-axis], out=axis_reference[axis])
                axis_reference[axis] /= 2
                np.subtract(center, axis_reference[axis], out=metric_reference[axis])
                metric_reference[axis] **= 2
            
            # Smoothing
            sum[...] = center
            count[...] = 1
            for direction in range(8):
                np.add(offsets[direction], center, out=direction_value)
                direction_value /= 2
                direction_valid[...] = True
                for axis in range(4):
                    np.subtract(direction_value, axis_reference[axis], out=directional_temp_mertric)
                    directional_temp_mertric **= 2
                    np.less_equal(directional_temp_mertric, metric_reference[axis], out=directional_temp_valid)
                    direction_valid &= directional_temp_valid

                sum[direction_valid] += direction_value[direction_valid]
                count[direction_valid] += 1
            np.divide(sum, count, out=dst_buf)
        return (dst_buf*255).astype(np.uint8)