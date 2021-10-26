# Functions to cast np.ndarray to cpp pointer
import numpy as np
import ctypes

def cast_array_into_2d_pointer(input_array, pointer_type):
    y_max, x_max = input_array.shape
    input_array_lines = list()
    for input_array_line in input_array:
        IMG_LINE = (pointer_type * x_max)(*input_array_line)
        ctypes.cast(IMG_LINE, ctypes.POINTER(pointer_type))
        input_array_lines.append(IMG_LINE)
    ARRAY_POINTER = (ctypes.POINTER(pointer_type) * y_max)(*input_array_lines)
    ctypes.cast(ARRAY_POINTER, ctypes.POINTER(ctypes.POINTER(pointer_type)))
    return ARRAY_POINTER

def get_array_from_2d_pointer(input_pointer, y_max, x_max, pointer_type, array_type):
    return_array = np.zeros((y_max,x_max), dtype=array_type)
    for y_axis in range(y_max):
        for x_axis in range(x_max):
            area_id = input_pointer[y_axis][x_axis]
            return_array[y_axis, x_axis] = area_id
    return return_array