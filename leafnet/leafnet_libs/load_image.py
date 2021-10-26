from typing import Callable, Tuple
from PIL import Image
import numpy as np
from typing import Callable

def load_image(image_path:str, res_ratio:float, background_color:bool, preprocesser:Callable = None) -> Tuple[np.ndarray, np.ndarray]:
    '''
    Load a image to array according to the given parameters.
    args:
        image_path - Path of the image to load.
        res_ratio - The ratio to resize the image to fit the target resolution of stoma detection model.
        background_color - Boolean value, true for dark cell wall on bright background, false for bright cell wall on dark background.
        preprocesser - Function to further procress the image.
    return:
        List containing pathes for input files.
    '''
    
    # Open image, convert to gray scale
    input_image = Image.open(image_path).convert('L')
    # Resize image according to resolution ratio
    if res_ratio != 1.0:
        input_image = input_image.resize((int(input_image.size[0] * res_ratio), int(input_image.size[1] * res_ratio)), Image.ANTIALIAS)

    input_image_array = np.array(input_image)
    input_raw = input_image_array.copy()
    # True: Bright Background, False: Dark Background
    if background_color == False:
        input_image_array = 255 - input_image_array
    # Denoise
    if preprocesser is not None:
        input_image_array = preprocesser(input_image_array)
    
    return input_image_array, input_raw