from tkinter.constants import TOP
from typing import Tuple
import numpy as np
from skimage.morphology import skeletonize, remove_small_objects, binary_dilation, disk, watershed
from skimage.feature import peak_local_max
from skimage import measure
from skimage import draw
from scipy import ndimage as ndi
import cv2

from .edt_lib import *

import platform, os
import ctypes

def get_binary(input_array:np.ndarray)->np.ndarray:
    '''
    Generate binary image from input uint8 image with otsu threshold.
    args:
        input_array - Input 8-bit grayscale image.
    return:
        Binary image with true for dark and false for bright.
    '''
    return cv2.threshold(cv2.medianBlur(input_array.astype(np.uint8), 5), 0,255,cv2.THRESH_OTSU)[1] < 127

class divider():
    '''
    LeafSeg pavementcell segmentator.
    '''
    def __init__(self, min_cell_size:float = 100, divider_thres:float = 40):
        '''
        args:
            min_cell_size - Minmium cell size, cells smaller than this value will be removed.
            divider_thres - Threshold for cell segmentation, smaller threshold results in more reported cells.
        '''
        # Input
        self.merge_threshold = float(divider_thres) / 100.0
        self.cell_min_size = min_cell_size

        # Load Binary Libs
        if platform.system() == "Windows":
            area_merge_dll = ctypes.CDLL(os.path.join(os.path.dirname(__file__),'edt_model.dll'))
        elif platform.system() == 'Darwin':
            area_merge_dll = ctypes.CDLL(os.path.join(os.path.dirname(__file__),'edt_model.osx.so'))
        else:
            area_merge_dll = ctypes.cdll.LoadLibrary(os.path.join(os.path.dirname(__file__),'edt_model.so'))

        self.cpp_merge_areas = area_merge_dll.merge_areas
        self.cpp_merge_areas.argtypes = [ctypes.POINTER(ctypes.POINTER(ctypes.c_int)), ctypes.POINTER(ctypes.POINTER(ctypes.c_float)), ctypes.c_int, ctypes.c_int, ctypes.c_float]
        self.cpp_merge_areas.restype = None

    # Divide Cells Using EDT Method
    def divide_cell(self, input_image:np.ndarray, stoma_list:list, stoma_map:np.ndarray = None) -> Tuple[set,np.ndarray]:
        '''
        Generate pixel-wise cell label for input image.
        args:
            input_image - Input 8-bit grayscale image
            stoma_list - Input list containing labeled stomata, stomata is represented as [center_r, center_c, length, width, angle]
            stoma_map - Optional, boolean array of pixel-wise label for stomata.
        return:
            Pixel-wise cell label.
        '''
        # mask the Stomas
        if stoma_map == None:
            stoma_map = np.zeros(input_image.shape, dtype=bool)
            for stoma in stoma_list:
                rr, cc = draw.ellipse(stoma[0], stoma[1], int(stoma[2]*1.5), int(stoma[3]*1.5), rotation=-stoma[4])
                draw.set_color(stoma_map,[rr,cc],True)

        binary_image = get_binary(input_image)

        binary_image[:4,:] = True
        binary_image[-4:,:] = True
        binary_image[:,:4] = True
        binary_image[:,-4:] = True

        binary_ske = skeletonize(binary_image)
        binary_ske = remove_small_objects(binary_ske, 64, connectivity=2)
        binary_ske = binary_dilation(binary_ske, selem=disk(4))
        binary_ske[np.where(stoma_map)] = True

        source_edt = ndi.distance_transform_edt((1-binary_ske.astype(np.uint8))*255).astype(float)
        local_maxs = peak_local_max(source_edt, indices=False, footprint=np.ones([3,3], dtype=bool))
        markers_joint = measure.label(local_maxs, connectivity=2)


        watershed_base = (255-input_image)
        watershed_base[np.where(stoma_map)] = 255
        labels_v2 = watershed(watershed_base, markers_joint)
        labels_v2[np.where(stoma_map)] =0

        binary_image_float = (binary_image).astype(float)
        binary_image_float[np.where(stoma_map)] = 1.0

        binary_image_float = cv2.blur(binary_image_float, (3,3))

        labels_v2_ptr = cast_array_into_2d_pointer(labels_v2, ctypes.c_int32)
        scores_ptr = cast_array_into_2d_pointer(binary_image_float, ctypes.c_float)

        self.cpp_merge_areas(labels_v2_ptr, scores_ptr, int(labels_v2.shape[0]), int(labels_v2.shape[1]), self.merge_threshold)

        labels_v2 = get_array_from_2d_pointer(labels_v2_ptr, int(labels_v2.shape[0]), int(labels_v2.shape[1]), ctypes.c_float, np.float)

        area_id_arr, area_size = np.unique(labels_v2, return_counts = True)

        for small_area_id in area_id_arr[np.where(area_size < self.cell_min_size) ]:
            labels_v2[np.where(labels_v2 == small_area_id)] = 0
        

        watershed_base = (255-input_image)
        watershed_base[np.where(stoma_map)] = 255
        labels_v2 = watershed(watershed_base, labels_v2)
        area_id_set = set(np.unique(labels_v2))
        return area_id_set, labels_v2