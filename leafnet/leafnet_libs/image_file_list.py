import os
from typing import List, Tuple
from PIL import Image

def image_file_list_io(input_folder:str, output_folder:str)->Tuple[list,list]:
    '''
    Get all images in the input folder and sub directories recursively, and generate output path with the same structure.
    args:
        input_folder - Path for input folder.
        output_folder - Path for output folder.
    return:
        Two lists containing pairs of pathes for input files and output files.
    '''
    input_file_list = list()
    output_file_list = list()
    for file_name in os.listdir(input_folder):
        current_path = os.path.join(input_folder, file_name)
        target_path = os.path.join(output_folder, file_name)
        if os.path.isdir(current_path):
            sub_in, sub_out = image_file_list_io(current_path, target_path)
            input_file_list.extend(sub_in)
            output_file_list.extend(sub_out)
        else:
            try: Image.open(current_path).close()
            except: continue
            if not os.path.exists(os.path.dirname(target_path)):
                os.makedirs(os.path.dirname(target_path))
            input_file_list.append(current_path)
            output_file_list.append(target_path)
    return input_file_list, output_file_list

def image_file_list_input_only(input_folder:str)->list:
    '''
    Get all images in the input folder and sub directories recursively.
    args:
        input_folder - Path for input folder.
    return:
        List containing pathes for input files.
    '''
    input_file_list = list()
    for file_name in os.listdir(input_folder):
        current_path = os.path.join(input_folder, file_name)
        if os.path.isdir(current_path):
            sub_in = image_file_list_input_only(current_path)
            input_file_list.extend(sub_in)
        else:
            try: Image.open(current_path).close()
            except: continue
            input_file_list.append(current_path)
    return input_file_list