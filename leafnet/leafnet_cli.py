import argparse, os
from argparse import HelpFormatter, SUPPRESS, OPTIONAL, ZERO_OR_MORE

def get_modules(module_base):
    file_names = os.listdir(module_base)
    module_names = list()
    for file_name in file_names:
        if os.path.isdir(os.path.join(module_base, file_name)) and not file_name.startswith("_"):
            module_names.append(file_name)
    return module_names

class MetavarTypeHelpFormatter(HelpFormatter):
    def _split_lines(self, text, width):
        return text.splitlines()
    def _get_default_metavar_for_optional(self, action):
        return action.type.__name__ 
    def _get_default_metavar_for_positional(self, action):
        return action.type.__name__ 

def parser():
    # Get libs
    output_mode_dict = {
        "INTERACTIVE": False, 
        "GRAPH": True, 
        "ANNOTATE": True, 
        "STATISTIC": True, 
        "ALL": True,
    }

    leafnet_libs_path = os.path.join(os.path.dirname(__file__), r"leafnet_libs")
    image_denoisers = get_modules(os.path.join(leafnet_libs_path, r"image_denoiser"))
    cell_dividers = get_modules(os.path.join(leafnet_libs_path, r"cell_divider"))
    stoma_detectors = list()
    stoma_detector_models_path = os.path.join(leafnet_libs_path, r"stoma_detector", r"models")
    for file_name in os.listdir(stoma_detector_models_path):
        if file_name.endswith(".model"):
            if os.path.exists(os.path.join(stoma_detector_models_path, file_name[:-6]+".res")):
                stoma_detectors.append(file_name[:-6])
    # Parse args
    arg_parser = argparse.ArgumentParser(
        description="LeafNet, a CNN based tool to localize stomata and segment pavement cells.",
        formatter_class=MetavarTypeHelpFormatter,)
    ## Input
    input_group = arg_parser.add_argument_group("Input")
    input_mode_group = input_group.add_mutually_exclusive_group()
    input_group.add_argument("-i",dest="input_path", type=str, required=True, help="Input path. (without -r/ -z: input image)")
    input_mode_group.add_argument("-r", "--recursive", dest="recursive_input", action="store_true", help="The input path is a directory.")
    input_mode_group.add_argument("-z", "--zipfile", dest="zipfile_input", action="store_true", help="The input path is a zipfile.")

    ## Output
    output_group = arg_parser.add_argument_group("Output")
    output_group.add_argument("-m", dest="output_mode", type=str, required=True, choices=output_mode_dict.keys(), help="Output mode.\nCHECK: Interactive\nGRAPH: Save preview image\nANNOTATE: Save image annotation\nSTATISTIC: Save preview image and statistic output\nALL: Save all generated data")
    output_group.add_argument("-p", "--pack", dest="output_zipfile", action="store_true", help="Pack output into a zipfile.")
    output_group.add_argument("-o",dest="output_path", type=str, help="Output path.(without -p: output folder | with -p: output zipfile)")

    ## Optimization
    optm_group = arg_parser.add_argument_group("Arguments for optimization")
    ### Basic
    optm_group.add_argument("--res", dest="res", type=float, default=2.17, help="[CRITICAL] The resolution(pixel per μm) of input image, default = %(default)s.")
    optm_group.add_argument("--bg", dest="bg", type=str, default="Bright", choices=["Bright", "Dark"], help="[CRITICAL] The type of image background, default = %(default)s.")
    ### Image denoiser
    optm_group.add_argument("--dn", dest="dn", type=str, default="PeeledDenoiser", choices=image_denoisers, help="Choose denoiser to denoise input images, default = %(default)s.")
    optm_group.add_argument("--dn_lv", dest="dn_lv", type=float, default=50, help="Strength of denoizing, from 0 to 100, increase denoise strength if your image is noisy, default = %(default)s.")
    ### Stoma detector
    optm_group.add_argument("--sd", dest="sd", type=str, default="StomaNet", choices=stoma_detectors, help="Choose stoma detector to detect stomata, default = %(default)s.")
    optm_group.add_argument("--sd_ts", dest="sd_ts", type=float, default=40, help="Threshold for stoma detection, from 0 to 100, higher threshold decreases fake positive rate, but increases fake negative rate, default = %(default)s.")
    optm_group.add_argument("--min_ss", dest="min_ss", type=float, default=20, help="Minimum stoma size (μm^2), stomata smaller than this threshold will be ignored, default = %(default)s.")
    optm_group.add_argument("--max_ss", dest="max_ss", type=float, default=1500, help="Maximum stoma size (μm^2), stomata larger than this threshold will be ignored, default = %(default)s.")
    optm_group.add_argument("--max_sa", dest="max_sa", type=float, default=5, help="Maximum stoma aspect(length/width ratio), stomata with a larger length/width ratio will be ignored, default = %(default)s.")
    ### Cell divider
    optm_group.add_argument("--cd", dest="cd", type=str, default="LeafSeg", choices=cell_dividers, help="Choose Cell divider to divide cells, default = %(default)s.")
    optm_group.add_argument("--cd_ts", dest="cd_ts", type=float, default=60, help="Threshold for cell divider, from 0 to 100, higher threshold could avoid detecting fake cell borders from noises, but might ignore blur cell borders, default = %(default)s.")
    optm_group.add_argument("--min_cs", dest="min_cs", type=float, default=85, help="Minimum cell size (μm^2), cells smaller than this threshold will be ignored, default = %(default)s.")
    ## Parse Args
    args = arg_parser.parse_args()
    
    # Further check arguments
    args_dict = dict()
    ## Input
    input_path = args.input_path
    recursive_input = args.recursive_input
    zipfile_input = args.zipfile_input

    if not os.path.exists(input_path):  raise FileNotFoundError('Input path not exist.')
    elif recursive_input:
        if not os.path.isdir(input_path): raise FileNotFoundError('Input path exists, but is not a folder, you might want to remove -r?')
    else:
        if not os.path.isfile(input_path): raise FileNotFoundError('Input path exists, but is not a file, you might want to add -r?')

    args_dict['input_path'] = input_path
    args_dict['input_is_folder'] = recursive_input
    args_dict['input_is_zipfile'] = zipfile_input

    ## Output
    output_mode = args.output_mode
    output_path = args.output_path
    output_zip = args.output_zipfile
    # Arugments for output
    if (not output_mode_dict[output_mode]) and output_path: raise ValueError(f"Output Mode {output_mode} does't need a output path!")
    if output_mode_dict[output_mode] and (not output_path): raise ValueError(f"Output Mode {output_mode} needs a output path!")
    if output_path:
        if output_zip:
            if not output_path.endswith(".zip"): output_path = output_path.rstrip(".") + ".zip"
            if os.path.exists(output_path): raise FileExistsError('Output file exists, remove the existing file or change output path!')
            try: open(output_path, "w").close()
            except: raise FileExistsError('Could not create output zip file!')
        else:
            if os.path.exists(output_path):
                if not os.path.isdir(output_path): raise FileNotFoundError('Output Path Exists, But Not Folder!')
                elif os.listdir(output_path): raise FileNotFoundError('Output Path Is Folder, But Not Empty!')
            else:
                os.makedirs(output_path)

    args_dict['output_mode'] = output_mode
    args_dict['output_path_str'] = output_path
    args_dict['output_zipfile'] = output_zip

    ## Optimization
    ### Basic
    if not args.res > 0: raise ValueError(f"{args.res} is not a valid value for image resolution, > 0 expected!")
    else: args_dict['input_image_resolution'] = args.res

    if args.bg == "Bright": args_dict['background_type'] = True
    elif args.bg == "Dark": args_dict['background_type'] = False
    else: raise ValueError(f"{args.bg} is not a valid background type, only Bright and Dark are accepted!")

    ### Image denoiser 
    args_dict['image_denoiser'] = args.dn
    if args.dn_lv < 0 or args.dn_lv > 100: raise ValueError(f"{args.dn_lv} is not a valid value for denoizing strength, 0-100 expected!")
    else: args_dict['denoise_level'] = args.dn_lv

    ### Stoma detector
    args_dict['stoma_detector'] = args.sd
    if args.sd_ts < 0 or args.sd_ts > 100: raise ValueError(f"{args.sd_ts} is not a valid value for stoma detector threshold, 0-100 expected!")
    else: args_dict['stoma_thres'] = args.sd_ts
    if not args.min_ss > 0: raise ValueError(f"{args.min_ss} is not a valid value for min stoma size, > 0 expected!")
    else: args_dict['min_stoma_size'] = args.min_ss
    if not args.max_ss > args.min_ss: raise ValueError(f"{args.max_ss} is not a valid value for max stoma size, > min_ss expected!")
    else: args_dict['max_stoma_size'] = args.max_ss
    if not args.max_sa > 1: raise ValueError(f"{args.max_sa} is not a valid value for max stoma aspect, > 1 expected!")
    else: args_dict['max_stoma_aspect'] = args.max_sa

    ### Cell divider
    args_dict['cell_divider'] = args.cd

    if args.cd_ts < 0 or args.cd_ts > 100: raise ValueError(f"{args.cd_ts} is not a valid value for cell divider threshold, 0-100 expected!")
    else: args_dict['divider_thres'] = args.cd_ts
    if not args.min_cs > 0: raise ValueError(f"{args.min_cs} is not a valid value for min cell size, > 0 expected!")
    else: args_dict['min_cell_size'] = args.min_cs

    return args_dict

def main():
    args_dict = parser()
    # Execute
    from .leafnet_libs.leafnet_exec import leafnet_exec
    leafnet_exec(**args_dict)

if __name__ == "__main__":
    main()