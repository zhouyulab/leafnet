from io import RawIOBase
import os, importlib
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from tempfile import TemporaryDirectory
import zipfile

from .leafnet_core import leafnet_image_parser
from .load_image import load_image
from .image_file_list import image_file_list_io, image_file_list_input_only
from .generate_preview_image import generate_preview_image
from .generate_annotation import generate_annotation
from .generate_statistics import generate_statistics

def leafnet_exec(**kwargs):
    # Load Arguments
    input_is_folder = kwargs['input_is_folder']
    input_is_zipfile = kwargs['input_is_zipfile']
    input_image_resolution = kwargs['input_image_resolution']
    image_denoiser = kwargs['image_denoiser']
    denoise_level = kwargs['denoise_level']
    stoma_detector = kwargs['stoma_detector']
    background_type = kwargs['background_type']
    cell_divider = kwargs['cell_divider']
    divider_thres = kwargs['divider_thres']
    stoma_thres = kwargs['stoma_thres']
    min_cell_size = kwargs['min_cell_size']
    min_stoma_size = kwargs['min_stoma_size']
    max_stoma_size = kwargs['max_stoma_size']
    max_stoma_aspect = kwargs['max_stoma_aspect']
    input_path = kwargs['input_path']
    output_mode = kwargs['output_mode']
    output_zipfile = kwargs['output_zipfile']
    output_path = kwargs['output_path_str']

    stat_list = [
        "image_name",
        "image_res",
        "stoma_density",
        "cell_density",
        "all_cell_size_distrib", 
        "pavement_cell_size_distrib", 
        "stoma_size_distrib", 
        "pavement_cell_circularity", 
        "cell_counts_adjust_to_stoma", 
        "pavement_cell_counts_adjust_to_stoma", 
        "stoma_counts_adjust_to_stoma", 
        "small_cell_counts_adjust_to_stoma", 
        "cell_counts_adjust_to_pave", 
        "pavement_cell_counts_adjust_to_pave", 
        "stoma_counts_adjust_to_pave", 
        "small_cell_counts_adjust_to_pave", 
    ]
    
    # Prepare Image preprocessor
    image_denoiser = importlib.import_module(f'.image_denoiser.{image_denoiser}.denoiser',"leafnet.leafnet_libs").denoiser(denoise_level=denoise_level)
    input_preprocesser = image_denoiser.denoise

    # Disable output if no output
    if output_mode == "INTERACTIVE":
        output_path = None
        output_zipfile = False

    # Generate IO Image List
    input_files = None
    output_files = None
    temp_input_directory = None
    temp_output_directory = None
    output_zip_filename = None

    if input_is_zipfile:
        temp_input_directory = TemporaryDirectory()
        zipfile.ZipFile(input_path).extractall(temp_input_directory.name)
        input_path = temp_input_directory.name
        input_is_folder = True

    if output_zipfile:
        output_zip_filename = output_path
        temp_output_directory = TemporaryDirectory()
        output_path = temp_output_directory.name

    if input_is_folder:
        if output_path:
            input_files, output_files = image_file_list_io(input_path, output_path)
        else:
            input_files = image_file_list_input_only(input_path)
    else:
        input_files = [input_path,]
        if output_path:
            output_files = [os.path.join(output_path, os.path.basename(input_path)),]

    # Default res = 2.17
    model_resolution = 2.17
    # Read Meta File
    try:
        with open(os.path.join(os.path.dirname(__file__), r'stoma_detector', r'models', stoma_detector + r'.res')) as model_meta_file: 
            model_meta = model_meta_file.readlines()
            model_resolution = float(model_meta[0])
    except:
        raise ValueError(f"The resolution file of this model:{stoma_detector + r'.res'} does not exist or contains no value.")
    # Create Leafnet Image Parser
    leafnet_parser = leafnet_image_parser(stoma_detector, cell_divider, divider_thres, stoma_thres, min_cell_size, min_stoma_size, max_stoma_size, max_stoma_aspect, model_resolution)

    # Load Images
    for image_index, file_path in enumerate(input_files):
        file_name = os.path.basename(file_path)
        input_image, raw_image = load_image(file_path, model_resolution / input_image_resolution, background_type, preprocesser = input_preprocesser)
        area_id_set, area_coverage_array, corrected_stoma_list = leafnet_parser.process_image(input_image)
        # Interactive Image Check
        if output_mode == "INTERACTIVE":
            preview_image = generate_preview_image(raw_image, area_coverage_array, corrected_stoma_list)
            plt.imshow(preview_image)
            plt.show()

        # Save Preview Image
        elif output_mode == "GRAPH":
            preview_image = generate_preview_image(raw_image, area_coverage_array, corrected_stoma_list)
            Image.fromarray(preview_image).save(output_files[image_index] + '_graph.png')

        # Output Image Annotation
        elif output_mode == "ANNOTATE":
            annotation_image = generate_annotation(area_coverage_array, corrected_stoma_list)
            Image.fromarray(annotation_image).save(output_files[image_index] + '_anno.png')

        # Output Statistic Results
        elif output_mode == "STATISTIC":
            # Save preview image
            preview_image = generate_preview_image(raw_image, area_coverage_array, corrected_stoma_list)
            Image.fromarray(preview_image).save(output_files[image_index] + '_graph.png')
            # Save statistical data
            statistic_save_path = output_files[image_index] + '_statistic.txt'
            statistic_dict = generate_statistics(area_coverage_array, corrected_stoma_list, model_resolution)
            meta_dict = dict()
            meta_dict['image_name'] = os.path.basename(output_files[image_index])
            meta_dict['image_res'] = input_image_resolution

            output_string = ""
            for meta_key, meta_val in meta_dict.items():
                output_string += meta_key + ":" + str(meta_val) + '\n'
            for stat_key, stat_val in statistic_dict.items():
                output_string += stat_key + ":" + str(stat_val) + '\n'
            
            with open(os.path.join(statistic_save_path), 'w') as result_file:
                result_file.write(output_string)
        
        elif output_mode == "ALL":
            # Save preview image
            preview_image = generate_preview_image(raw_image, area_coverage_array, corrected_stoma_list)
            Image.fromarray(preview_image).save(output_files[image_index] + '_graph.png')
            # Save annotation image
            annotation_image = generate_annotation(area_coverage_array, corrected_stoma_list)
            Image.fromarray(annotation_image).save(output_files[image_index] + '_anno.png')
            # Save statistical data
            statistic_save_path = output_files[image_index] + '_statistic.txt'
            statistic_dict = generate_statistics(area_coverage_array, corrected_stoma_list, model_resolution)
            meta_dict = dict()
            meta_dict['image_name'] = os.path.basename(output_files[image_index])
            meta_dict['source_image_res'] = input_image_resolution
            meta_dict['generated_image_res'] = model_resolution


            output_string = ""
            for meta_key, meta_val in meta_dict.items():
                output_string += meta_key + ":" + str(meta_val) + '\n'
            for stat_key, stat_val in statistic_dict.items():
                output_string += stat_key + ":" + str(stat_val) + '\n'
            
            with open(os.path.join(statistic_save_path), 'w', encoding='utf-8') as result_file:
                result_file.write(output_string)
    
    # Pack files if needed
    if output_zipfile:
        with zipfile.ZipFile(output_zip_filename, 'w', zipfile.ZIP_DEFLATED) as target_file:
            for path, sub_dirs, file_list in os.walk(output_path):
                zip_path = path.replace(output_path,'')
                for current_file_name in file_list:
                    target_file.write(os.path.join(path,current_file_name), os.path.join(zip_path,current_file_name))
