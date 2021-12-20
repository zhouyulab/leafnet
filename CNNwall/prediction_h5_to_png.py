import h5py
from PIL import Image
import numpy as np
import os
import sys
from skimage.exposure import adjust_gamma
import h5py

input_dir = sys.argv[1]
output_dir = sys.argv[2]
postfix = r"_predictions.h5"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for file_name in os.listdir(input_dir):
    if file_name.endswith(postfix):
        with h5py.File(os.path.join(input_dir, file_name)) as input_h5file:
            prediction_array = adjust_gamma(np.array(input_h5file["predictions"])[0,0,:,:], 0.4545)
            Image.fromarray((prediction_array*255).astype(np.uint8)).save(os.path.join(output_dir, file_name[:-len(postfix)]+".png"))