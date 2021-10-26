import numpy as np
from skimage import draw
import math

# Output Statistic Data
def generate_statistics(area_coverage_array:np.ndarray, corrected_stoma_list:list, base_resolution:float)->dict:
    '''
    args:
        area_coverage_array - Input array with pixel-wise area label.
        corrected_stoma_list - Input list containing labeled stomata, stomata is represented as [center_r, center_c, length, width, angle]
        base_resolution - The resolution of the model (Images are already resized to the resolution of the model in the preprocessing step).
    return:
        Dict containing statistics information of stomata and pavement cells.
    '''
    
    image_margin = 50
    image_effective_size = ((area_coverage_array.shape[0] - (image_margin*2)) * (area_coverage_array.shape[1] - (image_margin*2)))/(base_resolution*base_resolution)
    # Count Stomata In Effective Area, Get Cell Size
    temp_area_coverage = area_coverage_array.astype(int).copy()
    stoma_id_start = np.max(area_coverage_array) + 1
    stoma_id = stoma_id_start
    stoma_dict = dict()
    stoma_count = 0
    for stoma in corrected_stoma_list:
        if stoma[0] >= image_margin and stoma[0] < area_coverage_array.shape[0]-image_margin and stoma[1] >= image_margin and stoma[1] < area_coverage_array.shape[1]-image_margin:
            stoma_dict[stoma_id] = stoma
            stoma_count += 1
        draw.set_color(temp_area_coverage,draw.ellipse(stoma[0], stoma[1], stoma[2], stoma[3], rotation=-stoma[4]),[stoma_id])
        stoma_id += 1
    # Get areas adjust to borders, which count as half in counting, and not included in average cell size
    ## Cut the border off the image
    temp_area_coverage = temp_area_coverage[image_margin:-image_margin, image_margin:-image_margin]
    ## Get all pavemetn cells
    area_id_arr, area_size_arr = np.unique(temp_area_coverage, return_counts=True)
    ## Get pavement cells adjust to image border
    border_area_ids = np.unique(np.concatenate([np.unique(temp_area_coverage[0,:]), np.unique(temp_area_coverage[-1,:]), np.unique(temp_area_coverage[:,0]), np.unique(temp_area_coverage[:,-1])]))
    border_area_set = set(border_area_ids)
    cell_count = np.sum(area_id_arr < stoma_id_start) - (np.sum(border_area_ids < stoma_id_start) / 2)
    # Cell size sum and stoma size sum
    cell_size_sum = np.sum(area_size_arr[np.where(area_id_arr < stoma_id_start)])/(base_resolution*base_resolution)
    stoma_size_sum = np.sum(area_size_arr[np.where(area_id_arr >= stoma_id_start)])/(base_resolution*base_resolution)
    # (Full) stoma size and aspect
    # remove stomas adjusting to border
    for border_area_id in border_area_ids:
        if border_area_id in stoma_dict.keys():
            stoma_dict.pop(border_area_id)
    stoma_sizes = list()
    stoma_aspects = list()
    for stoma in stoma_dict.values():
        stoma_sizes.append((math.pi * stoma[2] * stoma[3])/(base_resolution*base_resolution))
        stoma_aspects.append(max(stoma[2], stoma[3]) / min(stoma[2], stoma[3]))
    # (Full) cell size
    cell_sizes = list()
    for area_id, area_size in zip(area_id_arr, area_size_arr):
        if (area_id < stoma_id_start) and (area_id not in border_area_set):
            cell_sizes.append(area_size/(base_resolution*base_resolution))
    return {
    'image_effective_size' : str(image_effective_size),
    'stoma_effective_size' : str(stoma_size_sum),
    'cell_effective_size' : str(cell_size_sum),
    'stoma_count' : str(stoma_count),
    'stoma_aspects' : str(stoma_aspects),
    'stoma_sizes' : str(stoma_sizes),
    'cell_count' : str(cell_count),
    'cell_sizes' : str(cell_sizes)
    }