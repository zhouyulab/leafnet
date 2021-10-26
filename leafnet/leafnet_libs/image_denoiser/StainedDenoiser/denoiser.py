from __future__ import division
import numpy as np
from skimage.filters import median, gaussian
from skimage.morphology import disk
from skimage.transform import resize
import math

def min_max_with_ratio(array:np.ndarray, ratio:float)->tuple:
    sorted_arr = np.sort(array.flatten())
    arr_min = sorted_arr[int(math.floor(sorted_arr.shape[0]*ratio))]
    arr_max = sorted_arr[int(math.ceil(sorted_arr.shape[0]*(1-ratio)))]
    return (arr_min, arr_max)

def area_grayscale_normalize(input_array:np.ndarray, kernel_size:int)->np.ndarray:
    half_ks = kernel_size//2

    axis_1 = input_array.shape[0]
    axis_2 = input_array.shape[1]

    axis_1_extended = int(math.ceil((axis_1+kernel_size)/kernel_size)*kernel_size)
    axis_2_extended = int(math.ceil((axis_2+kernel_size)/kernel_size)*kernel_size)

    axis_1_pad = (half_ks, axis_1_extended - axis_1 - half_ks)
    axis_2_pad = (half_ks, axis_2_extended - axis_2 - half_ks)

    input_min, input_max = min_max_with_ratio(input_array, 0.01)
    input_array_preprocessed = (input_array.copy() - input_min) / ((input_max - input_min) + 0.000000001)
    input_array_preprocessed = np.clip(input_array_preprocessed, 0, 1)

    input_array_extended = np.pad(input_array_preprocessed.copy(), (axis_1_pad, axis_2_pad), 'reflect')

    map_axis_1 = axis_1_extended//kernel_size
    map_axis_2 = axis_2_extended//kernel_size

    delta_array = np.zeros((map_axis_1, map_axis_2), float)
    min_array = np.zeros((map_axis_1, map_axis_2), float)

    for i in range(map_axis_1):
        for j in range(map_axis_2):
            area = input_array_extended[i*kernel_size:(i+1)*kernel_size, j*kernel_size:(j+1)*kernel_size]

            min_val, max_val = min_max_with_ratio(area, 0.01)
            min_array[i,j] = min_val
            delta_array[i,j] = max_val - min_val
    
    min_array_resized = resize(min_array, (axis_1_extended, axis_2_extended), anti_aliasing=True)
    delta_array_resized = resize(delta_array, (axis_1_extended, axis_2_extended), anti_aliasing=True)
    
    input_array_extended = (input_array_extended - min_array_resized) / (delta_array_resized + 0.000000001)
    input_array_extended = np.clip(input_array_extended, 0, 1)

    return input_array_extended[half_ks:half_ks+axis_1, half_ks:half_ks+axis_2]

def mean_curvature_flow(input):
    src_buf = np.pad(input.copy(), ((1,1),(1,1)), mode='edge')
    
    center = src_buf[1:-1, 1:-1]

    left = src_buf[1:-1, 0:-2]
    right = src_buf[1:-1, 2:]
    top = src_buf[0:-2, 1:-1]
    bottom = src_buf[2:, 1:-1]

    topleft = src_buf[0:-2, 0:-2]
    topright = src_buf[0:-2, 2:]
    bottomleft = src_buf[2:, 0:-2]
    bottomright = src_buf[2:, 2:]

    dx = right-left
    dy = bottom-top

    dx2 = dx**2
    dy2 = dy**2
    magnitude = (dx2 + dy2)**0.5

    dxx = (right + left) - (2 * center)
    dyy = (bottom + top) - (2 * center)
    dxy = 0.25*(bottomright-topright-bottomleft+topleft)

    n = (dx2 * dyy) + (dy2 * dxx) - (2 * dx * dy * dxy)
    d = ((dx2 + dy2)**3)**0.5

    d_not_0 = np.where(d!=0)
    dst_buf = center.copy()
    dst_buf[d_not_0] += 0.25 * magnitude[d_not_0] * (n[d_not_0]/d[d_not_0])
    
    return dst_buf

def mean_curvature_blur(input_image, iterations):
    dst_buf = input_image.copy()
    for i in range(iterations):
        dst_buf = mean_curvature_flow(dst_buf)
    return dst_buf

def image_grayscale_normalize(image, clip_factor):
    image_normalized = image.copy()
    image_grays = np.sort(image.flatten())
    img_min = image_grays[math.floor(image_grays.shape[0]*clip_factor)]
    img_max = image_grays[math.ceil(image_grays.shape[0]*(1-clip_factor))]
    image_normalized -= img_min
    image_normalized /= (img_max - img_min)
    image_normalized = np.clip(image_normalized,0,1)
    return image_normalized

class denoiser:
    '''
    Denoiser designed for stained image.
    '''
    def __init__(self, denoise_level = 50):
        self.denoise_level = denoise_level

    def denoise(self, source_img):
        denoising_image = source_img.copy().astype(float) / 255

        denoising_image = image_grayscale_normalize(denoising_image, 0.01)

        denoising_image = median(denoising_image, selem=disk(3))

        denoising_image = denoising_image*0.5 + gaussian(1.0-denoising_image, 15)*0.5

        denoising_image = area_grayscale_normalize(denoising_image, 100)

        denoising_image = mean_curvature_blur(denoising_image, 64)

        return (denoising_image*255).astype(np.uint8)