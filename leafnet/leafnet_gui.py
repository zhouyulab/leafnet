import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
import os, platform, ctypes
from .leafnet_libs.leafnet_exec import leafnet_exec

class leafnet_gui:
    def run(self):
        # try:
        args_dict = dict()
        # Input Method
        if (self.input_method.get() == 0):
            args_dict['input_is_folder'] = False
            args_dict['input_is_zipfile'] = False
        elif (self.input_method.get() == 1):
            args_dict['input_is_folder'] = True
            args_dict['input_is_zipfile'] = False
        elif (self.input_method.get() == 2):
            args_dict['input_is_folder'] = False
            args_dict['input_is_zipfile'] = True
        else:
            raise ValueError("Input method not selected!")
        # Image Configure
        ## Image Resolution
        if (self.image_res.get() == ''):
            args_dict['input_image_resolution'] = 2.17
        else:
            args_dict['input_image_resolution'] = float(self.image_res.get())
        ## Image Denoiser
        args_dict['image_denoiser'] = self.image_denoiser.get()
        ## Denoise level
        if(self.denoise_level.get() == ''):
            args_dict['denoise_level'] = 50
        else:
            args_dict['denoise_level'] = int(self.denoise_level.get())
        ## Stoma Detector
        args_dict['stoma_detector'] = self.stoma_detector.get()
        ## Background Type (True For Bright, False For Dark.)
        if self.bg_type.get() == "Bright":
            args_dict['background_type'] = True
        else:
            args_dict['background_type'] = False
        ## Cell Divider
        args_dict['cell_divider'] = self.cell_divider.get()
        ## Divider Threshold
        if(self.divider_thres.get() == ''):
            args_dict['divider_thres'] = 60
        else:
            args_dict['divider_thres'] = int(self.divider_thres.get())
        ## Stoma Threshold
        if(self.stoma_thres.get() == ''):
            args_dict['stoma_thres'] = 40
        else:
            args_dict['stoma_thres'] = int(self.stoma_thres.get())
        ## Min Cell Size
        if(self.min_cell_size.get() == ''):
            args_dict['min_cell_size'] = 0
        else:
            args_dict['min_cell_size'] = float(self.min_cell_size.get())
        ## Min Stoma Size
        if(self.min_stoma_size.get() == ''):
            args_dict['min_stoma_size'] = 0
        else:
            args_dict['min_stoma_size'] = float(self.min_stoma_size.get())
        ## Max Stoma Size
        if(self.max_stoma_size.get() == ''):
            args_dict['max_stoma_size'] = float("inf")
        else:
            args_dict['max_stoma_size'] = float(self.max_stoma_size.get())
        ## Max Stoma Aspect
        if(self.max_stoma_aspect.get() == ''):
            args_dict['max_stoma_aspect'] = float("inf")
        else:
            args_dict['max_stoma_aspect'] = float(self.max_stoma_aspect.get())
        # Input Path
        args_dict['input_path'] = self.input_path.get()
        args_dict['output_zipfile'] = self.output_zipfile.get()
        # Output Mode
        args_dict['output_mode'] = self.output_mode_program_code_dict[self.output_mode.get()]
        # Output Path
        if (args_dict['output_mode'] == 'INTERACTIVE_CHECK'):
            args_dict['output_path_str'] = None
        else:
            args_dict['output_path_str'] = self.output_path.get()
        # Check Input path
        if args_dict['input_path'] == '':
            raise FileNotFoundError('Input Path Not Defined.')
        else:
            if not os.path.exists(args_dict['input_path']):
                raise FileNotFoundError('Input Path Not Found:' + args_dict['input_path'])
            else:
                if args_dict['input_is_folder']:
                    if not os.path.isdir(args_dict['input_path']):
                        raise FileNotFoundError('Input Path Exists, But Not Folder: ' + args_dict['input_path'])
                else:
                    if not os.path.isfile(args_dict['input_path']):
                        raise FileNotFoundError('Input Path Exists, But Not File: ' + args_dict['input_path'])

        # Check Output Folder
        if (args_dict['output_mode'] != "INTERACTIVE"):
            output_path = args_dict['output_path_str']
            if not output_path:
                raise FileNotFoundError('Output Path Not Defined.')
            else:
                if args_dict['output_zipfile']:
                    try: open(output_path, "w").close()
                    except: raise FileExistsError('Could not create output zip file!')
                else:
                    if os.path.exists(output_path):
                        if not os.path.isdir(output_path):
                            raise FileNotFoundError('Output Path Exists, But Not Folder: ' + output_path)
                        else:
                            if os.listdir(output_path):
                                raise FileNotFoundError('Output Path Is Folder, But Not Empty: ' + output_path)
                    else:
                        os.makedirs(output_path)
        # Execute
        leafnet_exec(**args_dict)
        if (args_dict['output_mode'] != "INTERACTIVE"):
            messagebox.showinfo('Done','Finished!')
        # except Exception as e:
        #     messagebox.showerror('Error', e)

    def select_image_path(self):
        if (self.input_method.get() == 0) or (self.input_method.get() == 2):
            input_path = filedialog.askopenfilename()
            if input_path:
                self.input_path.set(input_path)
        elif self.input_method.get() == 1:
            input_path = filedialog.askdirectory()
            if input_path:
                self.input_path.set(input_path)

    def input_method_select(self):
        # File
        if self.input_method.get() == 0:
            self.input_path_title_str.set("Image:")
        # Folder
        elif self.input_method.get() == 1:
            self.input_path_title_str.set("Folder:")
        elif self.input_method.get() == 2:
            self.input_path_title_str.set("Zip:")
        self.input_path.set("")

    def select_output_folder_path(self):
        if self.output_zipfile.get():
            target_path = filedialog.asksaveasfilename(filetypes=[("Zip Archive", "*.zip")])
            if target_path:
                if not target_path.endswith(".zip"):
                    target_path = target_path.rstrip(".") + ".zip"
                self.output_path.set(target_path)
        else:
            self.output_path.set(filedialog.askdirectory())

    def output_pack_select(self):
        # Packed
        if self.output_zipfile.get():
            self.output_path_title_str.set("Zip:")
        # Unpacked
        else:
            self.output_path_title_str.set("Folder:")
        self.output_path.set("")


    def mode_select(self, event):
        if self.output_mode_has_output_file[self.output_mode.get()]:
            self.output_pack_checker['state'] = tk.NORMAL
            self.output_path_title['state'] = tk.NORMAL
            self.output_path_button['state'] = tk.NORMAL
            self.output_path_entry['state'] = tk.NORMAL
        else:
            self.output_pack_checker['state'] = tk.DISABLED
            self.output_path_title['state'] = tk.DISABLED
            self.output_path_button['state'] = tk.DISABLED
            self.output_path_entry['state'] = tk.DISABLED
    
    def str_is_positive_float(self, input_str):
        if(input_str == ''):
            return True
        elif(input_str.count('.') == 0):
            if (input_str == '' or input_str.isdigit()):
                return True
            else:
                return False
        elif(input_str.count('.') > 1):
            return False
        elif(input_str.count('.') == 1):
            left_num,right_num = input_str.split('.')
            if ((left_num == '' or left_num.isdigit()) and (right_num == '' or right_num.isdigit())):
                return True
            else:
                return False

    def str_is_0_to_100_int(self, input_str):
        if(input_str == ''):
            return True
        elif(not input_str.isdigit()):
            return False
        elif (int(input_str) < 0):
            return False
        elif (int(input_str) > 100):
            return False
        elif(len(input_str)>1 and input_str[0]=='0'):
            return False
        else:
            return True

    def str_is_positive_int(self, input_str):
        if(input_str == ''):
            return True
        elif(not input_str.isdigit()):
            return False
        elif (int(input_str) < 0):
            return False
        elif(len(input_str)>1 and input_str[0]=='0'):
            return False
        else:
            return True

    def __init__(self):
        # Init Vars
        ## Background types
        self.bg_types = ["Bright", "Dark"]
        ## Output Modes
        ## output_mode_list[0] = [mode_name_display, mode_name, has_output_file]
        output_mode_list = [
            ["Interactive", "INTERACTIVE", False],
            ["Save Preview Image", "GRAPH", True],
            ["Save Annotation", "ANNOTATE", True],
            ["Save Statistic", "STATISTIC", True],
            ["Save All", "ALL", True],
        ]
        denoiser_default_order = ["PeeledDenoiser", "StainedDenoiser", "None"]
        stoma_detector_default_order = ["StomaNet", "StomaNetConfocal", "StomaNetUniversal", "None"]
        pavement_cell_default_order = ["LeafSeg", "ITKMorphologicalWatershed", "None"]
        self.output_modes = list()
        self.output_mode_program_code_dict = dict()
        self.output_mode_has_output_file = dict()
        for mode_name_display, mode_name, has_output_file in output_mode_list:
            self.output_modes.append(mode_name_display)
            self.output_mode_program_code_dict[mode_name_display] = mode_name
            self.output_mode_has_output_file[mode_name_display] = has_output_file
        ## Image Denoisers
        image_denoiser_path = os.path.join(os.path.dirname(__file__), 'leafnet_libs', 'image_denoiser')
        self.image_denoisers_unsorted = list()
        for filename in os.listdir(image_denoiser_path): 
            if os.path.isdir(os.path.join(image_denoiser_path, filename)):
                if(not filename.startswith('__')):
                    self.image_denoisers_unsorted.append(filename)
        ### Sort
        self.image_denoisers = list()
        for name in denoiser_default_order:
            if name in self.image_denoisers_unsorted:
                self.image_denoisers.append(name)
                self.image_denoisers_unsorted.remove(name)
        self.image_denoisers.extend(self.image_denoisers_unsorted)

        ## Stoma Recognizers
        stoma_detector_models_path = os.path.join(os.path.dirname(__file__), r'leafnet_libs', r'stoma_detector', r"models")
        self.stoma_detectors_unsorted = list()
        for file_name in os.listdir(stoma_detector_models_path):
            if file_name.endswith(".model"):
                if os.path.exists(os.path.join(stoma_detector_models_path, file_name[:-6]+".res")):
                    self.stoma_detectors_unsorted.append(file_name[:-6])
        ### Sort
        self.stoma_detectors = list()
        for name in stoma_detector_default_order:
            if name in self.stoma_detectors_unsorted:
                self.stoma_detectors.append(name)
                self.stoma_detectors_unsorted.remove(name)
        self.stoma_detectors.extend(self.stoma_detectors_unsorted)

        ## Cell dividers
        cell_divider_path = os.path.join(os.path.dirname(__file__), 'leafnet_libs', 'cell_divider')
        self.cell_dividers_unsorted = list()
        for filename in os.listdir(cell_divider_path): 
            if os.path.isdir(os.path.join(cell_divider_path, filename)):
                if(not filename.startswith('__')):
                    self.cell_dividers_unsorted.append(filename)
        ### Sort
        self.cell_dividers = list()
        for name in pavement_cell_default_order:
            if name in self.cell_dividers_unsorted:
                self.cell_dividers.append(name)
                self.cell_dividers_unsorted.remove(name)
        self.cell_dividers.extend(self.cell_dividers_unsorted)

        # Main Window
        self.main_box=tk.Tk()
        self.main_box.resizable(width=False, height=False)
        self.main_box.title('LeafNet')
        # High Res for Windows
        if platform.system() == "Windows":
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
            ScaleFactor=ctypes.windll.shcore.GetScaleFactorForDevice(0)
            self.main_box.tk.call('tk', 'scaling', ScaleFactor/75)
        
        # Vars
        ## Input
        self.input_path_title_str = tk.StringVar()
        self.input_path_title_str.set("Image:")
        self.input_path = tk.StringVar()
        self.input_method = tk.IntVar()
        ## Image Configure
        self.image_res = tk.StringVar(value = 2.17)
        self.image_denoiser = tk.StringVar(value = self.image_denoisers[0])
        self.denoise_level = tk.IntVar(value = 50)
        self.stoma_detector = tk.StringVar(value = self.stoma_detectors[0])
        self.bg_type = tk.StringVar(value = self.bg_types[0])
        self.cell_divider = tk.StringVar(value = self.cell_dividers[0])
        self.divider_thres = tk.IntVar(value = 60)
        self.stoma_thres = tk.IntVar(value = 40)
        self.min_cell_size = tk.DoubleVar(value = 85)
        self.min_stoma_size = tk.DoubleVar(value = 20)
        self.max_stoma_size = tk.DoubleVar(value = 1500)
        self.max_stoma_aspect = tk.DoubleVar(value = 5)
        ## Output
        self.output_path_title_str = tk.StringVar()
        self.output_path_title_str.set("Folder:")
        self.output_path = tk.StringVar(value="")
        self.output_zipfile = tk.BooleanVar(value=False)
        self.output_mode = tk.StringVar(value = self.output_modes[0])

        # Input Validation
        ## Is Positive Float
        positive_float_val = self.main_box.register(self.str_is_positive_float)
        ## Is 0-100 Int
        int_0_100_val = self.main_box.register(self.str_is_0_to_100_int)
        ## Is Positive Int
        positive_int_val = self.main_box.register(self.str_is_positive_int)

        # Input Frame
        input_frame = ttk.LabelFrame(self.main_box, labelwidget = ttk.Label(text = "Input"), padding=(4,2))
        ## Input Method Title
        ttk.Label(input_frame,text = "Type:", width=6, anchor='w').grid(pady=2, row=0, column=0, sticky="w")
        ## Input Method Switch
        input_switch = ttk.Frame(input_frame)
        ### Single Image Radio
        ttk.Radiobutton(input_switch,text = "Image", value=0, command = self.input_method_select, variable=self.input_method).grid(row = 0, column = 0,sticky="w")
        ### Batch Radio
        ttk.Radiobutton(input_switch,text = "Folder", value=1, command = self.input_method_select, variable=self.input_method).grid(row = 0, column = 1,sticky="w")
        ### Zipfile Radio
        ttk.Radiobutton(input_switch,text = "Zip", value=2, command = self.input_method_select, variable=self.input_method).grid(row = 0, column = 2,sticky="w")
        ## Input Method Switch END
        input_switch.grid(pady=2, row = 0, column = 1,sticky="w")
        ## Input Path Title
        ttk.Label(input_frame,textvariable = self.input_path_title_str, width=6, anchor='w', ).grid(pady=2, row=1, column=0, sticky="w")
        ## Input Path Entry
        ttk.Entry(input_frame, textvariable = self.input_path, width=21).grid(pady=2, row = 1, column = 1, sticky="w")
        ## Browse Button
        ttk.Button(input_frame, text = "Browse..", command=self.select_image_path, width=27).grid(pady=2, row = 2, column = 0, columnspan = 2)
        # Input Frame End
        input_frame.grid(padx=8, pady=6, row = 0, column = 0)

        # Basic Config Frame
        basic_cfg_frame = ttk.LabelFrame(self.main_box, labelwidget = ttk.Label(text = "Basic configuration"), padding=(4,2))
        ## Image Resolution
        ### Title
        ttk.Label(basic_cfg_frame, text = "Image resolution: ", width=16, anchor='w').grid(pady=2, row=0, column=0, sticky="w")
        ### Input & Unit
        img_res_input_unit_frame = ttk.Frame(basic_cfg_frame)
        ttk.Entry(img_res_input_unit_frame, textvariable = self.image_res, validate='key', validatecommand=(positive_float_val, '%P'), width=5).grid(row=0, column=0, sticky="w")
        ttk.Label(img_res_input_unit_frame, text = "px/μm", anchor='w').grid(row=0, column=1, sticky="w")
        img_res_input_unit_frame.grid(pady=2, row=0, column=1, sticky="w")
        ## Background Type
        ### Title
        ttk.Label(basic_cfg_frame,text = "Background type: ", width=16, anchor='w').grid(pady=2, row=1, column=0, sticky="w")
        ### Selection
        ttk.Combobox(basic_cfg_frame, state='readonly', value=self.bg_types, textvariable=self.bg_type, width=8).grid(pady=2, row=1, column=1, sticky="w")
        # Basic Config Frame END
        basic_cfg_frame.grid(padx=8, pady=6, row = 1, column = 0)

        # Advanced Config Frame
        adv_cfg_frame = ttk.LabelFrame(self.main_box, labelwidget = ttk.Label(text = "Advanced configuration"), padding=(4,2))
        adv_cfg_frame.grid(padx=8, pady=6, row = 0, column = 1, rowspan=4)
        ## Denoiser Frame
        denoiser_cfg_frame = ttk.LabelFrame(adv_cfg_frame, labelwidget = ttk.Label(text = "Image denoiser"), padding=(4,2))
        denoiser_cfg_frame.grid(pady=2, row=0, column=0, sticky="w")
        ### Image Denoiser
        denoiser_method_line = ttk.Frame(denoiser_cfg_frame)
        denoiser_method_line.grid(pady=2, row = 0, column = 0, sticky="w")
        #### Title
        ttk.Label(denoiser_method_line,text = "Method: ", width=8, anchor='w').grid(row=0, column=0, sticky="w")
        #### Selection
        ttk.Combobox(denoiser_method_line, state='readonly', value=self.image_denoisers, textvariable=self.image_denoiser, width=18).grid(row=0, column=1, sticky="w")
        
        ### Image Denoise level
        denoiser_level_line = ttk.Frame(denoiser_cfg_frame)
        denoiser_level_line.grid(pady=2, row = 1, column = 0, sticky="w")
        #### Title
        ttk.Label(denoiser_level_line, text = "Denoise level: ", width=14, anchor='w').grid(row=0, column=0, sticky="w")
        #### Input
        ttk.Entry(denoiser_level_line, textvariable = self.denoise_level, validate='key', validatecommand=(int_0_100_val, '%P'), width=14).grid(row=0, column=1, sticky="w")

        ## Stoma Detector Frame
        stoma_detector_cfg_frame = ttk.LabelFrame(adv_cfg_frame, labelwidget = ttk.Label(text = "Stoma detector"), padding=(4,2))
        stoma_detector_cfg_frame.grid(pady=2, row=1, column=0, sticky="w")
        ### Stoma Detector Model
        stoma_model_line = ttk.Frame(stoma_detector_cfg_frame)
        stoma_model_line.grid(pady=2, row = 0, column = 0, sticky="w")
        #### Title
        ttk.Label(stoma_model_line,text = "Model: ", width=8, anchor='w').grid(row=0, column=0, sticky="w")
        #### Selection
        ttk.Combobox(stoma_model_line, state='readonly', value=self.stoma_detectors, textvariable=self.stoma_detector, width=18).grid(row=0, column=1, sticky="w")
        ### Stoma Detector Threshold
        stoma_thres_line = ttk.Frame(stoma_detector_cfg_frame)
        stoma_thres_line.grid(pady=2, row = 1, column = 0, sticky="w")
        #### Title
        ttk.Label(stoma_thres_line,text = "Threshold: ", width=14, anchor='w').grid(row=0, column=0, sticky="w")
        #### Input
        ttk.Entry(stoma_thres_line, textvariable = self.stoma_thres, validate='key', validatecommand=(int_0_100_val, '%P'), width=14).grid(row=0, column=1, sticky="w")
        ### Min Stoma Size
        stoma_min_size_line = ttk.Frame(stoma_detector_cfg_frame)
        stoma_min_size_line.grid(pady=2, row = 2, column = 0, sticky="w")
        #### Title
        ttk.Label(stoma_min_size_line, text = "Min size: ", width=14, anchor='w').grid(row=0, column=0, sticky="w")
        #### Input & Unit
        min_stoma_size_frame = ttk.Frame(stoma_min_size_line)
        min_stoma_size_frame.grid(row=0, column=1, sticky="w")
        ttk.Entry(min_stoma_size_frame, textvariable = self.min_stoma_size, validate='key', validatecommand=(positive_float_val, '%P'), width=8).grid(row=0, column=0, sticky="w")
        ttk.Label(min_stoma_size_frame, text = "μm^2").grid(row=0, column=1, sticky="w")
        ### Max Stoma Size
        stoma_max_size_line = ttk.Frame(stoma_detector_cfg_frame)
        stoma_max_size_line.grid(pady=2, row = 3, column = 0, sticky="w")
        #### Title
        ttk.Label(stoma_max_size_line, text = "Max size: ", width=14, anchor='w').grid(row=0, column=0, sticky="w")
        #### Input & Unit
        max_stoma_size_frame = ttk.Frame(stoma_max_size_line)
        max_stoma_size_frame.grid(row=0, column=1, sticky="w")
        ttk.Entry(max_stoma_size_frame, textvariable = self.max_stoma_size, validate='key', validatecommand=(positive_float_val, '%P'), width=8).grid(row=0, column=0, sticky="w")
        ttk.Label(max_stoma_size_frame, text = "μm^2").grid(row=0, column=1, sticky="w")
        ### Max Stoma Aspect
        max_stoma_aspect_line = ttk.Frame(stoma_detector_cfg_frame)
        max_stoma_aspect_line.grid(pady=2, row = 4, column = 0, sticky="w")
        #### Title
        ttk.Label(max_stoma_aspect_line, text = "Max length/width ratio: ", width=20, anchor='w').grid(row=0, column=0, sticky="w")
        #### Input & Unit
        ttk.Entry(max_stoma_aspect_line, textvariable = self.max_stoma_aspect, validate='key', validatecommand=(positive_float_val, '%P'), width=8).grid(row=0, column=1, sticky="w")

        ## Cell divider Frame
        cell_divider_cfg_frame = ttk.LabelFrame(adv_cfg_frame, labelwidget = ttk.Label(text = "Pavement cell segmentator"), padding=(4,2))
        cell_divider_cfg_frame.grid(pady=2, row=2, column=0, sticky="w")
        ## Cell divider
        cell_method_line = ttk.Frame(cell_divider_cfg_frame)
        cell_method_line.grid(pady=2, row = 0, column = 0, sticky="w")
        ### Title
        ttk.Label(cell_method_line,text = "Method: ", width=8, anchor='w').grid(row=0, column=0, sticky="w")
        ### Selection
        ttk.Combobox(cell_method_line, state='readonly', value=self.cell_dividers, textvariable=self.cell_divider, width=18).grid(row=0, column=1, sticky="w")
        ## Divider Threshold
        cell_thres_line = ttk.Frame(cell_divider_cfg_frame)
        cell_thres_line.grid(pady=2, row = 1, column = 0, sticky="w")
        ### Title
        ttk.Label(cell_thres_line,text = "Threshold: ", width=14, anchor='w').grid(row=0, column=0, sticky="w")
        ### Input
        ttk.Entry(cell_thres_line, textvariable = self.divider_thres, validate='key', validatecommand=(int_0_100_val, '%P'), width=14).grid(row=0, column=1, sticky="w")
        ## Min Cell Size
        cell_min_size_line = ttk.Frame(cell_divider_cfg_frame)
        cell_min_size_line.grid(pady=2, row = 2, column = 0, sticky="w")
        ### Title
        ttk.Label(cell_min_size_line, text = "Min size: ", width=14, anchor='w').grid(row=0, column=0, sticky="w")
        ### Input & Unit
        min_cell_size_frame = ttk.Frame(cell_min_size_line)
        min_cell_size_frame.grid(row=0, column=1, sticky="w")
        ttk.Entry(min_cell_size_frame, textvariable = self.min_cell_size, validate='key', validatecommand=(positive_float_val, '%P'), width=8).grid(row=0, column=0, sticky="w")
        ttk.Label(min_cell_size_frame, text = "μm^2").grid(row=0, column=1, sticky="w")

        # Output Config Frame
        output_frame = ttk.LabelFrame(self.main_box, labelwidget = ttk.Label(text = "Output"), padding=(4,2))
        output_frame.grid(padx=8, pady=6, row = 2, column = 0)
        ### Mode Selection Title
        ttk.Label(output_frame,text = "Mode: ", width=6, anchor='w').grid(pady=2, row=0, column=0, sticky="w")
        ### Mode Selection Entry
        analyse_mode_selection = ttk.Combobox(output_frame, state='readonly', value=self.output_modes, textvariable=self.output_mode, width=18)
        analyse_mode_selection.bind("<<ComboboxSelected>>", self.mode_select)
        analyse_mode_selection.grid(pady=2, row=0, column=1, sticky="w")
        ## Pack Output File
        self.output_pack_checker = ttk.Checkbutton(output_frame, state=tk.DISABLED, text = "Pack output files into a zipfile", variable=self.output_zipfile, command=self.output_pack_select)
        self.output_pack_checker.grid(pady=2, row=1, column=0, columnspan=2, sticky="w")
        ## Output Path Title
        self.output_path_title = ttk.Label(output_frame, state=tk.DISABLED, textvariable=self.output_path_title_str, width=6, anchor='w')
        self.output_path_title.grid(pady=2, row = 2, column = 0,sticky="w")
        ## Output Path Entry
        self.output_path_entry = ttk.Entry(output_frame, state=tk.DISABLED, textvariable = self.output_path, width=21)
        self.output_path_entry.grid(pady=2, row = 2, column = 1, sticky="w")
        ## Browse Button
        self.output_path_button = ttk.Button(output_frame, state=tk.DISABLED, text = "Browse ..", command=self.select_output_folder_path, width=27)
        self.output_path_button.grid(pady=2, row = 3, column = 0, columnspan = 2)

        # Run Button
        ttk.Button(self.main_box,text = "Start", command = self.run, width=30).grid(padx = 8, pady=(0,6), row = 3, column = 0)

    def show_window(self):
        self.main_box.mainloop()
def main():
    leafnet_interface = leafnet_gui()
    leafnet_interface.show_window()

if __name__ == "__main__":
    main()