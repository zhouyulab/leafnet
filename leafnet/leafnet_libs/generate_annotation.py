import numpy as np
from skimage import draw

# Output Annotation
def generate_annotation(area_coverage_array:np.ndarray, corrected_stoma_list:list) -> np.ndarray:
    '''
    Generate annotation image from an array for area id and a list of stomata.
    args:
        area_coverage_array - Input array with pixel-wise area label.
        corrected_stoma_list - Input list containing labeled stomata, stomata is represented as [center_r, center_c, length, width, angle]
    return:
        Image using green (0,255,0) to label pavement cell walls and blue (0,0255) to label stomata(8-bit RGB).
    '''
    __BORDER_DRAW_COLOR = (0, 255, 0)
    __STOMA_DRAW_COLOR = (0, 0, 255)
    output_image = np.zeros((area_coverage_array.shape[0], area_coverage_array.shape[1], 3), dtype=np.uint8)
    # Draw Borders
    for i in range(area_coverage_array.shape[0]-1):
        for j in range(area_coverage_array.shape[1]-1):
            cov_1 = area_coverage_array[i, j]
            cov_2 = area_coverage_array[i+1, j]
            cov_3 = area_coverage_array[i, j+1]
            cov_4 = area_coverage_array[i+1, j+1]
            if (cov_1 != cov_2) or (cov_1 != cov_3) or (cov_1 != cov_4):
                output_image[i-1:i+3, j-1:j+3] = __BORDER_DRAW_COLOR
    # Draw Stomata
    for stoma in corrected_stoma_list:
        rr, cc = draw.ellipse(stoma[0], stoma[1], int(
            stoma[2]*1.1), int(stoma[3]*1.1), rotation=-stoma[4])
        draw.set_color(output_image, [rr, cc], __STOMA_DRAW_COLOR)
    return output_image