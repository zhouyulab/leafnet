import numpy as np
from skimage import measure, draw
from skimage.segmentation import watershed, find_boundaries
from skimage.morphology import binary_opening, binary_closing, remove_small_objects, binary_erosion, binary_dilation
from tempfile import TemporaryDirectory
import zipfile
from PIL import Image
import cv2
import math
import os
import matplotlib.pyplot as plt
import shutil
import argparse
from argparse import HelpFormatter, SUPPRESS, OPTIONAL, ZERO_OR_MORE

__STOMA_COLOR = (0,0,255)
__BORDER_COLOR = (0,255,0)
__BACKGROUND_COLOR = (0,255,0)

class MetavarTypeHelpFormatter(HelpFormatter):
    def _split_lines(self, text, width):
        return text.splitlines()
    def _get_default_metavar_for_optional(self, action):
        return action.type.__name__ 
    def _get_default_metavar_for_positional(self, action):
        return action.type.__name__ 

def image_file_list_ior(input_folder, output_folder, raw_folder):
    input_file_list = list()
    output_file_list = list()
    raw_file_list = list()
    for file_name in os.listdir(input_folder):
        current_i_path = os.path.join(input_folder, file_name)
        current_o_path = os.path.join(output_folder, file_name)
        current_r_path = os.path.join(raw_folder, file_name)
        if os.path.isdir(current_i_path):
            sub_in, sub_out, sub_raw = image_file_list_ior(current_i_path, current_o_path, current_r_path)
            input_file_list.extend(sub_in)
            output_file_list.extend(sub_out)
            raw_file_list.extend(sub_raw)
        else:
            try: Image.open(current_i_path).close()
            except: continue
            if current_i_path.endswith("_anno.png"):
                input_file_list.append(current_i_path)
                output_file_list.append(current_o_path.strip("_anno.png"))
                os.makedirs(current_o_path.strip("_anno.png"))
                raw_file_list.append(current_r_path.strip("_anno.png"))
    return input_file_list, output_file_list, raw_file_list

def annotation_stoma_pca(stoma_dots):
    stoma_size = len(stoma_dots)
    dots_array = np.array(stoma_dots, dtype=float)
    # Get Stoma Center By weighted Average
    stoma_center = dots_array.transpose().mean(axis=-1)
    pca_center, pc_array, pc_weights = cv2.PCACompute2(dots_array, np.empty((0)))
    stoma_angle = -math.atan2(pc_array[0,1], pc_array[0,0])
    stoma_aspect = (pc_weights[0,0] / pc_weights[1,0])**0.5
    # Stoma Data From Size
    stoma_length = ((stoma_size/math.pi)*stoma_aspect)**0.5
    stoma_width = (stoma_length/stoma_aspect)
    return [stoma_center[0], stoma_center[1], stoma_length, stoma_width, stoma_angle]

def parse_annotation(annotation_arr):
    # Get Stomata
    stoma_mask = annotation_arr[:,:,2] > 127
    stoma_mask = binary_closing(stoma_mask)
    stoma_mask = binary_erosion(stoma_mask)
    stoma_mask = remove_small_objects(stoma_mask, min_size=64)
    stoma_list = list()
    for stoma_item in measure.regionprops(measure.label(stoma_mask)):
        center_r, center_c = stoma_item.centroid
        stoma_length = stoma_item.major_axis_length/2
        stoma_width = stoma_item.minor_axis_length/2
        stoma_angle = stoma_item.orientation + (math.pi/2)
        stoma_list.append([center_r, center_c, stoma_length, stoma_width, stoma_angle])
    # 
    border_mask = annotation_arr[:,:,1] > 127
    cell_mask = np.logical_not(np.logical_or(stoma_mask, border_mask))
    cell_mask = binary_opening(cell_mask)
    cell_mask = remove_small_objects(cell_mask, min_size=64)
    area_coverage_array = watershed(np.zeros(cell_mask.shape,dtype=np.uint8), measure.label(cell_mask))

    return area_coverage_array, stoma_list

def area_array_to_binary_image(area_coverage_array, corrected_stoma_list, output_image):
    temp_coverage_array = area_coverage_array.copy()
    for stoma in corrected_stoma_list:
        rr, cc = draw.ellipse(stoma[0], stoma[1], int(stoma[2]*1.1), int(stoma[3]*1.1), rotation=stoma[4])
        draw.set_color(temp_coverage_array, [rr, cc], 0)
    discarding_areas = set(np.concatenate([temp_coverage_array[:,0].flatten(), temp_coverage_array[:,-1].flatten(), temp_coverage_array[0,:].flatten(), temp_coverage_array[-1,:].flatten(), [0]]))
    for area_id in discarding_areas:
        temp_coverage_array[np.where(temp_coverage_array == area_id)] = 0
    boundary_mask = find_boundaries(temp_coverage_array)
    boundary_mask = binary_dilation(boundary_mask, selem = np.ones((3,3), dtype=bool))
    temp_coverage_array[boundary_mask] = 0
    binary_image = np.zeros(temp_coverage_array.shape, dtype=np.uint8)
    binary_image[np.where(temp_coverage_array>0)] = 255
    Image.fromarray(binary_image).save(output_image)

def main():
    # Parse args
    arg_parser = argparse.ArgumentParser(
        description="LeafNet annotation parser, a tool to pass leafnet annotation to PaCeQuant.",
        formatter_class=MetavarTypeHelpFormatter,)
    ## Input
    input_group = arg_parser.add_argument_group("Input")
    input_group.add_argument("-i",dest="input_path", type=str, required=True, help='Input folder containing annotation images ends with "_anno.png".')
    input_group.add_argument("--imagej",dest="imagej_path", type=str, required=True, help='Path to an imagej executable with PaCeQuant plugin installed (PaCeQuant plugin is in mitobo plugin).')
    input_group.add_argument("--raw",dest="raw_image_path", type=str, help='Input folder containing raw images. Raw images are required if you need stacked heatmaps. The directory structure and filenames must correspond to annotation images (annotation image file name = raw image file name + "_anno.png").')

    ## Output
    output_group = arg_parser.add_argument_group("Output")
    output_group.add_argument("-o",dest="output_path", type=str, required=True, help="Output path.")
    output_group.add_argument("--heatmap", dest="output_heatmap", action="store_true", help="Generate heatmap with scalebars.")
    output_group.add_argument("--stack", dest="output_stack", action="store_true", help="Generate stacked heatmap (heatmap above raw image).")

    ## Parse Args
    args = arg_parser.parse_args()

    ## Input
    input_path = args.input_path
    imagej_path = args.imagej_path
    raw_image_path = args.raw_image_path

    if not os.path.exists(input_path):  raise FileNotFoundError('Input path not exist.')
    elif os.path.isfile(input_path): raise FileNotFoundError('Input path exists, but is a file, annotation parser only accept folder for input path.')

    ## Output
    output_path = args.output_path
    output_heatmap = args.output_heatmap
    output_stack = args.output_stack

    # Arugments for output
    if not os.path.exists(output_path): os.makedirs(output_path)
    elif not os.path.isdir(output_path): raise FileNotFoundError('Output path exists, but not a folder!')
    elif os.listdir(output_path): raise FileNotFoundError('Output path is a folder, but not empty!')

    if output_stack:
        if not raw_image_path: raise FileNotFoundError('Raw image path is needed to draw stacked heatmap.')
        if not os.path.exists(raw_image_path): raise FileNotFoundError('Raw image path is needed to draw stacked heatmap, given path not exist.')
        elif os.path.isfile(raw_image_path): raise FileNotFoundError('Raw image path is needed to draw stacked heatmap, given path is a file, annotation parser only accept folder for input path.')

    # Collect input files
    input_file_list, output_file_list, raw_file_list = image_file_list_ior(input_path, output_path, raw_image_path)
    # Check if input file exist:
    if not input_file_list: raise FileNotFoundError('No image file found in input directory!')

    # Compose a temp script file, as imagej could make mistakes in arguments sent from different systems.
    imagej_work_dir = TemporaryDirectory()
    imagej_script_template = os.path.join(os.path.dirname(__file__), "pacequant_process.js")
    imagej_script_path = os.path.join(imagej_work_dir.name, "run_pacequant.js")
    images_binary_image_dir = os.path.join(imagej_work_dir.name, 'images')
    with open(imagej_script_path, 'w', encoding='utf-8') as imagej_script:
        imagej_script.write("var image_res = {0}\n".format(2.17))
        imagej_script.write('var input_path = "{0}"\n'.format(images_binary_image_dir.replace("\\", "\\\\")))
        with open(imagej_script_template, encoding='utf-8') as script_template:
            imagej_script.write(script_template.read())

    # Parse leafnet annotations into binary files for PaceQuant
    os.mkdir(images_binary_image_dir)
    i = 0
    for input_file in input_file_list:
        input_array = np.array(Image.open(input_file).convert('RGB'))
        area_coverage_array, corrected_stoma_list = parse_annotation(input_array)
        area_array_to_binary_image(area_coverage_array, corrected_stoma_list, os.path.join(images_binary_image_dir, str(i)+".png"))
        i += 1

    # IMAGEJ OPERATION
    os.system('{0} --headless -macro {1}'.format(imagej_path, imagej_script_path))

    # Collect PaceQuant results
    imagej_result_dir = os.path.join(images_binary_image_dir, "results")
    for i in range(len(input_file_list)):
        table_file_name = str(i) + "-table.txt"
        area_file_name = str(i) + "-grayscale-result.tif"
        shutil.copyfile(os.path.join(imagej_result_dir, table_file_name), os.path.join(output_file_list[i], "table.txt"))
        shutil.copyfile(os.path.join(imagej_result_dir, area_file_name), os.path.join(output_file_list[i], "area_id.tif"))

    # Generate heatmaps
    if output_heatmap or output_stack:
        for i in range(len(output_file_list)):
            output_image_dir = output_file_list[i]
            # Files
            current_table_path = os.path.join(output_image_dir, "table.txt")
            current_seg_path = os.path.join(output_image_dir, "area_id.tif")
            heatmap_path = os.path.join(output_image_dir, "heatmap")
            heatmap_stack_path = os.path.join(output_image_dir, "heatmap_stack")
            if output_heatmap: os.makedirs(heatmap_path)
            if output_stack: os.makedirs(heatmap_stack_path)
            
            # Read
            ij_area = np.array(Image.open(current_seg_path))
            ij_data = np.genfromtxt(current_table_path , delimiter="\t", names=True)
            
            source_img = None
            current_image_output_stack = False
            if output_stack:
                try:
                    source_img = np.array(Image.open(raw_file_list[i]).convert('RGB'))
                    current_image_output_stack = True
                except:
                    source_img = None
                    current_image_output_stack = False
                    open(os.path.join(heatmap_stack_path, "RawImageNotFound"), 'w').close()

            # Draw
            area_list = ij_data[ij_data.dtype.names[0]].astype(int)
            for parameter_name in ij_data.dtype.names[1:]:
                parameter_save_name = parameter_name.strip().split('_')[0]
                value_map = np.zeros((ij_area.shape[0], ij_area.shape[1]), dtype=float)
                value_map[:,:] = np.nan
                value_list = ij_data[parameter_name]
                for i in range(len(area_list)):
                    try:
                        # Value
                        if np.isnan(value_list[i]):
                            value_map[np.where(ij_area==area_list[i])] = np.nan
                        else:
                            value_map[np.where(ij_area==area_list[i])] = value_list[i]
                    except:
                        # Nan
                        value_map[np.where(ij_area==area_list[i])] = np.nan
                # Draw heatmap
                if output_heatmap:
                    plt.figure()
                    heatmap_output = plt.imshow(value_map, cmap = 'jet')
                    plt.colorbar(heatmap_output, shrink=0.8)
                    plt.savefig(os.path.join(heatmap_path, parameter_save_name+".png"), dpi=300)
                    plt.close()
                
                # Draw Stacked heatmap
                if current_image_output_stack:
                    nan_mask = np.where(np.isnan(value_map))
                    not_nan_mask = np.where(np.logical_not(np.isnan(value_map)))
                    cv2_draw_image = value_map.copy()
                    cv2_draw_image[nan_mask] = np.mean(value_map[not_nan_mask])
                    cv2_draw_image -= np.min(cv2_draw_image)
                    cv2_draw_image *= (255/np.max(cv2_draw_image))
                    cv2_draw_image = cv2_draw_image.astype(np.uint8)

                    heat_stack_img = cv2.applyColorMap(cv2_draw_image, cv2.COLORMAP_JET)
                    heat_stack_img = cv2.addWeighted(source_img, 0.3, heat_stack_img, 0.7, 0)
                    heat_stack_img[nan_mask] = source_img[nan_mask]

                    Image.fromarray(heat_stack_img).save(os.path.join(heatmap_stack_path, parameter_save_name+".png"))


if __name__ == "__main__":
    main()