# -*- coding: utf-8 -*-
"""
Created on Mon Sep  3 07:36:22 2018

PURPOSE OF THIS PROJECT FILE

This is a work in progress. It was originally developed and used in publication 
Gao, R., et al. (2019). CNTNAP2 is targeted to endosomes by the polarity protein PAR3. European Journal of Neuroscience. https://doi.org/10.1111/ejn.14620

This file is an attempt to compile the methods into a generalizable program and to extend on their functionality.

The original implementation uses .tif images, but I am working on extending that to .nd2 and other bioformats-compatible images.

Features:
1. ROI management
    - Import and use IJ ROIs
    - Measure stacks through time and z
    - Batch operations with filename and ROI name matching

2. Colocalization - THIS SHOULD BE A SEPARATE FILE THAT imports ROITools
    - Pearson/Spearman
    - Custom thresholding (Par3 method)
    
2. Measuring stack and time series
    - Measure ImageJ ROIs through time and z

FEATURES TO IMPLEMENT:
    1. Select ROI source (pre-drawn in ImageJ or channel-masking based) - This will be used 
    
TO DO: Updated 1/3/2019
1. Implement Freehand ROI
2. Confirm flexibility of existing program
3. Update documentation to clarify what each function does and how it's used
4. Improve 

@author: Christopher Pratt, PhD
"""

# import statements
import numpy as np, scipy as sp
import matplotlib.pyplot as plt
import skimage
from skimage import io
import pims
#%matplotlib inline

#%%
class ROI:
    def __init__(self, roi, masking='outside', use_z=True, image=None):
        """
        Create an ROI object using an roi imported using ijroi classes
        Inputs:
        1. masking: determine whether inside or outside pixels will be masked
        2. z, t, f: use roi's stored z, t (time), or f (frame) coordinate for roi determination.
        By default, z is true and t and f are false
        
        image can be an image or a path to image
        """
        # Import statements for this module
        from read_roi import read_roi_file, read_roi_zip # ImageJ ROI import
        from skimage.draw import polygon, ellipse # enable drawing of polygon and elliptical ROIs
        import numpy as np
        import numpy.ma as ma
        import pims
        
        # Initialize instance variables
        self.name = roi['name']
        #self.str = "ROI"
        self.kind = roi['type']
        self.position = roi['position'] # int if single slice, dict if z or c
        self.mask_type = masking
        self.mask = None # stores the mask
        self.masked_image = None # stores the masked image
        self.attribs = roi # bucket to hold all the variables that can be called under specialized circumstances
        # set attached image
        if type(image) == "str":
            print("image type str") # debug line
            self.image = pims.open(image) # open image
        else:
            self.image = image # pin image

        # define custom positionals (z, t, c)        
        # if only a single position is defined (single slice)
        self.z = None # initialize as None
        self.c = None # initialize as None
        self.t = None # initialize as None
        if type(self.position) == 'dict':
            for item in self.position:
                if item == "slice":
                    self.z = self.position["slice"]
                elif item == "frame":
                    self.t = self.position["frame"]
                elif item == "channel":
                    self.c = self.position["channel"]
        
        # Define ROI-inclusive pixels using contained methods
        self.pixels = self.__setPixels()
        
        # Define masking operations (debugging)
        if self.mask_type=='inside':
            print('inside mask requested')
        elif self.mask_type=='outside':
            print("outside mask requested")
        else:
            print("No mask requested")
        
        return
    
    def __str__(self):
        return str("ROI object. Name: '{}'\nROI type: '{}'.\nMasking of {} pixels is requested.\
        \n\nDefined ROI-inclusive pixels as {}".format(self.name, self.kind, self.mask_type, self.pixels))
    
    def __setPixels(self):
        """
        This "private" method is to set the properties of the ROI behind the scenes.
        This is called during __init__ and defines the pixels inclusive of the ROI
        """
        # hidden method to set the binary properties of the ROI behind the scenes
        if self.kind == 'rectangle':
            rr, cc = self.__rectangle()
        elif self.kind == 'oval':
            rr, cc = self.__ellipse()
        elif self.kind == 'freehand':
            rr, cc = self.__freehand()
        elif self.kind == 'polygon':
            rr, cc = self.__polygon()
        #elif self.kind == 'channel':
            # set pixels from mask
            # use self.attribs["channel"] or something similar to define pixels
            #rr, cc = self.from_pixels() # call method to create ROI from mask
        return rr, cc
    
    
    def set_pos(self, pos='z', num=1):
        # this method will set the ROI position based on arguments provided
        pass
    
    
    def attach_image(self, image, crop=False):
        # crop: if true, reduce image dimensions to include ROI but not anything else
        # This method will attach an image file to the ROI. 
        # This may be useful for organizational purposes but may not be good for memory management
        # The biggest limitation here would be if you need multiple ROIs on the same image
        # It may be worth doing the crop operation on the ROI by default and saving only the relevant image data
        self.image = image
        # crop image
        return
    
    
    def measure_stack(self, image=None, axis=0, bundle_axes='yx', measurements=('mean', 'median', 'std')):
        """
        Uses input image to measure each slice of a stack (z or t)
        Inputs: Image for ROI
        CHANGELOG 1/3/2019: Add ability for ROI to store an image. Use stored image if not included here.
        
        NOTE: Be sure that mask is created before using measure_stack(). Currently this only accepts default measurements
        
        INPUTS:
            image: image to be measured according to ROI object. If no image provided, uses the attached image.
            If no attached image, produce an error
            Axis: axis over which to iterate. For ndarray this is a number, for PIMS objects this is a character or string
            bundle_axes: axes to combine for measurement. By default this is 'yx'
            measurements: The measurements to return for each frame measured.
                'mean', 'median', 'std', '##-percentile', 'quantiles' 
        
        Function process
        1. import image (use attached image)
        2. Get pixel values for each frame, aggregate measurements into a DataFrame using vector operations
        3. Summarize each frame with dataframe or Series measurement, return DataFrame with values
        
        RETURNS:
            DataFrame with measurements for columns and each row representing a frame in the image
        
        """
        
        # import dependencies
        import pandas as pd
        from pandas import Series, DataFrame
        import numpy.ma as ma
        
        # if no image is provided, then use the attached image
        if image is None:
            image = self.image # alias self.image
        
        df_measurements = DataFrame(columns=measurements) # initialize dataframe
        
        ### test if array or PIMS object
        if hasattr(image, 'shape'): # then is an array
            imgDims = len(image.shape)
            image = np.moveaxis(image, axis, 0) # move given axis to the front to prepare for iterations
            #### NOT YET FUNCTIONAL WITH STANDARD NDARRAY
            for frames in image:
                values = ma.masked_array(frames, mask=self.mask).compressed()
                values_measurements = Series({measurements[0]: values.mean(),
                                                 measurements[1]: np.median(values),
                                                 measurements[2]: values.std()})
                df_measurements = df_measurements.append(values_measurements, ignore_index=True)
            
        elif hasattr(image, 'frame_shape'): # then is PIMS object
            image.iteraxes = axis  # set iteration axis
            image.bundle_axes = bundle_axes # bundle axes. KWarg to alter this if needed
            # iterate through axis
            for frames in image: # get values for each item
                values = ma.masked_array(np.array(frames), mask=self.mask).compressed()
                values_measurements = Series({measurements[0]: values.mean(),
                                                 measurements[1]: np.median(values),
                                                 measurements[2]: values.std()})
                df_measurements = df_measurements.append(values_measurements, ignore_index=True)
                        
        return df_measurements # return dataframe containing measurements
    
    def create_mask(self, image, define_mask_only=False, scale=1.0):
        """create binary mask.
        This means that an explicit instruction must be used so that the computer 
        does not waste time making binaries for every single object if not needed
        Returns: Binary mask of the image xy shape and creates a 3D binary
        Apply ROI mask on image.
        Scale kwarg is if pixel sizes are changed, new ROIs need not be created explicitly
        
        INPUT: image on which to apply mask.
        define_mask_only: If True, return only the 2D mask (not maskedArray). Assign attribute.
        PROCESSING: Create 2d (xy) and 3d masks (xyt/z) across all channels.
        Essentially, propagate the 2d mask into all other dimensions
        Send a 2D image if you only want to return a single plane/channel
        RETURNS: MaskedArray consisting of the original image with mask applied
        """
        
        ### NOTES ABOUT IMPLEMENTATION
        # Using 3 ndArray objects may eat up memory:
        # Can change maskedImage to just be image, which gets overwritten in this function - DONE
        
        import numpy as np
        import numpy.ma as ma # masked arrays
        
        image = np.array(image) # convert to ndarray
        
        print("create_mask() called")
        
        imgDims = len(image.shape) # store dimensions of image to be masked
        print("DEBUG in create_mask(): imgDims = {}".format(imgDims))
        

        # get XY shape of image for mask2D
        """if imgDims == 2:
            maskShape = image.shape
        elif imgDims > 2:
            # this depends on x and y being the last two dimensions
            maskShape = image.shape[-2:]
        else:
            print("Incompatible dimensionality in create_mask()")
        """
        
        """
        if imgDims < 6:
            maskShape3D = image.shape # nD mask to match shape of whole image. This could become a large memory hog
            maskShape2D = image.shape[-2:] # xy mask
            print("\n2D and nD masks created. xyMask shape = {}, ndMask shape = {}".format(maskShape, maskShape2D))
        else:
            print("Incompatible dimensionality in create_mask()") # throw an error maybe?
        """
        maskShape = image.shape[-2:] # xy mask shape
        maskShape3D = image.shape # nDimensional mask shape
            
        # 1 = masked, 0 = unmasked.
        # Create mask based on inside or outside shape
        if self.mask_type == "outside":
            xyMask = np.ones(maskShape)
            ndMask = np.ndarray(shape=maskShape3D) # initialize empty array for speed, data will be written soon
            xyMask[self.pixels] = 0
        elif self.mask_type == "inside":
            xyMask = np.zeros(maskShape)
            ndMask = np.ndarray(shape=maskShape3D) # initialize empty array for speed, data will be written soon
            xyMask[self.pixels] = 1
        
        # assign 2D mask to an attribute so that it can be easily retrieved if necessary
        self.mask = xyMask
        
        ## Extend mask into 3D for application to image
        # This might become a memory hog for large images, but probably runs faster than iteration
        
        # apply mask to all dimensions of image
        # Likely that imgDims ranges from 2-5 (ztcxy)
        if define_mask_only:
            return xyMask # return 2d mask if only the 2d mask is wanted
        elif (imgDims == 2):
            # do something
            image = ma.masked_array(image, mask=xyMask) # create masked_array over image
        elif imgDims == 3:
            # do another thing
            # make 3d mask and make masked_array
            ndMask[:] = xyMask
            image = ma.masked_array(image, mask=ndMask) # apply 3D mask
        elif imgDims == 4:
            # do yet another thing
            ndMask[:,:] = xyMask
            image = ma.masked_array(image, mask=ndMask) # apply 3D mask
        elif imgDims == 5: # probably 5 dims:
            ndMask[:,:,:] = xyMask
            image = ma.masked_array(image, mask=ndMask) # apply 3D mask
        else:
            print("Incompatible dimensionality for create_mask(). Too many dimensions (>6)!")
        
        """
        # now we apply the mask to the provided image
        if len(image.shape) == 2:
            maskedImage = ma.masked_array(image, mask)
        if len(image.shape) == 3:
            maskedImage = ma.masked_array(image, mask)
        """
        #self.masked_image = image # add to attributes
        return image
    
    
    def crop_image(self):
        """
        Crop image to smallest size to include the masked area. 
        This would be important for large files. Uses the self.mask attribute and updates it accordingly
        Return cropped image
        
        Image must be attached to ROI first. The cropped image will then override the original.
        """
        
        # get dimensions of square to crop
        x_min = min(self.pixels[0])
        y_min = min(self.pixels[1])
        x_max = max(self.pixels[0])
        y_max = max(self.pixels[1])
        
        # crop mask
        # print dims
        print("crop_image() not yet functional. Below are the crop dimensions (xy):\nx_min: {}, x_max: {}, y_min: {}, y_max: {}".format(
                x_min, x_max, y_min, y_max))
        #self.image = self.image() # get crop image using array functions
        return
    
    
    def set_axes(self, iteraxes, bundle_axes = 'yx'):
        """
        This sets the active PIMS axes. This is not for use with DataFrames or ndarrays
        """
        # set iteraxes
        self.image.iter_axes = iteraxes
        self.image.bundle_axes = bundle_axes
        return
    
    
    def __ellipse(self):
        """
        Provide an imported ImageJ ROI (ellipse) and creates an ellipse using skimage
        Returns pixel coordinates of ellipse

        Ellipse ROI has the following parameters:
        ['height', 'left', 'name', 'position', 'top', 'type', 'width']
        skimage to draw ellipse requires: r, c (center coordinates), r_radius, c_radius
        """
        from skimage.draw import ellipse
        # check that it is indeed an ellipse, abort if not
        """if not roi["type"] == 'oval':
        print("incorrect type. ROI.ellipse() called but type is {}".format(self.kind))
        return"""

        # get radii of ellipse
        r_radius = self.attribs['height']/2
        c_radius = self.attribs['width']/2
        # get coords
        r = self.attribs['top'] + r_radius
        c = self.attribs['left'] + c_radius

        # draw ellipse
        rr, cc = ellipse(r, c, r_radius, c_radius)
        
        # debugging
        print("ellipse() called for ROI {}".format(self.name))
        
        return rr, cc
    
    def __polygon(self):
        from skimage.draw import polygon
    
        r = self.attribs['y']
        c = self.attribs['x']
        rr, cc = polygon(r, c)
        
        # debugging
        print("polygon() called for ROI '{}'".format(self.name))
        
        return rr, cc
    
    def __freehand(self):
        # debugging
        print("freehand() called for ROI '{}'. This function is not yet implemented".format(self.name))
        
        # Figure out how to determine the boundaries of the freehand drawing
        
        return 0, 0
    
    def __rectangle(self):
        """
        Draws a rectangular ROI as defined by the imported ijroi
        rectangle: Defines width and height, left and top
        """
        
        # Compute boundaries of rectangle using x y coords
        top = self.attribs['top']
        left = self.attribs['left']
        bottom = top + self.attribs['height']
        right = left + self.attribs['width']
        
        # create rr (x), cc (y) lists of inclusive pixels
        rr = []
        cc = []
        for i in range(top, bottom):
            for j in range(left, right):
                rr.append(i) 
                cc.append(j)
        
        # Debug
        print("rectangle() called, dimensions defined as\
        \n Top:{}\n Left:{}\n Bottom:{}\n Right:{}".format(top, left, bottom, right))
        
        return np.array(rr), np.array(cc)


class ROI_Reader:
    """This class is a container to create ROI objects using a path"""
    #from read_roi import read_roi_file, read_roi_zip
    
    def __init__(self, path, image=None):
        """Open ROI (.roi) or list of ROIs (.zip) using ijroi modules
        INPUT: Path to ROI file
        image: Defines the path to an image associated with the ROIs. Optional. Can be added later"""
        from read_roi import read_roi_file, read_roi_zip
        import pims
        
        # Import ROI list
        if path.split('.')[-1] == "zip":
            self.rois = read_roi_zip(path) # imports a labeled dict
        elif path.split('.')[-1] == "roi":
            self.rois = read_roi_file(path) # import single ROI
        else: # no file extension provided
            try:
                self.rois = read_roi_zip(path + '.zip') # imports a labeled dict
                print('importing list of rois')
            except FileNotFoundError: # .roi file, not .zip file
                self.rois = read_roi_file(path + '.roi') # import single ROI
                print("Opening single ROI...")

        self.keys = list(self.rois.keys()) # get list of ROI names for referencing in Dict
        
        self.attach_image(image) # attach image if specified
        
        return
    
    def __str__(self):
        return("{} ROIs contained, with names {}".format(len(self.keys), self.keys))
    
    def get_ROIs(self):
        """Return all ROIs as ROI objects and a list of keys. For one or the other just use the attribute"""
        #roi_objs = [ROI(i) for i in self.rois]
        """roi_objs = []
        for k in self.keys:
        roi_objs.append(i)"""
        
        roi_objs = [ROI(self.rois[k]) for k in self.keys] # this approach is missing the original keys
        
        if len(roi_objs) == 1:
            roi_objs = roi_objs[0]
        
        return roi_objs
    
    def attach_image(self, image):
        """
        Attach an image to the ROI collection. If this is done at initialization, the path to the image is provided and it is opened
        If this method is used, the image is opened elsewhere and added to the item.
        """
        if type(image) == str:
            self.image = pims.open(image) # open an image file
        else:
            self.image = image # pin image variable directly to ROI_Reader object
        return
    
    def measure_ROIs(self, axis):
        """
        This may not be feasible since the ROI object defines the ROIs
        Create this like the measure_stack() method in ROI
        Have this iterate like this though:
            1. load image, pin to ROI_Reader object
                2. measure each ROI in a frame
                3. measure next frame
                4. repeat (1)
        """
        
        if self.image is None: # attach image if not attached
            self.attach_image(image)
        
        pass
    
#%%
        
#### ADDITIONAL OPERATIONS TO ENHANCE ROITOOLS

def roi_from_mask(mask_channel, image=None, mask_type="outside", name="channel_roi", **kwargs):
    """
    This module function will create a new ROI object using a channel for masking rather than relying on an import
    Questions: Include smoothing and thresholding functions inside this or leave it to the user to program? I think leave to user
    
    Put kwargs into a dict, the dict will be the "roi" object that is passed to the ROI() constructor.
    Constructor roi should include: 'name', 'kind', 'position'
    
    kw args:
        - image: attach image to ROI object
        - name: name for ROI
    ROI object attributes:
        - kind = "channel"
        - position = ?? 
        - mask_type = mask_type
    
    Included kw args include smoothing, labeling
    **kwargs add flexibility. How to use?
    
    mask_channel should be a masked_array type.
    """
    # 1. create mask in image from given 
    
    # function to create an ROI object by using a masking operation
    # Input: mask (this can be created using other methods)
    # Return: ROI object
    pass

def mask_and_flatten():
    """
    This function should be useful for neurons. 
    It uses a designated masking channel to mask all other channels and decompose image into masked 2D.
    This could be good for batch operations
    """
    pass
        
