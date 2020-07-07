# -*- coding: utf-8 -*-
"""
Created on Mon Sep  3 07:36:22 2018

GUI for PL-Image-Analyzer

Features:
1. ROI management
    - Import and use IJ ROIs
    - Measure stacks through time and z
    - Batch operations with filename and ROI name matching

2. Colocalization
    - Pearson/Spearman
    - Custom thresholding (Par3 method)
    
2. Measuring stack and time series
    - Measure ImageJ ROIs through time and z

FEATURES TO IMPLEMENT:
    1. Select ROI source (pre-drawn in ImageJ or channel-masking based)
    
CURRENT WORK:
    - Make useable GUI
    - Integrate 
    

@author: ChrisP
"""

import os
import sys
"""
if sys.version_info[0] < 3:
    import Tkinter as tk
    from Tkinter import StringVar, Label, Frame, Button
    from Tkinter.filedialog import askopenfilename, asksaveasfilename
else:
    import tkinter as tk
    from tkinter import StringVar, Label, Frame, Button
    from tkinter.filedialog import askopenfilename, asksaveasfilename
"""    
import tkinter as tk
from tkinter import StringVar, Label, Frame, Button
from tkinter.filedialog import askopenfilename, asksaveasfilename 

import matplotlib # for eventually creating a graphical display

class Colocalizer:
    """
    Application for running Colocalization analyses
        - Pearson
        - Thresholded binaries (akin to Par3/CASPR2 paper)
    """
    
    def __init__(self, master):
        # master= root
        
        # add import statements here for all dependencies if this module is to be co-opted
        # this is where the GUI is designed. Other functions then are made
        
        # Initialize string variables (labels)
        #self.file_path = StringVar()
        #self.roi_path = StringVar()  
        #self.output_path = StringVar() # where to save the resulting analysis
        
        #self.file_path.set("Image file path")
        #self.roi_path.set("ROI path (.zip or .roi)")
        #self.output_path.set("Where to save results")

        
        frame = Frame(master)
        frame.pack()

        self.helloLabel = Label(frame, "Hello World!").grid(row=1, column=1)
        
        # Set Buttons
        #self.exitButton = Button(frame, text="QUIT", fg='red', command=frame.quit).grid(row=10, column=0, sticky=W)
        #self.oldRecordButton = Button(frame, text='Select File to be Updated (Drive)', command = lambda: self.set_path('Old')).grid(row=1, column=0, sticky=tk.W)
        #self.newRecordButton = Button(frame, text='Select File Containing New Data (mLims)', command = lambda: self.set_path('New')).grid(row=2, column=0, sticky=tk.W)
        #self.outputButton = Button(frame, text='Select Output Path', command = lambda: self.set_path('Output')).grid(row=3, column=0, sticky=tk.W)
        #self.processButton = Button(frame, text = 'Process and Output Data', fg='green', command = lambda: self.process_data()).grid(row=4, column=0, sticky=tk.W)
        
        
        
        # set labels
        #self.oldRecordLabel = Label(frame, textvariable=self.old_path).grid(row=1, column=1)
        #self.newRcordLabel = Label(frame, textvariable=self.new_path).grid(row=2, column=1)
        #self.outputLabel = Label(frame, fg='green', textvariable=self.output_path).grid(row=3, column=1) # update this with a new textvar

        # add informational label describing module status
        INFO = "Colocalize using ImageJ ROIs! or Define a Masking Channel"

        #self.projectInfoLabel = Label(frame, text=INFO, font=('Helvetica', 14, 'italic'), wraplength=400, justify='left').grid(row=0, column=0,sticky=tk.W)

        return
        
        
root = tk.Tk()
app = Colocalizer(root)

root.mainloop()