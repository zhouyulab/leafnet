# LeafNet

## Description

LeafNet is a convenient tool that can robustly localize stomata and segment pavement cells for light-microscope images of leaves.

## Installation

LeafNet has been tested under Linux, Mac OS Catalina (10.15), and Windows 10 with Python 3.6.8. The RAM is required to be larger than 4G. GPU is optional, and should be Nvidia Graphic Card with [Compute Capability](https://developer.nvidia.com/cuda-gpus) >= 3.5. (GPU acceleration is not supported in macOS.)

### Install with Conda (Recommended)
  ```bash
  # Create a python 3.6 enviorment for installation (suggested)
  conda create -n leafnet_env python=3.6
  conda activate leafnet_env

  # Install LeafNet CPU version
  conda install -c anaconda -c conda-forge -c zhouyulab leafnet
  # or install GPU version
  conda install -c anaconda -c conda-forge -c zhouyulab leafnet-gpu

  # Install ITK 5.2 if you wants to compare LeafSeg with ITK Morphological watershed
  pip install itk==5.2

  # then you can use LeafNet now
  leafnet-gui
  # or with command-line
  leafnet-cli
  ```

### Install manually

* Clone LeafNet GitHub repo
  ```bash
  git clone https://github.com/zhouyulab/leafnet.git
  cd leafnet
  ```

* Compiling C++ plugins (Optional)

  * We **STRONGLY** suggest users to use our pre-compiled dynamic libraries on x86-64 compatible platform.
  * If you must compile these libs locally (e.g. to run LeafNet on arm64 based platform), use clang == 6.0.0 with c++ 14 standard and -O2 optimization for linux, and Visual Studio 2019 for windows.
  * Compile the source code in **.\CppSourceCode**, and replace **.\leafnet\leafnet_libs\cell_divider\LeafSeg\edt_model.dll(.so, .osx.so)** by compiled file.
  ```bash
  clang++ {cpp files} -shared -fPIC -O2 -std=c++14 -o {compiled}
  ```
* Install System dependencies
  >If you are running LeafNet on a linux server without graphicial interface, you may need to manually install libsm6 (dependency of opencv) as below.

  ```bash
  apt-get install libsm6
  ```

* Install Python dependencies
  > You need to install python 3.6.8 first. If you are using GPU, cuDNN 7.4 and CUDA 10 are also needed.

  ```bash
  python -m venv {path to your venv dir}  # create and a new venv
  {path to your venv dir}/Scripts/activate  # activate venv (Windows)
  {path to your venv dir}/bin/activate  # activate venv (Linux)

  # install dependencies for CPU
  pip install -r requirements.txt
  # install dependencies for GPU
  pip install -r requirements_gpu.txt
  ```
  
* You can execute LeafNet now.
  ```bash
  cd {path to cloned leafnet repo}
  # Lanuch LeafNet with graphic interface
  python -m leafnet.leafnet_gui
  # or with command-line
  python -m leafnet.leafnet_cli
  ```

## Usage

* Try LeafNet on the LeafNet website
  > Check the [LeafNet Webserver](http://leafnet.whu.edu.cn).

### Leaf epidermal imaging
* We suggest users to prepare a leaf epidermal peel, and take micrographs under 200x magnification. Users could take sample.png in this repo for a good example.
* LeafNet can also analyze stained leaf epidermis sample, max intensity z-projection of confocal image stack, and other types of images. Users could take the representative images in LeafNet article for example.
* Follow the instructions to select the best configuration for your images.

### LeafNet configuration

### Input configuration
Input configuration contains several options to describe input files.

* Input path (-i input_path): the file, or folder, or archive of images.
* Recursive (-r): Input path is a folder, and all images in this folder (including sub directories) will be processed. The output files will have the same structure with input.
* Zipfile (-z):  Input path is a zipfile, and all images in this zipfile will be processed. The output files will have the same structure with input. We strongly suggest users to use English characters for file names.

### Basic configuration
Basic configuration contains options critical for performance.

* Image resolution (--res 2.17): the resolution (px/μm) of the input image. Input image will be resized to the same resolution of of our training samples according to this value. By default, images are resized to 2.17 px/μm when using StomaNet.
* Background type (--bg Bright|Dark): the type of image background. We use "Bright" for bright field images with bright background and dark cell walls, and "Dark" for fluorescent images with dark background and bright cell walls. Images with dark background will be inverted before processing.

### Output setting
Output configuration defines the files LeafNet to generate. 

* Output path (-o output_path): the folder to save results. LeafNet create a folder if the folder doesn't exist, and if the folder exists, LeafNet will **only** continue if the folder is empty to avoid overwritting existing files.
* Pack output (-p): output as a zipfile. When using with -p, -o means output zipfile instead of output folder.
* Output mode: If you are using CLI or GUI, an output mode must be selected. If you use web interface, all results are generated including the preview image, annotation and statistic files.
  * Interactive (-m INTERACTIVE): Directly show the preview image, in which different cells are marked with different colors.
  * Save Image (-m GRAPH): Save the preview image to output folder.
  * Save Annotation (-m ANNOTATE): Save the annotation image to output folder, in which cell walls are marked with green color, and stomata are marked with blue color.
  * Save Statistic (-m STATISTIC): Save the statistic data into a txt file in output folder, and save a preview image for further check.
  * Save Statistic (-m ALL): Save the preview image, annotation image and statistic data in output folder.

### Advanced configuration

For bright field images of *Arabidopsis thaliana* leaf epidermal peel like sample.png in this repo, LeafNet perform well without changing advanced configuration. To use LeafNet on different species and imaging methods, please use the following instructions to optimize the performance on providied samples. A small sample set could be used for calibrating these parameters.

#### Image denoiser

* Image denoiser (--dn="PeeledDenoiser"): Select from "PeeledDenoiser", "StainedDenoiser", or none. This is the algorithm for input image denoising. Use "Peeled Denoiser" for unstained leaf epidermal peel sample and max intensity z-projection of confocal stack, and use "Stained Denoiser" for stained leaf epidermis sample. We also suggest users to try "Stained Denoiser" as default for samples not tested with LeafNet.
* Denoise level (--dn_lv=50): Strength of the denoiser. From 0 (not denoised) to 100 (heavyly denoised), increasing this value might be helpful to deal with noisy images.

#### Stoma detector

* Stoma detector (--sd "StomaNet"): Select from "StomaNet", "StomaNetConfocal", "StomaNetUniversal", and "None". This is the model to recognize stoma. Use "StomaNet" for bright field images of *Arabidopsis thaliana* leaf epidermal peel and other similar images, use "StomaNetConfocal" for max intensity z-projection of confocal stack, and use "StomaNetUniversal" for all other conditions. We also suggest to try StomaNetUniversal when the image is too noisy for StomaNet/StomaNetConfocal to perform well. Users could also use "None" to skip stomata detection.
* Min size (--min_ss=20): Stomata smaller than this size (μm^2) will be ignored.
* Max size (--max_ss=1500): Stomata larger than this size (μm^2) will be ignored.
* Max length/width ratio (--max_sa=5): Stomata with a length/width ratio above this value will be deleted.

#### Pavement cell segmentator

* Cell divider (--cd="LeafSeg"): "LeafSeg" or "ITKMorphologicalWatershed", the algorithm to segment cells. We suggest to use LeafSeg for all conditions, we added ITK Morphological Watershed here just for comparison.
* Divider threshold (--sd_ts=60): For LeafSeg, threshold means the minimum score for a cell boundary to be kept in the segmentation, from 0 (all boundaries will be kept) to 100 (only boundaries with full score will be kept). For ITK Morphological Watershed, this value is directly used as segmentation level.
* Min cell size (--min_cs=85): Cells smaller than this size (μm^2) will be ignored and merged into nearby cells.

#### Run LeafSeg alone

* LeafSeg can be run in standalone mode with command "leafnet-cli --sd None --cd LeafSeg" by skipping stomata detection. 

## Training models

StomaNet could be trained for images from other species, or images taken from other methods, to detect stomata. The pavement cell segmentators are not trainable currently.

### Training data

The process below is a suggested way to generate annotation for image. Refer to the dataset provided in the LeafNet article for a good example.

1. Preparing an image dataset.
2. (Optional) Use LeafNet to generate segmentation as initial annotation.
3. Load sample image and annotation image in the GIMP or Photoshop.
4. Put annotation image in a layer on the top of sample image. (If step 2 skipped, create an empty layer.)
5. Set the opacity of the annotation layer to 50%.
6. Correct stomata with 100 hardness and (0,0,255) color on the annotation layer.
7. Set the opacity of annotation layer back to 100%.
8. Set background of the image to black (0,0,0).
9.  Remove sample image layer.
10. Flatten image, save corrected annotation.

### Model training

* Model trainer is not included in the conda package. Users could install the conda package for training requirements, and clone this git repo for training scripts.
* Training script:
  * StomaNet: StomaNetTrainer/train_model.py

* Parameters:
  * Image directory (-i): the folder containing sample images.
  * Label directory (-l): the folder containing labeled images.
  * Model output path (-o): The path to save the trained model.
  * Training sample resolution (--sample_res): The resolution (px/μm) for training samples.
  * Model resolution (--target_res, optional): The target resolution (px/μm) of the trained model. Training samples will be automatically resized to match this resolution. (default value: 2.17)
  * Epochs (-e epoch, optional): Each epoch means training the model on all training data once. (default value: 10)
  * Foreign negative sample directory: (-f, optional): The folder containing the foreign negative images. Foreign negative images are images from completely different sources containing no stoma, such like drawings, daily photos, and animal cells. These samples might prevent the model from overfitting. No foreign negative sample will be added without -f.
  * Base model path (-m, optional): Path to a base model for transfer learning, whose weights will be used for initialization. We suggest to use StomaNetUniversal shipped with LeafNet as the base model for custom training. Other models could be used, but this model must be a StomaNet based model (i.e. have the same structure with StomaNet). The model will be randomly initialized without -m.
  * GPU count (--gpu_count, optional): Argument passed to tensorflow's multi_gpu_model, Use 1 to disable multi_gpu feature for single gpu training or cpu training.(default value: 1)
  * Batch size (--batch_size, optional): The batch size used for batch training, reduce this value if you ran out of video memory.(default value: 40)
  * Validation split (--validation_split, optional): Images will be split into training and validation with this ratio. This step is applied before sample duplication. (default value: 0.2)
  * Use dynamic batch size (--dynamic_batch_size): With this argument, the training procedure will be seperated to 5 training period with increasing batch sizes.
  * Duplicate sample by adding undenoised image (--duplicate_undenoise): With this argument, input images will be duplicated by 2x by using denoised and raw images together.
  * Duplicate sample by adding inverted image (--duplicate_invert): With this argument, input images will be duplicated by 2x by adding inverting images.
  * Duplicate sample by adding mirrored image (--duplicate_mirror): With this argument, input images will be duplicated by 2x by adding mirrored images.
  * Duplicate sample by adding rotated image (--duplicate_rotate): With this argument, input images will be duplicated by x by adding rotated(90, 180 and 270 degrees) samples.
  
### Use LeafNet with CNNwall

* Currently, CNNwall is provided in a seperate directory (CNNwall) in LeafNet repo.
* To segment images with CNNwall:
1. Use LeafNet regularly to identify stomata.
2. Use *CNNwall/denoise_image_for_cnnwall.py* to denoise the input images and the images will be converted to tiff for PlantSeg.
  ```bash
  python CNNwall/denoise_image_for_cnnwall.py [PathToInputFolder] [PathToDenoisedOutput]
  ```
3. Use PlantSeg with the model *CNNwall/CNNwallModel* to generate predictions.
4. Use *CNNwall/prediction_h5_to_png.py* to convert predictions to png images for LeafNet.
  ```bash
  python CNNwall/denoise_image_for_cnnwall.py [PredictionFolderOfPlantSeg] [PathToPNGOutput]
  ```
5. Use LeafNet to segment pavement cells on predictions.
  > Set background type to Dark, image denoiser to none, and stoma detector to None.
6. Combine the results of stomata detection and pavement cell segmentation.

## Contacts

If you have any questions or suggestions, please contact Shaopeng Li (lishaopeng@whu.edu.cn) or Dr. Yu Zhou (yu.zhou@whu.edu.cn) at Wuhan University.

