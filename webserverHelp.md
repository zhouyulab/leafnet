# Help Page for LeafNet Webserver

## LeafNet Introduction 

The morphological features of leaves for stomata and pavement cells are important traits in plant studies. LeafNet is built to automatically and accurately analyze light microscope images to detect stomata and segment pavement cells, and quantify their morphological features such as counts and sizes.

## Should I download a standalone version?

We recommend you to use this webserver to try LeafNet. However, in following situations, we suggest users to download a standalone version.

* LeafNet webserver only has models to detect stomata in images of leaves from *Arabidopsis thaliana*. The Standalone version is needed if you want to training a new model to detect stomata from other sources, w/o transfer learning.
* LeafNet webserver only accepts one image per task. Standalone version can analyze images in a folder or a zipfile recursively.
* LeafNet webserver has a limited speed (slower than most Desktop computers and recent laptops), as the server hosts other web services. Standalone version is needed if you want to enhance the speed.

See [Docs](./) to install and use a standalone version of LeafNet.

## Webserver Usage

### Submit a task

1. Click "Submit a new task!" to initiate a task. We suggest you to [Create an account](./) to manage your task list.
2. Upload your image as input file, write your task name, and fill the e-mail to get notification upon completion.
3. Set basic configuration (critical for performance)
    1. Image resolution: the resolution of input image (pixel per μm).
    2. Background type: the type of the image background (Bright for bright field images, dark for fluorescent images).
4. Set advanced configuration (optional)
    * Image denoiser
        1. Method: choose a denoiser to denoise input image (choose None to use raw image).
        2. Level: strength of denoizing (0-100), increasing it if your image is noisy.
    * Pavement cell segmentator
        1. Method: choose a Cell divider to segment pavement cells.
        2. Threshold: 0-100, higher threshold avoid false cell borders from noises, but might ignore blur ones.
        3. Min size: (μm^2), set the threshold to ignore pavement cells smaller than this size. 
    * Stoma detector
        1. Method: choose a stoma detection model to detect stomata.
        2. Threshold: 0-100, higher threshold decreases false positive rate, but increases false negative rate. 
        3. Min size: (μm^2), stomata smaller than this threshold will be ignored. 
        4. Max size: (μm^2), Stomata larger than this threshold will be ignored. 
        5. Max length/width ratio: stomata with a larger length/width ratio will be ignored.
5. Click "Create" to run your task. The result page is refreshing periodly to check the running state, and you will receive a notification email when the job is completed.

### Download results

1. When the job is complete, you will receive a notification email with a link to the result page.
2. Taking [our example result page](./) for example, two images, and a data table are generated. 
   1. Preview image: visualized image segmentation. Different pavement cells are marked with different colors, and stomata are marked with blue.
   2. Annotation image: image segmentation file for further analysis. The cell walls are marked with green line and stomata are marked with blue ellipse. This image could be used as a fluorescent image for other pipelines.
   3. Statistic data table: Collected statistical data from the segmentation for the input image.
3. You can download each file separately or download them as a zipfile.

## Contacts

If you have any question or suggestion, please contact Dr. Yu Zhou (yu.zhou@whu.edu.cn) at Wuhan University.
