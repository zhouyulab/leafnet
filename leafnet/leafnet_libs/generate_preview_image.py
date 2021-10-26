import numpy as np
import math
from PIL import Image
from skimage import draw

def partition_colorizer(partition_array:np.ndarray) -> np.ndarray:
    '''
    args:
        partition_array - Input array with pixel-wise area label.
    return:
        Image using different colors to represent seperate areas (8-bit RGB).
    '''
    
    partition_list = np.unique(partition_array)
    partition_count = partition_list.shape[0]
    adj_table = np.zeros((partition_count, partition_count), dtype = bool)
    
    adj_table_dict = dict()
    adj_table_reverse_dict = dict()
    part_count = 0
    for item in partition_list:
        adj_table_dict[item] = part_count
        adj_table_reverse_dict[part_count] = item
        part_count += 1

    y_axis, x_axis = partition_array.shape
    
    array_list = list()
    for i in range(y_axis - 1):
        array_list.append(np.unique(np.concatenate((partition_array[i,:][:, np.newaxis],partition_array[i+1,:][:, np.newaxis]), axis = 1), axis = 0))
    for j in range(x_axis - 1):
        array_list.append(np.unique(np.concatenate((partition_array[:,j][:, np.newaxis],partition_array[:,j+1][:, np.newaxis]), axis = 1), axis = 0))
    adj_unique = np.unique(np.concatenate(array_list, axis = 0), axis = 0)

    for adj in adj_unique:
        area_0 = adj_table_dict[adj[0]]
        area_1 = adj_table_dict[adj[1]]
        adj_table[area_0, area_1] = True
        adj_table[area_1, area_0] = True

    color_dict = dict()
    total_color_count = 0
    for i in range(partition_count):
        adjust_colors = set()
        # parts already colorized:[0:i]
        for j in range(i):
            if adj_table[i,j]:
                adjust_colors.add(color_dict[j])
        # if some color is not used
        for color_index in range(total_color_count):
            if color_index not in adjust_colors:
                color_dict[i] = color_index
                break
        # if all colors are used
        else:
            color_dict[i] = total_color_count
            total_color_count += 1

    if total_color_count <= 22:
        rgb_index = [[31,120,180],[51,160,44],[251,154,153],[227,26,28],[255,127,0],[106,61,154],[177,89,40],[141,211,199],[255,255,179],[190,186,218],[251,128,114],[128,177,211],[253,180,98],[179,222,105],[252,205,229],[217,217,217],[188,128,189],[204,235,197],[255,237,111],[178,223,138],[253,191,111],[255,255,153],]
    else:
        color_distance = 192 // math.ceil(total_color_count**(0.33))
        rgb_index = list()

        for r in range(32, 225, color_distance):
            for g in range(32, 225, color_distance):
                for b in range(32, 128, color_distance):
                    rgb_index.append([r,g,b])


    rgb_mapping_dict = dict()
    for item in partition_list:
        rgb_mapping_dict[item] = rgb_index[color_dict[adj_table_dict[item]]]
    rgb_mapping_dict[0] = [255,255,255]
    rgb_mapping_dict[1] = [0,0,0]

    colorized_image = np.zeros((y_axis, x_axis, 3))

    for i in range(y_axis):
        for j in range(x_axis):
            colorized_image[i, j] = rgb_mapping_dict[partition_array[i,j]]

    return colorized_image

def generate_preview_image(raw_image:np.ndarray, area_coverage_array:np.ndarray, corrected_stoma_list:list)->np.ndarray:
    '''
    args:
        raw_image - Source image for visualization.
        area_coverage_array - Input array with pixel-wise area label.
        corrected_stoma_list - Input list containing labeled stomata, stomata is represented as [center_r, center_c, length, width, angle]
    return:
        Image using transparent colors to represent seperate areas on the original input image (8-bit RGB).
    '''
    
    __BORDER_SIZE = 50
    __BORDER_WIDTH = 3
    # Generate Preview Image
    preview_image = partition_colorizer(area_coverage_array)
    for stoma in corrected_stoma_list:
        rr, cc = draw.ellipse(stoma[0], stoma[1], stoma[2], stoma[3], rotation=-stoma[4])
        draw.set_color(preview_image,[rr,cc],[0,0,255])
    
    raw_image_rgb = np.array(Image.fromarray(raw_image).convert('RGB'))
    img_y_size, img_x_size = raw_image_rgb.shape[0], raw_image_rgb.shape[1]
    preview_image = ((preview_image.astype(float)*0.5) + (raw_image_rgb.astype(float)*0.5)).astype(np.uint8)
    # Draw Border Lines
    line_start = __BORDER_SIZE - (__BORDER_WIDTH//2)
    line_end = line_start + __BORDER_WIDTH
    for i in range(line_start, line_end):
        rr, cc = draw.rectangle_perimeter(
            (i, i), (img_y_size-i, img_x_size-i), )
        draw.set_color(preview_image, [rr, cc], [255, 0, 0])
    return preview_image