import math
import numpy as np
import cv2
import os
from PIL import Image
from PIL.ImageFilter import GaussianBlur

def sample_loader(source_size, target_size, sample_img, label_img, border_cutoff, stoma_weight):
    # Get the shape of samples
    img_r_size, img_c_size = sample_img.shape
    r_max_step = math.floor((img_r_size-(border_cutoff*2))/target_size)
    c_max_step = math.floor((img_c_size-(border_cutoff*2))/target_size)

    network_border = (source_size-target_size)//2

    img_left_up_pad = network_border - border_cutoff

    # Cut/Pad Left and Top
    label_img = label_img[border_cutoff:,border_cutoff:].astype(np.uint8)
    if img_left_up_pad > 0:
        sample_img = cv2.copyMakeBorder(sample_img.astype(np.uint8), img_left_up_pad,0,img_left_up_pad,0,cv2.BORDER_REFLECT)
    elif img_left_up_pad < 0:
        sample_img = sample_img[-img_left_up_pad:,-img_left_up_pad:].astype(np.uint8)
    else:
        sample_img = sample_img.astype(np.uint8)

    # Cut/Pad Right and Bottom
    img_r_size, img_c_size = sample_img.shape
    label_img = label_img[:target_size*(r_max_step),:target_size*(c_max_step)].astype(np.uint8)

    sample_target_r_len = target_size*(r_max_step) + source_size - target_size
    if sample_target_r_len > img_r_size:
        sample_img = cv2.copyMakeBorder(sample_img, 0,sample_target_r_len - img_r_size,0,0,cv2.BORDER_REFLECT)
    elif sample_target_r_len < img_r_size:
        sample_img = sample_img[:sample_target_r_len,:]
    
    sample_target_c_len = target_size*(c_max_step) + source_size - target_size
    if sample_target_c_len > img_c_size:
        sample_img = cv2.copyMakeBorder(sample_img, 0,0,0,sample_target_c_len - img_c_size,cv2.BORDER_REFLECT)
    elif sample_target_c_len < img_c_size:
        sample_img = sample_img[:,:sample_target_c_len]
    
    # Normalize
    sample_img_norm = sample_img.astype(float) / 255
    label_img_norm = label_img.astype(float) / 255

    # Sample_array, Sample_weight
    sample_array = np.zeros((r_max_step*c_max_step, source_size, source_size, 1),dtype=float)
    label_array = np.zeros((r_max_step*c_max_step, target_size, target_size, 2),dtype=float)
    multiply_area_list = list()

    for r in range (r_max_step):
        for c in range (c_max_step):
            block_id = (r * c_max_step) + c
            start_r = r * target_size
            start_c = c * target_size
            sample_array[block_id] = sample_img_norm[start_r:start_r+source_size,start_c:start_c+source_size,np.newaxis]
            label_array[block_id,:,:,0] = label_img_norm[start_r:start_r+target_size,start_c:start_c+target_size]
            if np.mean(label_array[block_id,:,:,0]) > 0.1:
                multiply_area_list.append(block_id)
    label_array[:,:,:,1] = 1-label_array[:,:,:,0]
    area_ids = list(range(r_max_step*c_max_step))
    for i in range(stoma_weight-1):
        area_ids.extend(multiply_area_list)
    return sample_array[area_ids], label_array[area_ids]

def load_sample_from_folder(image_dir, label_dir, source_size, target_size, validation_split, image_denoiser, foreign_neg_dir=None, args_duplicate_undenoise=False, args_duplicate_invert=False, args_duplicate_mirror=False, args_duplicate_rotate=False, resize_ratio = 1.0, stoma_weight = 1):

    if args_duplicate_undenoise:
        duplicate_undenoise = [True, False]
    else:
        duplicate_undenoise = [False]

    if args_duplicate_invert:
        duplicate_invert = [True, False]
    else:
        duplicate_invert = [False]

    if args_duplicate_mirror:
        duplicate_mirror = [True, False]
    else:
        duplicate_mirror = [False]

    if args_duplicate_rotate:
        duplicate_rotate = [0, 1, 2, 3]
    else:
        duplicate_rotate = [0]

    # Load images
    img_count_sum = 0
    validation_count_sum = 0
    foreign_count_sum = 0
    input_training_samples = list()
    input_training_labels = list()
    input_validation_samples = list()
    input_validation_labels = list()
    for image_name in os.listdir(image_dir):
        try: Image.open(os.path.join(image_dir, image_name)).close()
        except: continue
        image_path = os.path.join(image_dir, image_name)
        label_path = os.path.join(label_dir, image_name)
        if not os.path.exists(image_path): raise FileNotFoundError(image_path + " do not exist.")
        if not os.path.exists(label_path): raise FileNotFoundError(label_path + " do not exist.")


        sample_PIL_image = Image.open(image_path).convert('L')
        label_PIL_image = Image.open(label_path).convert('RGB')

        image_resize_target = (int(sample_PIL_image.size[0] * resize_ratio), int(sample_PIL_image.size[1] * resize_ratio))

        sample_PIL_image = sample_PIL_image.resize(image_resize_target, Image.ANTIALIAS)
        label_PIL_image = label_PIL_image.resize(image_resize_target, Image.ANTIALIAS)

        input_image = np.array(sample_PIL_image)
        input_label = np.array(label_PIL_image.filter(GaussianBlur(4)))[:,:,2]

        img_count_sum += 1
        current_image_validation = False
        if img_count_sum * validation_split > validation_count_sum:
            validation_count_sum += 1
            current_image_validation = True

        for undenoise_ops in duplicate_undenoise:
            if not undenoise_ops:
                input_image = image_denoiser.denoise(input_image)
            for invert_ops in duplicate_invert:
                if invert_ops:
                    input_image = 255 - input_image
                for mirror_ops in duplicate_mirror:
                    if mirror_ops:
                        input_image = input_image[:,::-1]
                        input_label = input_label[:,::-1]
                    for rotate_ops in duplicate_rotate:
                        input_image = np.rot90(input_image,rotate_ops)
                        input_label = np.rot90(input_label,rotate_ops)

                        image_stack, label_stack = sample_loader(source_size, target_size, input_image, input_label, 50, stoma_weight)

                        if not current_image_validation:
                            input_training_samples.append(image_stack)
                            input_training_labels.append(label_stack)
                        else:
                            input_validation_samples.append(image_stack)
                            input_validation_labels.append(label_stack)

    if foreign_neg_dir:
        for image_name in os.listdir(foreign_neg_dir):
            try: Image.open(os.path.join(foreign_neg_dir, image_name)).close()
            except: continue
            image_path = os.path.join(foreign_neg_dir, image_name)
            if not os.path.exists(image_path): raise FileNotFoundError(image_path + " do not exist.")

            input_image = np.array(Image.open(image_path).convert('L'))

            foreign_count_sum += 1

            for undenoise_ops in duplicate_undenoise:
                if undenoise_ops:
                    input_image = image_denoiser.denoise(input_image)
                for invert_ops in duplicate_invert:
                    if invert_ops:
                        input_image = 255 - input_image
                    for mirror_ops in duplicate_mirror:
                        if mirror_ops:
                            input_image = input_image[:,::-1]
                        for rotate_ops in duplicate_rotate:
                            input_image = np.rot90(input_image,rotate_ops)
                            input_label = np.zeros(input_image.shape, dtype=np.uint8)

                            image_stack, label_stack = sample_loader(source_size, target_size, input_image, input_label, 50, stoma_weight)
                            input_training_samples.append(image_stack)
                            input_training_labels.append(label_stack)
    return input_training_samples, input_training_labels, input_validation_samples, input_validation_labels, img_count_sum, validation_count_sum, foreign_count_sum