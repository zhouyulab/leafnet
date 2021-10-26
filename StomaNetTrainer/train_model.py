import argparse
import math

arg_parser = argparse.ArgumentParser(description="StomaNet model trainer.")
## Input
arg_parser.add_argument("-i", dest="image_dir", type=str, required=True, help="The folder containing training image.")
arg_parser.add_argument("-l", dest="label_dir", type=str, required=True, help="The folder containing training annotation.")
arg_parser.add_argument("-o", dest="save_path", type=str, required=True, help="The path to save trained model.")
arg_parser.add_argument("--sample_res", dest="sample_res", type=float, required=True, help="The resolution (px/μm) for training samples.")
arg_parser.add_argument("--target_res", dest="target_res", default=2.17, type=float, help="The target resolution (px/μm) of the trained model. Training samples will be automatically resized to match this resolution.(default value: 2.17)")

arg_parser.add_argument("-e", dest="epoch", type=int, default=10, help="The count of epochs,(a epoch means training the model on all training data once) (default value: 10)")
arg_parser.add_argument("-f", dest="foreign_neg_dir", type=str, help="(optional)The folder containing foreign negative images (images without stomata), foreign negative images will NOT be resized according to resolution.")
arg_parser.add_argument("-m", dest="stoma_net_model_path", type=str, help="The source model for transfer training (must be another model based on StomaNet).")

arg_parser.add_argument("--gpu_count", dest="multi_gpu", type=int, default=1, help="Tensorflow multi_gpu_model argument, use 1 for cpu or one gpu.(default value: 1)")
arg_parser.add_argument("--batch_size", dest="batch_size", type=int, default=40, help="Batch size of training.(default value: 40)")
arg_parser.add_argument("--validation_split", dest="validation_split", type=float, default=0.2, help="Images will be split into training and validation with this ratio BEFORE sample duplication.(default value: 0.2)")
arg_parser.add_argument("--dynamic_batch_size", dest="dynamic_batch_size", action="store_true", help="Seperate epochs to 5 training period with increasing batch sizes.")
arg_parser.add_argument("--duplicate_undenoise", dest="duplicate_undenoise", action="store_true", help="Duplicate samples(*2) by using denoised and raw images together.")
arg_parser.add_argument("--duplicate_invert", dest="duplicate_invert", action="store_true", help="Duplicate samples(*2) by using inverting images.")
arg_parser.add_argument("--duplicate_mirror", dest="duplicate_mirror", action="store_true", help="Duplicate samples(*2) by using mirrored images.")
arg_parser.add_argument("--duplicate_rotate", dest="duplicate_rotate", action="store_true", help="Duplicate samples(*4) by rotating samples 90, 180, 270 degree.")

arg_parser.add_argument("--stoma_weight", dest="stoma_weight", type=int, default=1, help="Image areas containing stomata will be mulitplied by this factor.(default value: 1)")

## Parse Args
args = arg_parser.parse_args()

if args.epoch <= 0:
    raise ValueError(f"Epoch must be an intenger above zero!") 

image_dir = args.image_dir
label_dir = args.label_dir
save_path = args.save_path
if not save_path.endswith(".model"): save_path += ".model"

sample_res = args.sample_res
target_res = args.target_res

total_epoch = args.epoch
final_batch_size = args.batch_size
dynamic_batch_size = args.dynamic_batch_size
foreign_neg_dir = args.foreign_neg_dir
stoma_net_model_path = args.stoma_net_model_path
multi_gpu = max(1, args.multi_gpu)

validation_split = args.validation_split

if final_batch_size <=0:
    raise ValueError("Batch size must be above zero.")
if total_epoch <=0:
    raise ValueError("Epoch must be above zero.")
if validation_split <= 0 or validation_split >= 1: 
    raise ValueError("Validation split must be above zero and under one.")

args_duplicate_undenoise=args.duplicate_undenoise
args_duplicate_invert=args.duplicate_invert
args_duplicate_mirror=args.duplicate_mirror
args_duplicate_rotate=args.duplicate_rotate

duplicate_times = 1
if args_duplicate_undenoise: duplicate_times *= 2
if args_duplicate_invert: duplicate_times *= 2
if args_duplicate_mirror: duplicate_times *= 2
if args_duplicate_rotate: duplicate_times *= 4

stoma_weight = args.stoma_weight
if stoma_weight < 1:
    raise ValueError("Stoma weight must be an intenger above zero.")

#Ignore tensorflow import warnings
# import warnings
# warnings.filterwarnings("ignore")

import numpy as np
import os
import random

import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras import optimizers, backend

from gegl_denoise.denoiser import denoiser
from sample_loader import load_sample_from_folder
from stoma_net_models import build_stoma_net_model

from tensorflow.keras.utils import multi_gpu_model

np.random.seed(0)
random.seed(0)
tf.set_random_seed(0)
sess = tf.Session(graph=tf.get_default_graph())
backend.set_session(sess)

# Compile model
print("Compiling model...")
training_model = build_stoma_net_model(small_model=True, sigmoid_before_output=True)
source_size = int(training_model.input.shape[1])
target_size = int(training_model.output.shape[1])

# Load Weight if used
if stoma_net_model_path:
    print("Loading weights...")
    # Not using load_weights to avoid tensorflow model issue 2676
    reference_model = load_model(stoma_net_model_path)
    training_model.set_weights(reference_model.get_weights())

# Load Samples
image_denoiser = denoiser()

input_training_samples, input_training_labels, input_validation_samples, input_validation_labels, img_count_sum, validation_count_sum, foreign_count_sum = load_sample_from_folder(image_dir, label_dir, source_size, target_size, validation_split, image_denoiser, foreign_neg_dir, args_duplicate_undenoise, args_duplicate_invert, args_duplicate_mirror, args_duplicate_rotate, target_res/sample_res, stoma_weight)

print("Collected "+str(img_count_sum)+" sample images("+str(img_count_sum-validation_count_sum)+" for training, "+str(validation_count_sum)+" for validation) and "+str(foreign_count_sum)+" foreign negative images.")
print("Input images are duplicated by *" + str(duplicate_times))

training_sample_array = np.concatenate(input_training_samples, axis=0)
del input_training_samples
training_label_array = np.concatenate(input_training_labels, axis=0)
del input_training_labels
validation_sample_array = np.concatenate(input_validation_samples, axis=0)
del input_validation_samples
validation_label_array = np.concatenate(input_validation_labels, axis=0)
del input_validation_labels

val_data = (validation_sample_array, validation_label_array)

optm=optimizers.SGD(lr=0.001, momentum=0.9, nesterov = True)
# optm = optimizers.Nadam()

exec_model = None
if multi_gpu > 1:
    exec_model = multi_gpu_model(training_model, gpus=multi_gpu)
else:
    exec_model = training_model
exec_model.compile(loss='kld', optimizer=optm, metrics=['accuracy'])

if dynamic_batch_size:
    # Get Epochs
    epoch_per_step = np.zeros(5, dtype=int)
    epoch_per_step[:] = total_epoch//5
    if total_epoch%5 != 0:
        epoch_per_step[-(total_epoch%5):] += 1
    # Get batch_sizes
    batch_sizes = list()
    batch_size_increment = float(final_batch_size) / 5
    batch_sizes.append(math.ceil(batch_size_increment*1))
    batch_sizes.append(math.ceil(batch_size_increment*2))
    batch_sizes.append(math.ceil(batch_size_increment*3))
    batch_sizes.append(math.ceil(batch_size_increment*4))
    batch_sizes.append(math.ceil(batch_size_increment*5))
    # Train
    for i in range(5):
        exec_model.fit(training_sample_array, training_label_array, epochs = epoch_per_step[i], validation_data = val_data, batch_size=batch_sizes[i])
else:
    exec_model.fit(training_sample_array, training_label_array, epochs = total_epoch, validation_data = val_data, batch_size=final_batch_size)

saving_model = build_stoma_net_model(small_model=False, sigmoid_before_output=False)
saving_model.set_weights(training_model.get_weights())
saving_model.save(save_path)
with open(save_path[:-6]+".res", "w") as model_meta: model_meta.write(str(target_res))