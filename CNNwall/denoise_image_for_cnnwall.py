from PIL import Image
import numpy as np
import os
import sys
from StainedDenoiser import denoiser

input_dir = sys.argv[1]
output_dir = sys.argv[2]

if not os.path.exists(output_dir):
    os.makedirs(output_dir)
current_denoiser = denoiser.denoiser()
for file_name in os.listdir(input_dir):
    try:
        input_array = np.array(Image.open(os.path.join(input_dir, file_name)).convert('L'))
        Image.fromarray(current_denoiser.denoise(input_array)).save(os.path.join(output_dir, os.path.splitext(file_name)[0]+".tiff"))
    except:
        pass