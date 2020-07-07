# ROITools
Developing Python tools for analyzing ROIs defined by masking operations or ImageJ. This would not be possible without the `Read-ROI` module developed by Hadrien Mary https://github.com/hadim/read-roi

*Disclaimer:* I am not a professional software developer by any means. I am a neurobiologist and I am hoping that the tools I make can be useful to others. As such, my code may be rough, and I appreciate all the feedback! Forgive me for the rough edges that my github profile will have while I learn this.


This is a work in progress. The methods were originally developed and used in the following publication 
Gao, R., et al. (2019). CNTNAP2 is targeted to endosomes by the polarity protein PAR3. European Journal of Neuroscience. https://doi.org/10.1111/ejn.14620

This file is an attempt to compile the methods into a generalizable program and to extend on their functionality.

The original implementation uses .tif images, but I am working on extending that to .nd2 and other bioformats-compatible images.

### Libraries used
numpy, scipy, scikit-image, pims (for bioformats capability)

## Development Files
### ROITools
This file contains all the functions and methods defined in the `ROITools` module, including the `ROI` and `ROI_Reader` classes. This will provide a suite of functions in both defining and working with ImageJ ROIs. This will use `bioformats` to open `.nd2`, `.tif`, and other imaging formats using their metadata.

### ROI_GUI
The file `ROI_GUI` houses the GUI development efforts. This project will use the classes included in `ROITools` in order to function.

### IJ ROI Classes.ipynb
This jupyter notebook is for testing methods and adding new features if IDE is insufficient.


## How to use the `ROITools` package
**Note: This is not yet functional**

#### Opening single ROI
class `ROI` takes an roi object opened using the `read_roi` class and makes it into a more useable form.

For simplicity, `ROI_Reader` can also open a single ROI.

#### Opening list of ROIs (.zip)
class `ROI_Reader` opens a .zip file containing imageJ rois and creates individual `ROI` objects. These objects can be retrieved with the `ROIs` class method

##### Example:

`MyROIs = ROI_Reader(roi_list.zip).ROIs()`

`myROIs` is a dict containing ROIs based on label (key)

#### Define an ROI to import using `ROI` or `ROI_Reader`:

## Functions to be Included in Final Product
1. Read ImageJ ROIs and .zip archives of ROIs. Define pixels within an ROI of four types: freehand, polygon, ellipse, rectangle
2. Batch process ROIs using the `ROI_Reader` class and the attached image
3. Correlation methods
3. Measure stacks and export .csv files and 

- Measure stack
- Measure correlations
- Descriptive statistics (Mean, Median, Grey values, Sum, Integrated Density)
- Save .csv files and return vectors for measurement
- Maybe create figures (go along with measure stack)

## Current status of the project
#### `class ROI`
##### Methods and Operations
- Working functions:
    - Initialize ROI: Define instance vars 
        1. `name`: ROI name (defined in ImageJ)
        2. `position`: contains a dictionary defining c, z, and t positions
        3. `kind`: type of ROI (eg: polygon, rectangle, ellipse, freehand)
        4. `mask_type`: defines whether masking will be applied to inside or outside of ROI
        5. `mask`: stores the masked image. Initialized as `None`
        6. `image`: stores the image that the ROI is applied to. Initialized as `None`
        7. `attribs`: holds all other features of the imported ROI that aren't explicitly used. Adds user-functionality if processes outside the scope of this module are desired.
    - `__setpixels()`: Define all pixels of the ROI
    - `ellipse()`, `polygon()`, `rectangle()`, `freehand()`: methods that define the pixels of the ROI. Called in `__init__()`. Currently all are functional except for `freehand()`.
- Not yet functional
    1. `freehand()`
    2. `measure_stack()`: return the measurement values in the stack.
        Input args: axis (c, z, t) must be made compatible with PIMS, measurements (single keyword or list of keywords)
    3. `crop_image()`: Reduce the size of the attached image
##### TO DO:
1. [] Implement `measure_stack()`: Measure all frames of a stack within the ROI. This method should include keywords to tell what measurements to perform and how to return it. The returned values should be a `DataFrame` or `Series` that can then be used in `Seaborn` or `Pyplot`
2. [] Implement `freehand()`
3. [] Implement `crop_image()`: reduce the size of the attached `ndarray` or `ndarray` sub-class by trimming based on the dimensions of the ROI
#### `class ROI_Reader`
##### Functions:
##### Fixes
