import numpy as np
import math
from scipy.ndimage.filters import gaussian_filter
from sklearn.cluster import DBSCAN
from skimage import draw
from skimage.filters import gaussian
import cv2
import os
from tensorflow.keras.models import load_model

def sample_loader(source_size, target_size, sample_img):
    # Get the shape of samples
    img_r_size, img_c_size = sample_img.shape

    r_max_step = math.ceil(img_r_size/target_size)
    c_max_step = math.ceil(img_c_size/target_size)

    network_border = (source_size-target_size)//2

    expand_r_size = (target_size*(r_max_step))+(network_border*2)
    expand_c_size = (target_size*(c_max_step))+(network_border*2)

    img_r_pad = expand_r_size-img_r_size-network_border
    img_c_pad = expand_c_size-img_c_size-network_border
    image_padded = cv2.copyMakeBorder(sample_img.astype(np.uint8), network_border,img_r_pad,network_border,img_c_pad,cv2.BORDER_REFLECT)

    # Sample_array, Sample_weight
    sample_array = np.zeros((r_max_step*c_max_step, source_size, source_size, 1),dtype=float)
    for r in range (r_max_step):
        for c in range (c_max_step):
            block_id = (r * c_max_step) + c
            start_r = r * target_size
            start_c = c * target_size
            sample_array[block_id] = image_padded[start_r:start_r+source_size,start_c:start_c+source_size,np.newaxis].astype(float) / 255
    return sample_array, r_max_step, c_max_step

def generate_heatmap(normalized_sample_image, model_object, model_input_shape, model_output_shape):
    # Get the shape of samples
    img_r_size, img_c_size = normalized_sample_image.shape
    # Input Image
    samples, r_max_step, c_max_step = sample_loader(model_input_shape, model_output_shape, normalized_sample_image)
    # Use the Model to Predict the Stomas
    results = model_object.predict(samples)[:,:,:,0]
    # Rearrange the Results to Get Heatmap of Stoma Distribution
    total_list = list()
    for r_step in range (r_max_step):
        c_list = list()
        for c_step in range (c_max_step):
            c_list.append(results[c_step+r_step*c_max_step,:,:])
        total_list.append(np.concatenate(c_list, axis = 1))
    result_array = np.concatenate(total_list, axis = 0)[:img_r_size,:img_c_size]

    return result_array

def clusting_heatmap(heatmap_array, stoma_size_correction_ratio):
    # Generate a List of Dots With More Than 50% Possibility of Being in a Stoma
    stoma_dots = np.where(heatmap_array>0.70)
    dots_score = heatmap_array[stoma_dots]
    dots_arr = np.array(stoma_dots).transpose()
    if dots_arr.shape[0] == 0:
        return list()
    # Cluster Dots
    db = DBSCAN(eps=5, min_samples=60)
    db.fit(dots_arr, sample_weight=dots_score)
    stoma_list = list()
    # label -1 means Noise, removed.
    for label in np.unique(db.labels_):
        if label != -1:
            dots_id = np.where(db.labels_==label)
            stoma_dots = dots_arr[dots_id]
            stoma_scores = dots_score[dots_id]
            stoma_list.append(stoma_pca(stoma_dots, stoma_scores, stoma_size_correction_ratio))
    return stoma_list


def stoma_pca(stoma, score, stoma_size_correction_ratio):
    score_sum = np.sum(score)
    stoma_size = len(stoma)*stoma_size_correction_ratio
    # dots_array: (y_axis, x_axis)
    dots_array = np.array(stoma, dtype=float)
    # Get Stoma Center By weighted Average
    stoma_center = (dots_array.transpose()*score).sum(axis=-1)/score_sum
    pca_center, pc_array, pc_weights = cv2.PCACompute2(dots_array, np.empty((0)))
    stoma_angle = -math.atan2(pc_array[0,1], pc_array[0,0])
    stoma_aspect = (pc_weights[0,0] / pc_weights[1,0])**0.5
    # Stoma Data From Size
    stoma_length = ((stoma_size/math.pi)*stoma_aspect)**0.5
    stoma_width = (stoma_length/stoma_aspect)
    return [int(stoma_center[0]), int(stoma_center[1]), int(stoma_length), int(stoma_width), stoma_angle]

class stoma_detector:
    def __init__(self, stoma_thres, min_stoma_size, max_stoma_size, max_stoma_aspect, model_name):
        if model_name == "None":
            self.enabled = False
        else:
            self.enabled = True
            self.model_object = load_model(os.path.join(os.path.dirname(__file__), r'models', model_name + r'.model'))
            self.model_input_shape = self.model_object.input_shape[1]
            self.model_output_shape = self.model_object.output_shape[1]
            self.stoma_size_correction_ratio = 0.85

            self.stoma_thres = stoma_thres
            self.min_stoma_size = min_stoma_size
            self.max_stoma_size = max_stoma_size
            self.max_stoma_aspect = max_stoma_aspect

    def detect_stomas(self, input_image):
        if not self.enabled:
            return list()
        # Generate Heatmap of Stoma Distribution
        result_array = generate_heatmap(input_image, self.model_object, self.model_input_shape, self.model_output_shape)
        result_array = gaussian_filter(result_array, 2)
        
        # Use PCA on Stoma List(dot list) to Generate PCA Stoma List[stoma_center_0, stoma_center_1, stoma_length, stoma_width, stoma_angle]
        stoma_list = clusting_heatmap(result_array, self.stoma_size_correction_ratio)

        corrected_stoma_list = list()

        for stoma in stoma_list:
            corrected_stoma = stoma
            stoma_mask = np.zeros(result_array.shape, dtype=bool)
            draw.set_color(stoma_mask,draw.ellipse(corrected_stoma[0], corrected_stoma[1], corrected_stoma[2], corrected_stoma[3], rotation=-corrected_stoma[4]),True)
            stoma_score = np.mean(result_array[np.where(stoma_mask)])
            stoma_size = int(3.14*corrected_stoma[2]*corrected_stoma[3])
            if ((stoma_size >= (self.min_stoma_size)) and 
            (stoma_size < (self.max_stoma_size)) and 
            (stoma_score >= self.stoma_thres) and 
            ((max(corrected_stoma[2], corrected_stoma[3]) / min(corrected_stoma[2], corrected_stoma[3])) < self.max_stoma_aspect)):
                corrected_stoma_list.append(corrected_stoma)
        return corrected_stoma_list