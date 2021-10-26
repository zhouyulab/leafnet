import importlib
from PIL import Image
import os
import numpy as np
from collections import Counter
import skimage.io as plt
from skimage import draw
import math
import cv2
from .stoma_detector.stoma_detector import stoma_detector

class leafnet_image_parser:
    def __init__(self, stoma_detector_model_name, cell_divider, divider_thres, stoma_thres, min_cell_size, min_stoma_size, max_stoma_size, max_stoma_aspect, base_resolution):
        # Load Stoma detector
        self.stoma_detector = stoma_detector(
            stoma_thres = stoma_thres / 100,
            min_stoma_size = min_stoma_size * base_resolution * base_resolution,
            max_stoma_size = max_stoma_size * base_resolution * base_resolution,
            max_stoma_aspect = max_stoma_aspect, 
            model_name = stoma_detector_model_name
        )
        self.cell_divider = importlib.import_module(
            f'.cell_divider.{cell_divider}.divider',
            "leafnet.leafnet_libs",
        ).divider(
            min_cell_size=min_cell_size * base_resolution * base_resolution,
            divider_thres=divider_thres,
        )
        self.base_resolution = base_resolution

    def process_image(self, input_image):
        # Load Properties from Model
        corrected_stoma_list = self.stoma_detector.detect_stomas(input_image)
        # Divide Cells
        area_id_set, area_coverage_array = self.cell_divider.divide_cell(input_image, corrected_stoma_list)
        return area_id_set, area_coverage_array, corrected_stoma_list
