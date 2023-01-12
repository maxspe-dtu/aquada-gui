# -*- coding: utf-8 -*-
"""
Created on Fri Sep  2 14:28:56 2022
@author: catspe

GUI for AQUADA: Automated quantification of damages in composite wind turbine blades.
By Max Spencer
PI Xiao Chen, DTU
imageprocessing modified from main code from Shohreh Sheiati
"""
#MIT Liscence for AQUADA GUI
'''
Copyright © 2023 Technical University of Denmark, Department of Wind and Energy Systems

Permission is hereby granted, free of charge, to any person obtaining a copy of this software 
and associated documentation files (the “Software”), to deal in the Software without restriction, 
including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, 
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED 
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import tkinter as tk
from tkinter.filedialog import askopenfile, askopenfilename, askdirectory

from tkinter import ttk

import os
import gc
import shutil
from csv import reader, writer

from PIL import Image, ImageTk

import imageprocessing as im

#tk video packages/modules
import threading
from time import perf_counter, sleep
import imageio

'''begin tkvideo'''
## tkvideo class comes from the tkvideo module and is used and modified under the mit liscence (notice below)
## https://pypi.org/project/tkVideo/
## minimal changes were made, but included in this file to stop recursive package imports with pyinstaller.
'''Copyright (c) 2020 Xenofon Konitsas

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.'''


class tkvideo():
    """ 
        Main class of tkVideo. Handles loading and playing 
        the video inside the selected label.
        
        :keyword path: 
            Path of video file
        :keyword label: 
            Name of label that will house the player
        :param loop:
            If equal to 0, the video only plays once, 
            if not it plays in an infinite loop (default 0)
        :param size:
            Changes the video's dimensions (2-tuple, 
            default is 640x360) 
        :param hz:
            Sets the video's frame rate (float, 
            default 0 is unchecked) 
    
    """
    def __init__(self, path, label, loop = 0, size = (640,360), hz = 0):
        self.path = path
        self.label = label
        self.loop = loop
        self.size = size
        self.hz = hz
    
    def load(self, path, label, loop, hz):
        """
            Loads the video's frames recursively onto the selected label widget's image parameter.
            Loop parameter controls whether the function will run in an infinite loop
            or once.
        """
        frame_data = imageio.get_reader(path)

        if hz > 0:
            frame_duration = float(1 / hz)
        else:
            frame_duration = float(0)

        if loop == 1:
            while True:
                before = perf_counter()
                for image in frame_data.iter_data():
                    frame_image = ImageTk.PhotoImage(Image.fromarray(image).resize(self.size))
                    label.config(image=frame_image)
                    label.image = frame_image

                    diff = frame_duration + before
                    after = perf_counter()
                    diff = diff - after 
                    if diff > 0:
                        sleep(diff)
                    before = perf_counter()
        else:
            before = perf_counter()
            for image in frame_data.iter_data():
                    frame_image = ImageTk.PhotoImage(Image.fromarray(image).resize(self.size))
                    label.config(image=frame_image)
                    label.image = frame_image

                    diff = frame_duration + before
                    after = perf_counter()
                    diff = diff - after 
                    if diff > 0:
                        sleep(diff)
                    before = perf_counter()

    def play(self):
        """
            Creates and starts a thread as a daemon that plays the video by rapidly going through
            the video's frames.
        """
        thread = threading.Thread(target=self.load, args=(self.path, self.label, self.loop, self.hz))
        thread.daemon = 1
        thread.start()
##end tkvideo        
'''end tkvideo'''

'''begin gui'''
class App(tk.Frame):
    '''
    App takes in a tkinter frame and builds the GUI for AQUADA
    '''
    def __init__(self, parent, title, geometry, *args, **kwargs):
        #intializes variables
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.title = title 
        self.geometry = geometry #size of the window to be created
        

        self.videopath = tk.StringVar()

        #note! twd stands for 'the working directory' and is occasionally referenced as such,
        #but should not be confused with the actual working directory
        #the actual working directory is determinted by the computer, and determines relative paths
        #this variable approximates that for the purposes of this program, but changing this varible
        #does not change the actual working directory
        self.twd = tk.StringVar()
        
        self.make_folder(os.getcwd(), '/__resulting__/')
        self.make_folder(os.getcwd(), 'working')
        home_dir = (os.getcwd()+'/__resulting__/').replace('\\','/').replace('\\\\', '/')
        
        #list of folders containing different damage iterations
        self.damagefolders = []
        options = os.listdir(home_dir)
        self.damagefolders = options

        for i in options:
            if os.path.isdir(i):
                self.damagefolders.append(i)
        try:       
            self.twd.set(self.damagefolders[0])
        except:
            #if there are no folders, make this default one, just in case. 
            self.make_folder(home_dir, '99default')
            self.twd.set('99default')
            self.damagefolders.append('99default')

        #defining folders
            #call folders by using these variables
        self.frames = tk.StringVar()
        self.crops = tk.StringVar()
        self.masks = tk.StringVar()
        self.segments = tk.StringVar()
        self.localizes = tk.StringVar()
        self.progression = tk.StringVar()
        self.results = tk.StringVar()
        
        self.frames.set(os.getcwd() + '/__resulting__/' + self.twd.get()+'/1Frames/')
        self.crops.set(os.getcwd() + '/__resulting__/' + self.twd.get()+'/2Cropped_Frames/')
        self.masks.set(os.getcwd() + '/__resulting__/' + self.twd.get()+'/3Threshold_Mask/')
        self.segments.set(os.getcwd() + '/__resulting__/' + self.twd.get()+'/4Segmented_Damages/')
        self.localizes.set(os.getcwd() + '/__resulting__/' + self.twd.get()+'/5Localized_Damages/')
        self.progression.set(os.getcwd() + '/__resulting__/' + self.twd.get()+'/6DamageProgression/')
        self.results.set(os.getcwd() + '/__resulting__/' + self.twd.get()+'/results/')

        

        #instantiate and initialize value for the threshold
        self.thresh_im_path = tk.StringVar()
        self.threshold_slide = tk.IntVar()
        self.threshold_slide.set(177)
        self.thresh_options = [177, 180, 116]
        
        self.crop_val = tk.StringVar() #use this to combine all the crop atributes, return later.
        
        #instantiate and initialize values for the kernels and blur, used in image processing
        #kernel0 is the opening kernel, kernel1 is the closing kernel
        self.kernel0 = tk.IntVar()
        self.kernel0.set(13)
        self.kernel0_options  = [13, 14, 15]
        
        self.kernel1 = tk.IntVar()
        self.kernel1.set(3)
        self.kernel1_options  = [3, 4, 5,6]
        
        self.blur_thresh = tk.DoubleVar()
        self.blur_thresh.set(80)
        self.blur_options = [80,90,100]
        

        #for crop, intantiate and initialize variables.
        self.x = self.y = 0
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.curX = 0
        self.curY = 0
        
        #these are the coordinates for the chosen cropping.
        self.left = tk.IntVar()
        self.upper =tk.IntVar()
        self.right =tk.IntVar()
        self.lower= tk.IntVar()
        
        #set default crop to the pre-gui crop
        self.left.set(130)
        self.upper.set(0)
        self.right.set(480)
        self.lower.set(480)
        
        
        #labels for settings options. List of strings. 
        self.labels =[]
        
        #number of frames per project
        self.num_frames = tk.IntVar()
        self.num_frames.set(5)
        
        #number of damages in the video
        self.numdamages = tk.IntVar()
        self.numdamages.set(6)
        
        #app name, defined when class is instantiated
        root.title(title)
        
        #app size on screen, defined when instantiated
        root.geometry(geometry)
        width_ind = self.geometry.index('x')
        self.width = self.geometry[0:width_ind]
        self.height = self.geometry[width_ind+1:]
        
        #0 or 1, for linear or quadratic fit
        self.fit_var = tk.IntVar()
        self.fit_var.set(0)
        
        
        #wind turbine favicon
        try:
            root.iconbitmap("wind-turbine-icon.ico")
        except:
            pass
        
        #create tabs for GUI, each tab represents a different 'page'
        self.tabControl = ttk.Notebook(root)
        self.tab0 = ttk.Frame(self.tabControl)
        self.tab1 = ttk.Frame(self.tabControl)
        self.tab2 = ttk.Frame(self.tabControl)
        self.tab3 = ttk.Frame(self.tabControl)
        self.tab4 = ttk.Frame(self.tabControl)
        self.tab5 = ttk.Frame(self.tabControl)
        self.tab6 = ttk.Frame(self.tabControl)
        self.tab7 = ttk.Frame(self.tabControl)
        self.tab8 = ttk.Frame(self.tabControl)
        
        #links tabs with names, puts them in an order
        self.tabControl.add(self.tab0, text='Home')
        self.tabControl.add(self.tab6, text = 'Crop Image')
        self.tabControl.add(self.tab5, text = 'Damage Mask')
        self.tabControl.add(self.tab2, text='Detect Damages')
        self.tabControl.add(self.tab7, text='Damage Progression')
        self.tabControl.add(self.tab4, text = 'Evaluate Individual Damages') #previously Evaluate Single Damage
        self.tabControl.add(self.tab8, text = 'Results')
        self.tabControl.add(self.tab3, text='Settings')
        self.tabControl.add(self.tab1, text = 'Help')
        #data tab, not yet implimented
        #self.tab9 = ttk.Frame(self.tabControl)
        #self.tabControl.add(self.tab9, text = 'Data')
        #self.data_tab(self.tab9)
        
        
        #creates tabs, then gives the frame to the corresponding 
        #function for populating that tab
        
        self.tabControl.pack(expand=1, fill="both")
        
        self.welcome(self.tab0)
        self.crop_tab(self.tab6)
        self.combined_mask(self.tab5)
        self.individual(self.tab2)
        self.indv_damage(self.tab4)
        self.graph_tab(self.tab7)
        self.results_tab(self.tab8)
        self.settings(self.tab3)
        self.help_tab(self.tab1)
        
        
        '''begin tabs'''     
    def welcome(self,window):
        #given a tkinter frame, populates the home tab.
        self.print_text("AQUADA GUI v1", window)
        self.print_text("Welcome to AQUADA GUI. This program is designed to detect damages in wind turbine blades through computer vision.", window)
        
        try:
            self.show_image(window, imagepath ="blade-frame-with-text.png")
        except:
            self.print_text('Image is Missing, but enjoy AQUADA Regardless. Maybe check if other things are missing too...', window)
        #video is coppied to working directory, and frames are put in the frame folder. 
        tk.Button(window, text = 'Begin New Project', command = self.open_vid).pack()
        tk.Button(window, text = 'Instructions and Information', fg="green", command = lambda: [self.instructions(window, tab = 'home')]).pack()
    
    def data_tab(self, window):
        #builds data tab, not in current use
        #this is avalible for a future feature, of 'binned' data, where say, the average of 10 frames is taken every 20 frames
        self.bundle_num = tk.IntVar()
        self.bundle_num.set(1)
        self.bundle_space = tk.IntVar()
        self.bundle_space.set(1)
        
        self.num_frames.set(im.count_frames(self.frames.get()))
        
        tk.Label(window, text = 'Select Data Density', bg = 'light grey').grid(row = 1, column = 1, sticky=tk.N)
        
        tk.Label(window,text='Number of Frames Per Bundle', bg = 'light green').grid(row = 4, column = 1, pady = 10)
        value = tk.Scale(window,from_= 1,to = self.num_frames.get(), orient='horizontal', variable=self.bundle_num, tickinterval=100)
        value.grid(row = 3, column = 1, sticky=tk.N)
        
        tk.Label(window,text='Space Between Bundles', bg = 'light green').grid(row = 7, column = 1, pady = 10)
        value = tk.Scale(window,from_= 1,to = self.num_frames.get(), orient='horizontal', variable=self.bundle_space, tickinterval=100)
        value.grid(row = 6, column = 1, sticky=tk.N)
        
        
    def crop_tab(self, window):
        #builds base for the crop tab this tab allows the user to draw the croped area onto their image
        tk.Label(window, text = 'Crop Image Around Damages', bg = 'light grey').grid(row = 1, column = 1, sticky=tk.N)
        tk.Label(window, text = 'Cropped Selection').grid(row = 1, column = 2, sticky=tk.N)
        #with this button the user is offered a directory to choose an image to crop
        tk.Button(window, text = 'Choose Image to Crop', command = self.crop_im).grid(row = 2, column = 1)
        
        try:
            #the crop all button was removed, cropping all frames now occurs within damage detection. 
            #doing it all together means that if there are lots of frames the user only has to wait once
            tk.Button(window, text = 'Instructions and Information', fg="green", command = lambda:[self.instructions(window, tab= 'crop')]).grid(row =5, column= 1)
            
            #shows buttons that where user can view previous results
            tk.Label(window, text = 'View Files').grid(row = 1, column = 3, sticky=tk.N)
            tk.Button(window, text = 'Video Frames', command = lambda:[self.open_and_show('/1Frames/')]).grid(row =2, column = 3, padx=20, sticky = tk.N)
            tk.Button(window, text = 'Cropped Frames', command = lambda:[self.open_and_show('/2Cropped_Frames/')]).grid(row = 3, column = 3, padx=20, sticky = tk.N)
            
            #the image to be cropped will default to the first frame in the current project when loaded.
            self.crop_im_path = os.getcwd() + '/__resulting__/' + self.twd.get()+'/1Frames/img0.png'
    
            
            self.image_area = tk.Canvas(window, width = 700, height = 500, bg = '#C8C8C8') #define area to display image, allows for selection within it
            self.image_area.grid(row =3, column = 1) #display the area
            self.crop_ims = Image.open(self.crop_im_path) #open the image
            self.crop_im = ImageTk.PhotoImage(self.crop_ims) #turn into ImageTk object
            self.image_area.create_image(0,0, image=self.crop_im, anchor = 'nw') #put image in area
            self.image_area.bind("<ButtonPress-1>", self.on_button_press) #defines action when the mouse is clicked in this area (begin drawing rectangle)
            self.image_area.bind("<B1-Motion>", self.on_move_press)#defines action when the mouse is moved (expand the rectangle)
            self.image_area.bind("<ButtonRelease-1>", self.on_button_release)#defines action when the mouse is released in this area (coordinates of rectangle are saved and the area cropped.)
            
        except:
            pass
            
    
    def combined_mask(self, window):
        #builds the base for the masking tab
        
        #instructions and labels. colors coorelate to steps
        tk.Label(window, text = 'Optimize Binary Damage Mask', bg = 'light grey').grid(row = 0, column = 1, columnspan= 5)
        tk.Label(window, text = 'Input: Image to Adjust').grid(row = 2, column = 1, sticky=tk.N)
        tk.Label(window, text = 'Step 1: Binary Mask', bg = 'light green').grid(row = 2, column = 2, sticky=tk.N)
        tk.Label(window, text = 'Step 2: Mask With Post Processing' , bg = 'light blue').grid(row = 2, column = 3, sticky=tk.N)
        tk.Label(window, text = 'Result: Damage Segmentation').grid(row = 2, column = 4, sticky=tk.N)
        tk.Label(window, text = 'Adjust Parameters and Press Go').grid(row = 7, column = 2, columnspan = 2, sticky=tk.N)
        
        #gives users the option to choose the image they will build their damage mask arround. 
        tk.Button(window, text = 'Choose Image to Mask', command = self.mask_im).grid(row = 1, column = 1)
       
        try:
            #try to get the most recent crop from working, and display on the lhs, adjust variables
            self.thresh_im_path.set(os.cwd.get()+'/working/crop0.png')
            self.og_image=self.grid_image(window, imagepath= self.thresh_im_path.get(), row = 3, column = 1)
            self.adjust_im_path = self.thresh_im_path.get()
            self.update_mask(window) #automatically make the first mask based on the current settings
        except:
            self.thresh_im_path.set(os.getcwd()+'/working/crop0.png')
            self.adjust_im_path = self.thresh_im_path.get()

        #make sliders and labels for the four input steps
        tk.Label(window,text='Step 1: Threshold', bg = 'light green').grid(row = 4, column = 1, pady = 10)
        value = tk.Scale(window,from_= 0,to = 255, orient='horizontal', variable=self.threshold_slide, tickinterval=100)
        value.grid(row = 5, column = 1, sticky=tk.N)
        
        tk.Label(window, text = 'Step 2: Opening (Kernel 0)', bg = 'light blue').grid(row = 4, column = 2, pady = 10, sticky=tk.S)
        value1 = tk.Scale(window,from_= 0,to = 50, orient='horizontal', variable=self.kernel0, tickinterval= 15)
        value1.set(self.kernel0.get())
        value1.grid(row = 5, column = 2, sticky=tk.S)
        
        tk.Label(window, text = 'Step 2: Closing (Kernel 1)', bg = 'light blue').grid(row = 4, column = 3, pady = 10, sticky=tk.S)
        value2 = tk.Scale(window,from_= 0,to = 50, orient='horizontal', variable=self.kernel1,tickinterval= 15)
        value2.grid(row = 5, column = 3, sticky=tk.S)
        value2.set(self.kernel1.get())
        
        tk.Label(window, text = 'Step 2: Blur Threshold', bg = 'light blue').grid(row = 4, column = 4, pady = 10, sticky=tk.S)
        value3 = tk.Scale(window, from_= 0, to = 400, orient='horizontal', variable=self.blur_thresh, tickinterval= 150)
        value3.grid(row = 5, column = 4, sticky=tk.S)
        value3.set(self.blur_thresh.get())
        
        #updates all the steps with the current values, displays result
        tk.Button(window, text="Go", command = self.update_mask).grid(row = 6, column = 2, columnspan = 2, sticky=tk.N)
        
        #resets the values to something reasonable, not necessarily the best. 
        tk.Button(window, text="Reset Values", command = lambda:[self.threshold_slide.set(177), self.kernel0.set(13), self.kernel1.set(3), self.blur_thresh.set(80)]).grid(row = 8, column = 2, columnspan = 2, sticky=tk.N)
        
        #instructions and view files
        tk.Button(window, text = 'Instructions and Information', fg="green", command = lambda:[self.instructions(window, tab= 'mask')]).grid(row = 9, column = 1, columnspan= 1, sticky = tk.W)
        tk.Label(window, text = 'View Files', bg = 'light grey').grid(row =10, column = 1, padx=20, pady = 20, sticky = tk.S)
        tk.Button(window, text = 'Binary Masks', command = lambda:[self.open_and_show('/3Threshold_Mask/')]).grid(row = 11, column = 1, padx=20)
    
    def individual(self, window):
        #this function takes in a tkinter frame and populates the tab for
        #damage detection functions, ie, masking, segmentation ect
        #can either be individual, or full detection.
        
        
        tk.Label(window, text='Perform Entire Damage Detection Process', bg = 'light grey').grid(row =0, column =0,  padx=10 , pady=10)
        #deletes whole project folder, but not the 'frames1' folder with the initial data.
        tk.Button(window, text="Clear Previous Damage Detection", command =lambda : self.clear_last(os.getcwd() + '/__resulting__/' + self.twd.get())).grid(row = 1, column = 0 , padx=20, pady=5 )
        #makes all the folders and does all the damage detection steps, through localize
        full_detect = tk.Button(window, text="Detect Damages", command =lambda : self.all_in_one(window))
        full_detect.grid(row = 2, column = 0 , padx=20, pady=5 )
       
        
       # title text for column
        tk.Label(window, text='Perform Individual Components of Damage Detection Process', bg = 'light grey').grid(row =0, column =1,  padx=10 , pady=10)
  
        #can do the individual steps, inputting input and save paths each time. 
        #not generally reccomended
        
        splitvid = tk.Button(window, text="Split Video", command = self.vid_to_im)
        splitvid.grid(row =1, column =1 , padx=20, pady=5)
        
        cropims = tk.Button(window, text="Crop Images", command = self.crop_images)
        cropims.grid(row =2, column =1 , padx=20, pady=5)
        
        maskims = tk.Button(window, text="Mask Images", command = self.mask_ims)
        maskims.grid(row =3, column =1, padx=20, pady=5)
        
        segmentims = tk.Button(window, text="Segment Damages", command = self.segment_ims)
        segmentims.grid(row =4, column =1 , padx=20, pady=5)
        
        localizeims = tk.Button(window, text="Localize Damages", command = self.localize_ims)
        localizeims.grid(row =5, column =1 , padx=20, pady=5)
        
        savevid = tk.Button(window, text="Save Video",command = lambda: self.save_vid())
        savevid.grid(row =6, column =1 , padx=20, pady=5)
        
        
        tk.Button(window, text = 'Instructions and Information', fg="green", command = lambda:[self.instructions(window, tab = 'detect')]).grid(row = 9, column = 0, columnspan= 1)
        
        #options to open in file explorer the steps of current project
        tk.Label(window, text = 'View Files', bg = 'light grey').grid(row = 0, column = 2, padx=20)
        tk.Button(window, text = 'Video Frames', command = lambda:[self.open_and_show('/1Frames/')]).grid(row =1, column = 2, padx=20)
        tk.Button(window, text = 'Cropped Frames', command = lambda:[self.open_and_show('/2Cropped_Frames/')]).grid(row = 2, column = 2, padx=20)
        tk.Button(window, text = 'Binary Masks', command = lambda:[self.open_and_show('/3Threshold_Mask/')]).grid(row = 3, column = 2, padx=20)
        tk.Button(window, text = 'Segmented Images', command = lambda:[self.open_and_show('/4Segmented_Damages/')]).grid(row = 4, column = 2, padx=20)
        tk.Button(window, text = 'Localized Images', command = lambda:[self.open_and_show('/5Localized_Damages/')]).grid(row = 5, column = 2, padx=20)

        
    def graph_tab(self, window):
        #builds the tab that generates the full damage progerssion, with all damages.
        tk.Label(window, text = 'Generate and View Damage Progression Figures', bg = 'light grey').grid(row = 1, column = 1)
        
        #deletes most recent damage localization data file, to indicate a need to overwrite.
        tk.Button(window, text = 'Clear Previous Progression Visualization (Optional)', command = lambda: [self.clear_last(self.progression.get(), os.getcwd() + '/__resulting__/' + self.twd.get()+'/damage_localization.csv')]).grid(row = 3, column = 1)
        
        #calls the next function, which based on number of damages localizes, crops, and graphs all on one figure.
        tk.Label(window, text = 'Generate Damage Progression Data:', bg = 'light grey').grid(row = 4, column = 1)
        tk.Button(window, text = 'With Seperated Damages', command = lambda:[self.full_progression(window)]).grid(row = 5, column = 1)
        tk.Button(window, text = 'For Whole Image', command = lambda:[self.use_mask(window)]).grid(row = 6, column = 1)
        
        tk.Label(window, text = 'View Files', bg = 'light grey').grid(row = 8, column = 1, padx=20)
        tk.Button(window, text = 'Localized Images', command = lambda:[self.open_and_show('/5Localized_Damages/')]).grid(row = 9, column = 1, padx=20)
        tk.Button(window, text = 'Damage Results', command = lambda:[self.open_and_show('/6DamageProgression/graphs/')]).grid(row = 10, column = 1, padx=20)
        
        tk.Button(window, text = 'Instructions and Information', fg="green", command = lambda: [self.instructions(window, 'eval')]).grid(row = 11, column = 1)

        
    def indv_damage(self, window):
        #builds the very basis of the evaluate single damages tab
        #doesn't autopopulate, since it is reliant on all the previous tabs.
        tk.Button(window, text = 'Load Damages', command = self.load_damages).grid(row = 0, column = 1, columnspan= 1)
        tk.Button(window, text = 'Instructions and Information', fg="green", command = lambda:[self.instructions(window, 'single')]).grid(row = 14, column = 1, columnspan= 1)
    
    def results_tab(self, window):
        #tab to make and show video that has with all steps of the process + graphs
        tk.Label(window, text = 'View Complete Results', bg = 'light grey').grid( row = 1, column = 1, padx = 10)

        #clears the 'results' file, to indicate overwriting with a new one. 
        tk.Button(window, text = 'Clear Past Results Visualization', command = lambda:[self.clear_last(self.results.get())]).grid(row =2 , column = 1, padx = 10)
        #calls another helper to find the right paths to all six parts of the results layout.
        tk.Button(window, text = 'Generate Results', command = lambda:[self.generate_results(window)]).grid(row = 3, column = 1, padx = 10)
       
        tk.Button(window, text = 'Instructions and Information', fg="green", command = lambda: [self.instructions(window, tab = 'results')]).grid(row = 4, column = 1, padx = 10, pady = 5)
        

    
    def settings(self, window):
        #builds the setting tab
        tk.Label(window, text = 'Settings', bg = 'light grey').grid(row = 0, column = 1, columnspan= 5, sticky = tk.N, pady = 10)
        

        #make the directory selection component of setting using build_setting        
        self.dir_refresh = tk.Button(window, text="Update Project") #create button to be the update, so that it is unique to updating the dir
        #build out the option menu and input, as well as display it all. returns the button with the current project, and the input from the entry
        # so that both of those can be stored and forgotten accordingly. 
        self.curr_dir, self.input_dir = self.build_setting(window, 'Project', self.twd, self.damagefolders, 1, 0, self.dir_refresh)
        
        #link the refresh button with forgetting the current project, and displaying the new one.
        self.dir_refresh.config(command= lambda: [self.curr_dir.grid_forget(),self.update_project(), self.update_setting_wdir(row= 2, column=1, window = window)])
        
        
        self.thresh_refresh = tk.Button(window, text="Update Threshold")
        self.thresh_but, self.input_thresh = self.build_setting(window, 'Threshold', self.threshold_slide, self.thresh_options, 2, 0, self.thresh_refresh)
        self.thresh_refresh.config(command = lambda: [self.thresh_but.grid_forget(), self.update_setting_thresh(row= 2, column=2, window = window)])
        
      
        #crop doesn't use building setting, because inputting values is both difficult, and also makes less sense.
        tk.Label(window, text = 'Current Crop', bg = 'lightgrey').grid(row = 1, column = 3) 
        self.crop_but = tk.Button(window, text = 'left = ' + str(self.left.get())+' upper = '+ str(self.upper.get()) + ' right = ' + str(self.right.get()) +' lower = '+str(self.lower.get()))
        self.crop_but.grid(row = 2, column = 3, padx= 5)
        tk.Button(window, text='Update Crop', command= lambda: [self.crop_but.grid_forget(), self.update_setting_crop(row= 2, column=3, window = window)]).grid(row = 7, column = 3)
        
        tk.Label(window, text ='--------------------------------------------------------------------').grid(row = 8, column = 1, columnspan=3)
        self.kernel0_refresh = tk.Button(window, text="Update Kernel 0 ")
        self.kernel0_but, self.input_kernel0 = self.build_setting(window, 'Kernel 0 ', self.kernel0, self.kernel0_options, 1, 9, self.kernel0_refresh)
        self.kernel0_refresh.config(command = lambda: [self.kernel0_but.grid_forget(), self.update_setting_kernel0(row= 11, column = 1, window = window)])
        
        self.kernel1_refresh = tk.Button(window, text="Update Kernel 1")
        self.kernel1_but, self.input_kernel1 = self.build_setting(window, 'Kernel 1 ', self.kernel1, self.kernel1_options, 2, 9, self.kernel1_refresh)
        self.kernel1_refresh.config(command = lambda: [self.kernel1_but.grid_forget(), self.update_setting_kernel1(row= 11, column = 2, window = window)])
        

        self.blur_refresh = tk.Button(window, text="Update Blur")
        self.blur_but, self.input_blur = self.build_setting(window, 'Blur ', self.blur_thresh, self.blur_options, 3, 9, self.blur_refresh)
        self.blur_refresh.config(command = lambda: [self.blur_but.grid_forget(), self.update_setting_blur(row= 11, column =3, window = window)])
        
        tk.Button(window, text='Save Settings', command= self.save_settings ).grid(row = 17, column = 1, columnspan=4, pady = 10) 
        
        tk.Button(window, text = 'Instructions and Information', fg="green", command = lambda:[self.instructions(window, 'settings')]).grid(row = 18, column = 1, columnspan= 4)
        
        #options to open in file explorer the steps of current project
        row = 1
        column = 4
        tk.Label(window, text = 'View Files', bg = 'lightgrey').grid(row = row, column = column, padx=10, pady = 10)
        tk.Button(window, text = 'Video Frames', command = lambda:[self.open_and_show('/1Frames/')]).grid(row = row+1, column = column, padx=20)
        tk.Button(window, text = 'Cropped Frames', command = lambda:[self.open_and_show('/2Cropped_Frames/')]).grid(row = row+2, column = column, padx=20)
        tk.Button(window, text = 'Binary Masks', command = lambda:[self.open_and_show('/3Threshold_Mask/')]).grid(row = row+3, column = column, padx=20)
        tk.Button(window, text = 'Segmented Images', command = lambda:[self.open_and_show('/4Segmented_Damages/')]).grid(row = row+4, column = column, padx=20)
        tk.Button(window, text = 'Localized Images', command = lambda:[self.open_and_show('/5Localized_Damages/')]).grid(row = row+5, column = column, padx=20)
        tk.Button(window, text = 'All Damage Results', command = lambda:[self.open_and_show('/6DamageProgression/')]).grid(row = row+6, column = column, padx=20)
        tk.Button(window, text = 'Resulting Images', command = lambda:[self.open_and_show('/results/')]).grid(row = row+7, column = column, padx=20)
        
        
       
        
        
    def help_tab(self, window):
        #builds the help tab by displaying advice
        self.print_text('\nGeneral Advice:', window)
        self.print_text('This GUI handles files based on their location and names in folders, so please do not rename files or folders.', window)
        self.print_text('Likewise, analysis is in general not completed if there are pre-existing files. So if you wish to repeat steps with different settings, delete the files and re-run the program.', window)
        self.print_text('The \'Clear Previous\' buttons will also do this.', window) 
        self.print_text('All analysis and settings should be saved, so when in doubt simply close and open the GUI again.', window) 
        self.print_text('This program is only designed for .wmv and .png files. Use of other video and image file types will result in errors.', window)
        self.print_text('Please be patient with loading times, these images can contain a lot of data. Please also only press buttons once, then give them time to load. If it hasn’t worked the first time, it is unlikely to work again immediately. ', window)
        self.print_text('You can monitor the progress of your analysis by watching the files be generated. You can open the relevant folder in file explorer in \'Settings\'  under \'View Files \'', window)
        self.print_text('While the processing is occurring, you will see a message that the GUI is not responding. This is normal.', window)
        self.print_text('Instructions for each tab can be accessed by clicking the green \'Instructions and Information\' button in each tab', window)
        self.print_text('\n\nResources:', window)
        self.print_text('Included with this GUI is a video demonstration, which demonstrates the full damage detection process.', window)
        
        
    '''begin helper methods'''
    
    '''home tab helper methods'''
    def open_vid(self):
        #takes the working video, copies it to the working directory. sets the videopath
        filepath = self.open_file(prompt = 'Choose a Thermal Image Video with a .wmv format')
        if filepath.__contains__('.wmv'):
            
            name_ind = filepath.rfind('/')
            file_name = filepath[name_ind:]
            try:
                shutil.copy(filepath, os.getcwd()+'/working/'+file_name)
            except shutil.SameFileError:
                #if file is already in working, pass
                pass
            #ideally, video would also be copied into the project directory. not working currently.
            try:
                shutil.copy(os.getcwd()+'/working/'+file_name, os.getcwd()+'/__resulting__/'+self.twd.get()+'/')
            except:
                self.show_error('testing')
                
            try:
                os.rename(os.getcwd()+'/working/'+file_name, os.getcwd()+'/working/video.wmv')
            except:
                #if video.wmv already exists, delete the old video first
                os.remove(os.getcwd()+'/working/video.wmv')
                os.rename(os.getcwd()+'/working/'+file_name, os.getcwd()+'/working/video.wmv')
            #video is now in /working/
            self.videopath.set(os.getcwd()+'/working/')
            
            #pop up window that asks for the project name and frame spacing
            self.ask_filename()
        else:
            self.show_error(text = 'File incompatible, please select a file with a .wmv extention.')
        
    def close_win(self, top):
        #closes the box asking for the project name
        top.destroy()
        
    def insert_val(self,e,n, top):
        #called when 'okay' is selected on the filename popup
        #makes a new project with the user inputted name, creates the necessary subfolders, then closes itself.
        if len(e.get()):
            self.update_project(e.get())
            self.make_folder('__resulting__/',self.twd.get())
            self.make_folder('__resulting__/'+self.twd.get()+'/', "1Frames")
            self.make_folder('__resulting__/'+self.twd.get()+'/', "2Cropped_Frames")
            self.make_folder('__resulting__/'+self.twd.get()+'/', "3Threshold_Mask")
            self.make_folder('__resulting__/'+self.twd.get()+'/', "4Segmented_Damages")
            self.make_folder('__resulting__/'+self.twd.get()+'/', "5Localized_Damages")
            self.make_folder('__resulting__/'+self.twd.get()+'/', "6DamageProgression")
            
            #also trying here to copy the video into the working directory
            try:
                shutil.copyfile(self.videopath.get()+'video.wmv', os.getcwd() + '/__resulting__/' + self.twd.get()+'/')
            except PermissionError:
                pass
            
            #gets the length of the frame spacing (number of frames to skip)
            if len(n.get()):
                im.select_frames(self.videopath.get()+'video.wmv', self.frames.get(), int(n.get()))
                self.close_win(top)
            #if nothing is inputed, default is to just look at everything
            else:
                im.readvid(self.videopath.get()+'video.wmv', self.frames.get())
                self.close_win(top)
        else:
            self.close_win(top)
            self.show_error(text = 'Error in making new project')
    
    def ask_filename(self, window= None):
        #asks for a users input name for a new project, in a pop up window
        if window == None:
            window = self.tab0
        
        #Create pop up window
        top= tk.Toplevel(window)
        top.geometry("250x115")
     
        tk.Label(top, text = 'Project Name').pack()
        
        #Create an Entry for opening
        entry= tk.Entry(top, width= 25)
        entry.pack()
        
        tk.Label(top, text = 'Frame Spacing').pack()
        number = tk.Entry(top, width = 10)
        number.pack()
     
        #submit the values to insert_val which will make the folders and read in the video
        tk.Button(top,text= "ok", command= lambda:self.insert_val(entry,number, top)).pack(pady= 5,side=tk.TOP)
        
    
    '''crop tab methods'''
    def on_button_press(self, event, area= None, window = None):
        #creates a rectangle, when user starts drawing on the image to crop
        if window == None:
            window = self.tab6
        if area == None:
            area = self.image_area
        self.start_x = event.x
        self.start_y = event.y
        # create rectangle if not yet exist
        self.rect = self.image_area.create_rectangle(self.x, self.y, 1, 1, fill="")
    
    def on_move_press(self,  event, area= None, window = None):
        #expands rectangle as user draws crop over selected frame. 
        if window == None:
            window = self.tab6
        if area == None:
            area = self.image_area
        self.curX, self.curY = (event.x, event.y)
        # expand rectangle as you drag the mouse
        self.image_area.coords(self.rect, self.start_x, self.start_y, self.curX, self.curY)
        
    def on_button_release(self,  event, image = None, area= None, window = None):
        #when the user stops drawing over crop area, save the coordinates, and display the selection
        if window == None:
            window = self.tab6
        if area == None:
            area = self.image_area
        if image == None:
            image = self.crop_ims
        try:
            self.crop_lab.grid_forget()
        except:
            pass
        #save the selection to the working directory
        cropped_section = self.crop_ims.crop([self.start_x,self.start_y,self.curX,self.curY])
        cropped_section.save(os.getcwd()+'/working/'+ 'crop0' + ".png", quality=100)
        cropped_section.save(self.crops.get()+'img0' + ".png", quality=100)
        cropped_section = ImageTk.PhotoImage(cropped_section)

        self.crop_lab = tk.Label(window, image=cropped_section)
        self.crop_lab.image = cropped_section
        #display the selection
        self.crop_lab.grid(row = 3, column = 2)   
        self.left.set(self.start_x)
        self.upper.set(self.start_y)
        self.right.set(self.curX)
        self.lower.set(self.curY)
        self.update_setting_crop(row= 2, column=3)
      
    def crop_im(self, window = None):
        #in the 'crop'' tab, ask and display an image to be cropped, then bind the buttons.
        #once the 'choose image to crop' button, display image, bind buttons
        if window == None:
            window = self.tab6
        
        self.crop_im_path = self.open_file(prompt = 'Choose Image to Crop', start_dir = self.frames.get() )    
        self.image_area = tk.Canvas(window, width = 700, height = 500, bg = '#C8C8C8')
        self.image_area.grid(row =3, column = 1)      
        self.crop_ims = Image.open(self.crop_im_path)
        self.crop_im = ImageTk.PhotoImage(self.crop_ims)
        self.image_area.create_image(0,0, image=self.crop_im, anchor = 'nw')
        self.image_area.bind("<ButtonPress-1>", self.on_button_press)
        self.image_area.bind("<B1-Motion>", self.on_move_press)
        self.image_area.bind("<ButtonRelease-1>", self.on_button_release)

    '''mask tab methods'''
    def mask_im(self, window = None):
        #when user selects image to mask, this is called. Pop up for image choice, and shows image. 
        if window == None:
            window = self.tab5
        try:
            #try and remove the orrigional image from the gui
            self.og_image.grid_forget()
        except:
            pass
        #open directory to ask for the image to mask
        self.thresh_im_path.set(self.open_file(prompt = 'Choose Image to Mask', start_dir=(self.crops.get())))
        #shows the orrigional image
        self.og_image=self.grid_image(window, imagepath= self.thresh_im_path.get(), row = 3, column = 1)
        self.adjust_im_path = self.thresh_im_path.get()
        #use the image to update the three mask images
        self.update_mask(window)
        
                   
    def update_mask(self, window = None):
        #updates all four images in the masking process, based on slider values, then displays them.
        if window == None:
            window = self.tab5
        try:
            #try and forget the four images in the masking process
            self.og_image.grid_forget()            
            self.mask_image.grid_forget()
            self.adjust_image.grid_forget()
            self.segmented_image.grid_forget()
        except:
            pass
        try:
            #call the three steps in the making process, from the image_processing package
            im.threshold(self.thresh_im_path.get(), os.getcwd()+'/working/', threshold = self.threshold_slide.get(), one = True)
            im.processing(self.thresh_im_path.get(), os.getcwd()+'/working/', threshold = self.threshold_slide.get(), kernel0val= self.kernel0.get(), kernel1val= self.kernel1.get(), blur_thresh= (self.blur_thresh.get()/100), one = True)
            im.segmentation(self.thresh_im_path.get(), os.getcwd()+'/working/adjust0.png', os.getcwd()+'/working/',one=True)
        except:
            self.show_error(window, text = 'There was an error, please select an image to mask.')
        try:
            self.og_image.grid_forget()
        except:
            pass
        #show the four steps of masking
        self.og_image=self.grid_image(window, imagepath= self.thresh_im_path.get(), row = 3, column = 1)
        self.mask_image = self.grid_image(window, imagepath= os.getcwd()+'/working/mask0.png', row = 3, column = 2)
        self.adjust_image = self.grid_image(window, imagepath =os.getcwd()+'/working/adjust0.png', row = 3, column = 3)
        self.segmented_image = self.grid_image(window, imagepath= os.getcwd()+'/working/seg0.png', row = 3, column = 4)
        self.input_thresh.delete(1.0)
        

        
    '''damage detection tab methods'''
    def all_in_one(self, window, path = None, video = None):
        #performs the entire damage detection process, as long as a video is provided. 
        #Checks for existing files in the folders, if there are any, then that step is not completed (to save time)
        if path == None:
            path = self.twd.get() 
        if video == None:
            video = self.videopath.get()
            
        #save the settings so in case the user forgets
        self.save_settings()
        
        #declaring all the paths for the file locations
        folder_path = os.getcwd()+ '/__resulting__/'+self.twd.get()
        folder_path = folder_path.replace('//','/')
        video = video.replace('//','/')
        
        #added 1 to end to avoid confusion with the self.frames paths 
        frames1 = self.make_folder(folder_path, "1Frames")
        crops1 = self.make_folder(folder_path, "2Cropped_Frames")
        masks1 = self.make_folder(folder_path, "3Threshold_Mask")
        segs1 = self.make_folder(folder_path, "4Segmented_Damages")
        locs1 = self.make_folder(folder_path, "5Localized_Damages")
        
        #basically, if there are more than two files already existing, pass, if not, perform the step
        #one image can end up in the folders based on the earlier steps, but there shouldnt be more than 2
        if len([name for name in os.listdir(self.frames.get()) if os.path.isfile(os.path.join(self.frames.get(), name))]) >2:
            pass  
        else:
            im.readvid(video,frames1)
        
        if len([name for name in os.listdir(self.crops.get()) if os.path.isfile(os.path.join(self.crops.get(), name))]) >2:
            pass  
        else:
            im.crop(frames1, crops1,left = self.left.get(), upper = self.upper.get(), right = self.right.get(), lower = self.lower.get() )
        
        if len([name for name in os.listdir(self.masks.get()) if os.path.isfile(os.path.join(self.masks.get(), name))]) >2:
            pass  
        else:
            im.processing(crops1, masks1 ,threshold = self.threshold_slide.get(), kernel0val= self.kernel0.get(), kernel1val= self.kernel1.get(), blur_thresh= (self.blur_thresh.get()/100))
        
        #actually localize image before doing segmentation, so that if the number of hot spots
        #changes then the user can adjust sooner
        if len([name for name in os.listdir(self.localizes.get()) if os.path.isfile(os.path.join(self.localizes.get(), name))]) >2 and os.path.exists (os.getcwd() + '/__resulting__/' + self.twd.get()+'/damage_localization.csv'):
            num_cnts = im.count_damages(os.getcwd()+'/__resulting__/'+self.twd.get())  
        else:
            try:
                #get the number of countours (damages)
                num_cnts = im.localize(crops1,masks1,locs1, data_path=os.getcwd()+'/__resulting__/'+self.twd.get())
                self.numdamages.set(num_cnts)
            except KeyError:
                self.show_error(window, text = 'Number of damages is not constant. Please adjust crop or mask to ensure that the damage number is constant if you wish to evaluate individual damages.')
                
        if len([name for name in os.listdir(self.segments.get()) if os.path.isfile(os.path.join(self.segments.get(), name))]) >2:
            pass  
        else:
            im.segmentation(crops1, masks1 ,segs1)

        self.move_on(window, 'Damage detection complete, ready to move on.')
        self.save_settings()
        gc.collect()
        
        
    def vid_to_im(self):
        #prompts a user for the paths, then splits the video into images
        #from the individual damage step buttons
        vid_path = self.open_file(prompt = 'select video to split into frames')
        save_path = self.open_dir('Select location for saved images', self.twd.get()+'/1Frames/')
        im.readvid(vid_path, save_path)
        self.move_on(text = 'Damage detection complete, ready to move on.')
        
    def crop_images(self):
        #prompts the user for a path, then crops images (according to saved crop)
        #from the individual damage step buttons
        frame_path = self.open_dir('Select images to crop', self.frames.get(), show = True)
        save_path = self.open_dir('Select location for saved images', self.crops.get())
        im.crop(frame_path, save_path, left = self.left.get(), upper = self.upper.get(), right = self.right.get(), lower = self.lower.get())
    
    def mask_ims(self):
        #prompts the user for paths, then generates binary mask
        #from the individual damage step buttons
        frame_path = self.open_dir('Select images to mask', self.crops.get(), show = True)
        save_path = self.open_dir('Select location for saved images', self.masks.get())
        im.processing(frame_path, save_path, threshold = self.threshold_slide.get(), kernel0val= self.kernel0.get(), kernel1val= self.kernel1.get(), blur_thresh= (self.blur_thresh.get()/100))
        
        
    def segment_ims(self):
        #prompts the user for paths, then generates segmented images
        #from the individual damage step buttons
        frame_path = self.open_dir('Select images to segment',self.crops.get(), show = True)
        mask_path = self.open_dir('Select threshold mask', self.masks.get(), show = True)
        save_path = self.open_dir('Select location for saved images',self.segments.get())
        im.segmentation(frame_path, mask_path, save_path)
        
    def localize_ims(self):
        #prompts the user for paths, then generates localized images
        #from the individual damage step buttons
        frame_path = self.open_dir('Select images to localize', self.crops.get(), show = True)
        mask_path = self.open_dir('Select threshold mask', self.masks.get(), show = True)
        save_path = self.open_dir('Select location for saved images', self.localizes.get())
        
        try:
            num_cnts = im.localize(frame_path, mask_path, save_path, data_path=os.getcwd()+'/__resulting__/'+self.twd.get())
        except KeyError:
            self.show_error(text = 'Error in locating damages. Please make sure there are cropped images and correct binary masks.')
        self.numdamages.set(num_cnts)
        self.count_all_pixels()
        
    def save_vid(self):
        #prompts the user for paths, then generates video by stitching images back together.
        #finnese this better, want to have a prompt to select the save location ect, instead of just having that show up on file explorer
        #from the individual damage step buttons
        frame_path = self.open_dir('Select folder of images to combine')
        save_path = self.open_dir('Select location for saved video')
        im.combine(frame_path, save_path)
        
    ''' damage progression tab methods'''
    def full_progression(self, window):
        #calls these four steps in order, to localize, crop, count damages, and graph them.
        #if there is only 1 damage, asks if user wants linear or quad fit. 
        #if there already are files, then do not re-make the whole graph
        self.get_damage_locations()
        
        if self.numdamages.get()==1:
            self.count_all_pixels(one= True)
            try:
                path = self.make_folder(os.getcwd() + '/__resulting__/' + self.twd.get(), '6DamageProgression')
            except:
                pass
            if os.path.exists (self.progression.get()+'/graphs/damage1fig0.png'):
                self.all_in_one_graphs(window)
            else: 
                self.ask_fit(window)
        else:
            self.crop_all_damages()
        
            self.count_all_pixels()
        
            self.all_in_one_graphs(window)
            
    def use_mask(self, window):
        #counting all pixels in the image, not just in each damage.
        #aka counting pixels by using the mask
        try:
            path = self.make_folder(os.getcwd() + '/__resulting__/' + self.twd.get(), '6DamageProgression')
        except:
            pass
        if os.path.exists (self.progression.get()+'/graphs/damage1fig0.png'):
            #mostly copies all_in_one damages here. Not the best solution, could be improved
            if window == None:
                window = self.tab7
            #clear the tab
            for widgets in window.winfo_children():
                widgets.destroy()
            
            #repopulate the tab
            self.graph_tab(window)
            
            #show a localized image for context on the damage numbers
            self.grid_image(window,self.localizes.get()+ 'finalimg0.png', row=1, column=3, rspan = 10)

            
            
            data_path = os.getcwd()+ '/__resulting__/' +self.twd.get()+'/damaged_pixels.csv'
            save_path = self.make_folder(self.progression.get(), 'graphs')
            #just pick a random folder that has the correct number of frames.
            folder_path = self.masks.get()
            self.numdamages.set(1)
            
            #if there have already been graphs made, dont make new ones! this saves time, if new ones arent wanted.
            if os.path.exists (self.progression.get()+'/graphs/damagesfig0.png') or os.path.exists (self.progression.get()+'/graphs/damage1fig0.png'):
                pass
            else:
                if self.numdamages.get()==1:
                    #allows for quadratic or linear fit. 
                     im.count_pixels(self.masks.get(), data_path, 1)
                     im.make_graph(data_path, save_path,folder_path, 1, fit= self.fit_var.get())
                else:
                    self.show_error(window, 'an error has occured. please review files.')
                gc.collect()
                #combine plots into a video, then display.
                im.combine(self.progression.get()+'graphs/', self.progression.get()+ 'graphs/')
                #put a pop up so the user knows its done.
                self.move_on(window, text= 'progression complete')
            
            try:
                #show the video of the results, check that it exists first
                os.path.exists(self.progression.get() +'graphs/savedvideo.wmv')
                self.grid_video(window, self.progression.get()+ '/graphs/savedvideo.wmv', row = 1, column = 4, rowspan=20 , replayrow=21)

            except:
                tk.Label(window, text = 'unable to play video').grid(row = 1, column = 4)
        
        else: 
            self.fit_var.set(0) #chooses linear fit, again, not a good solution
            #mostly copies all_in_one damages here. Not the best solution, should be changed
            if window == None:
                window = self.tab7
            #clear the tab
            for widgets in window.winfo_children():
                widgets.destroy()
            
            #repopulate the tab
            self.graph_tab(window)
            
            #show a localized image for context on the damage numbers
            self.grid_image(window,self.segments.get()+ 'seg0.png', row=1, column=3, rspan = 10)
            
            
            data_path = os.getcwd()+ '/__resulting__/' +self.twd.get()+'/damaged_pixels.csv'
            save_path = self.make_folder(self.progression.get(), 'graphs')
            #just pick a folder that has the correct number of frames.
            folder_path = self.masks.get()
            self.numdamages.set(1)
            
            #if there have already been graphs made, dont make new ones! this saves time, if new ones arent wanted.
            if os.path.exists (self.progression.get()+'/graphs/damagesfig0.png') or os.path.exists (self.progression.get()+'/graphs/damage1fig0.png'):
                pass
            else:
                if self.numdamages.get()==1:
                    #allows for quadratic or linear fit. 
                     im.count_pixels(self.masks.get(), data_path, 1)
                     im.make_graph(data_path, save_path,folder_path, 1, fit= self.fit_var.get())
                else:
                    im.plot_all(data_path, save_path,folder_path, self.numdamages.get())
                gc.collect()
                #combine plots into a video, then display.
                im.combine(self.progression.get()+'graphs/', self.progression.get()+ 'graphs/')
                #put a pop up so the user knows its done.
                self.move_on(window, text= 'progression complete')
            
            try:
                #show the video of the results, check that it exists first
                os.path.exists(self.progression.get() +'graphs/savedvideo.wmv')
                self.grid_video(window, self.progression.get()+ '/graphs/savedvideo.wmv', row = 1, column = 4, rowspan=20 , replayrow=21)
            except:
                tk.Label(window, text = 'unable to play video').grid(row = 1, column = 4)
            

    def ask_fit(self, window= None, text = 'Linear or Quadratic Fit'):
         #creates a pop up to ask if the user wants a quadratic or linear fit with one damage.
         if window == None:
             window = self.tab0
         #Create a Toplevel window (new pop up)
         top= tk.Toplevel(window)
         top.geometry("250x100")
         
         root.eval(f'tk::PlaceWindow {str(top)} center')
         
         line = tk.Radiobutton(top, text = 'Linear Fit', value =0, variable= self.fit_var)
         curve = tk.Radiobutton(top, text = 'Quadratic (Curve) Fit', value = 1, variable= self.fit_var)
         
         line.grid(row = 2, column =1)
         curve.grid(row = 2, column = 2)
         #Create an Entry Widget in the Toplevel window
         tk.Label(top, text = text, wraplength = 230).grid(row = 1, column = 1, columnspan= 2)
         tk.Button(top,text= "ok", command= lambda:self.go_fit(window, self.fit_var)).grid(row = 3, column = 1, columnspan= 2)
        
    def go_fit(self, window, variable):
        variable.get()
        self.all_in_one_graphs(window)
        
    def all_in_one_graphs(self, window = None):
        #generates graphs for all damages. localizes and counts pixels, then graphs
        if window == None:
            window = self.tab7
        #clear the tab
        for widgets in window.winfo_children():
            widgets.destroy()
        
        #repopulate the tab
        self.graph_tab(window)
        
        #show a localized image for context on the damage numbers
        self.grid_image(window,self.localizes.get()+ 'finalimg0.png', row=1, column=3, rspan = 10)
        
        
        data_path = os.getcwd()+ '/__resulting__/' +self.twd.get()+'/damaged_pixels.csv'
        save_path = self.make_folder(self.progression.get(), 'graphs')
        #just pick a folder that has the correct number of frames.
        folder_path = self.masks.get()
        num = im.count_damages(os.getcwd()+'/__resulting__/'+self.twd.get())
        self.numdamages.set(num)
        
        #if there have already been graphs made, dont make new ones! this saves time, if new ones arent wanted.
        if os.path.exists (self.progression.get()+'/graphs/damagesfig0.png') or os.path.exists (self.progression.get()+'/graphs/damage1fig0.png'):
            pass
        else:
            if self.numdamages.get()==1:
                #allows for quadratic or linear fit. 
                 im.make_graph(data_path, save_path,folder_path, 1, fit= self.fit_var.get())
            else:
                im.plot_all(data_path, save_path,folder_path, self.numdamages.get())
            gc.collect()
            #combine plots into a video, then display.
            im.combine(self.progression.get()+'graphs/', self.progression.get()+ 'graphs/')
            #put a pop up so the user knows its done.
            self.move_on(window, text= 'progression complete')
        
        try:
            #show the video of the results, check that it exists first
            os.path.exists(self.progression.get() +'graphs/savedvideo.wmv')
            self.grid_video(window, self.progression.get()+ '/graphs/savedvideo.wmv', row = 1, column = 4, rowspan=20 , replayrow=21)
        except:
            tk.Label(window, text = 'unable to play video').grid(row = 1, column = 4)
            
    def get_damage_locations(self):
        #gets the coordinates of the damages on a localized image. if a file of locations alreay exists, just count
        #the number of damages, otherwise localize one image and use that. Checking for the existing file allows for
        #new locations to be saved after the damages are re-cropped.
        frame_path = self.crops.get()
        thresh_path = self.masks.get()
        save_path = os.getcwd()+'/working/'
        data_path = os.getcwd()+'/__resulting__/'+self.twd.get()
        if os.path.exists (os.getcwd() + '/__resulting__/' + self.twd.get()+'/damage_localization.csv'):
            num_dams = im.count_damages(os.getcwd()+'/__resulting__/'+self.twd.get())  
        else:
            try:
                num_dams = im.localize(frame_path, thresh_path, save_path, data_path, one =True)
            except:
                self.show_error(text = 'Error in locating damages. Please make sure there are cropped images and correct binary masks.')
                
        self.numdamages.set(num_dams)

    
    def crop_all_damages(self):
        #if crop folders are empty, crops all damages from full frame according to damage localization
        frame_path = self.masks.get()
        save_path = self.make_folder(os.getcwd() + '/__resulting__/' + self.twd.get(), '6DamageProgression')
        
        #jsut checks for the first mask in the first damage folder
        if os.path.exists (self.progression.get()+ '/damage1/crop/mask0.png'):
            pass
        else:
            im.crop_ind_damages(os.getcwd()+ '/__resulting__/' +self.twd.get()+'/damage_localization.csv', frame_path, save_path+'/')
        gc.collect()
        
    def count_all_pixels(self, one =False):
        #counts the damaged pixels in cropped damages, assuming there is not a previous count
        if os.path.exists (os.getcwd() + '/__resulting__/' + self.twd.get()+'/damaged_pixels.csv'):
            pass  
        else:
            if one:
                im.count_pixels(self.masks.get(), os.getcwd()+ '/__resulting__/' +self.twd.get()+'/damaged_pixels.csv', 1)
            else:
                for i in range(1, self.numdamages.get()+1):
                    im.count_pixels(self.progression.get()+ '/damage'+str(i)+'/crop/', os.getcwd()+ '/__resulting__/' +self.twd.get()+'/damaged_pixels.csv', i)
    

            
    '''single damage tab methods'''
    def load_damages(self, window = None):
        # populates the 'Evaluate Single Damage' tab. This shows the localized frame, then gives options to evaluate
        # each damage. This is a seperate function from making the tab, since in a new project there would be no 
        # existing localized frame, or counted damages
        if window == None:
            window = self.tab4
        self.load_setting()
        if self.numdamages.get()==1:
            self.show_error(window, 'These functions are only for videos with multiple damages. Only one damage exists in the current project.')
        else:

            for widgets in self.tab4.winfo_children():
                widgets.destroy()
            gc.collect()
            tk.Button(window, text = 'Load Damages', command = self.load_damages).grid(row = 0, column = 1, columnspan= 1)
            tk.Button(window, text = 'Instructions and Information', fg = 'green', command = lambda:[self.instructions(window, 'single')]).grid(row = 14, column = 1, columnspan= 1)
            self.crop_buffer = tk.IntVar()
            self.crop_buffer.set(0)
            try: 
                #this throws an error on purpose, because it the variable damagepicker before assignment
                #in order to assure that it is forgotten in the grid
                damagepicker.grid_forget()
                damagepicker2.grid_forget()
                
            except:
                pass
            try:
                self.get_damage_locations()
                num = im.count_damages(os.getcwd()+'/__resulting__/'+self.twd.get())
                self.numdamages.set(num)
                damagepicker = self.grid_image(window, imagepath=self.localizes.get()+'/finalimg0.png', row =2, column =1, rspan = self.numdamages.get()+2)
                try:
                    damagepicker = self.grid_image(window, imagepath=os.getcwd()+'/working/localize0.png', row =2, column =1, rspan = self.numdamages.get()+2)
                    damagepicker2 = self.grid_image(window, imagepath=self.masks.get()+'/mask0/', row = self.numdamages.get()+4, column =1, rspan = self.numdamages.get()+2)
                except:
                    pass
                
                #customizes the spacing
                if self.numdamages.get() == 1:
                    i= 1
                    tk.Button(window, text = 'Damage {0}'.format(i), command = lambda i=i: self.show_adjust_crop(window, i)).grid(row = i+2, column = 2)
                else:
                    for i in range(1, self.numdamages.get()+1):
                        tk.Button(window, text = 'Damage {0}'.format(i), command = lambda i=i: [ self.load_damages(window), self.show_adjust_crop(window, i)]).grid(row = i+2, column = 2)
            except:
                self.show_error(window, text = 'Please Localize Damages to Begin')
            
    def show_adjust_crop(self,window,number):
        # this function is called when a damage is selected in the 'Evaluate Single Damage' tab. it takes in the number
        # of the damage selection, and shows the slider to add the buffer pixels.
        try:
            #this throws an error on purpose, because it is referencing variables before assignment
            #in order to assure that they are forgotten in the grid
            label.grid_forget()
            self.apply_crop.grid_forget()
            name.grid_forget()
        except:
            pass
        try:
            self.make_folder(self.progression.get()+'/damage{0}/'.format(number), 'graph') 
            adj_crop_path=self.progression.get()+'/damage{0}/crop/mask0.png'.format(number).replace('\\', '/')
            self.num_choice = number
            to_crop= Image.open(adj_crop_path)
            #make the damage 50x50. this will already be a square
            resize_image = to_crop.resize((50, 50))
            
            name = tk.Label(window, text = 'Damage {0}'.format(number))
            name.grid(row = 2, column = 3)
            test = ImageTk.PhotoImage(resize_image)
            label = tk.Label(window, image=test)
            label.image = test
            if self.numdamages.get()>3:
                row_span = self.numdamages.get() -2
                label.grid(row = 3, column = 3, rowspan= row_span)
            
                value = tk.Scale(window, from_= -10,to = 10, orient='horizontal', variable=self.crop_buffer, tickinterval=5)
                value.grid(row = self.numdamages.get()+1, column = 3, sticky=tk.N, padx=10)
                
                self.apply_crop = tk.Button(window, text = 'Adjust Crop', command = lambda: self.adjust_crop(window, number))
                self.apply_crop.grid(row = self.numdamages.get()+2, column = 3)
            else:
                row_span = self.numdamages.get()
                label.grid(row = 3, column = 3, rowspan= row_span)
            
                value = tk.Scale(window, from_= -10,to = 10, orient='horizontal', variable=self.crop_buffer, tickinterval=5)
                value.grid(row = self.numdamages.get()+3, column = 3, sticky=tk.N, padx=10)
                
                self.apply_crop = tk.Button(window, text = 'Adjust Crop', command = lambda: self.adjust_crop(window, number))
                self.apply_crop.grid(row = self.numdamages.get()+4, column = 3)
        except:
            self.show_error(window, text = 'An error occured. Please make sure that the Damage Progression Process has been completed.')
    
    def adjust_crop(self, window, number):
        #this refreshes the crop on the selected damage in the 'Evaluate Single Damage' tab. The user is then given
        #the option to apply the new crop to show results, or just to show the results.
        try:
            #this throws an error on purpose, because it the variable damagepicker before assignment
            #in order to assure that it is forgotten in the grid
            apply.grid_forget()
            label.grid_forget()
            name.grid_forget()
        except:
            pass
        self.make_folder(self.progression.get()+'/damage{0}/'.format(number), 'graph')
        name = tk.Label(window, text = 'Damage {0}'.format(number))
        name.grid(row = 2, column = 3)
        x,y,c = im.get_indv_coords(os.getcwd()+ '/__resulting__/' +self.twd.get()+'/damage_localization.csv', number)
        full_mask = self.masks.get()+'/mask0.png'
        fullm = Image.open(full_mask)
        b = self.crop_buffer.get()
        new_crop= fullm.crop((x-c- b,y-c-b,x+c+b, y+c+b))
        resize_image = new_crop.resize((50,50))
        test = ImageTk.PhotoImage(resize_image)
        label = tk.Label(window, image=test)
        label.image = test

        line = tk.Radiobutton(window, text = 'Linear Fit', value =0, variable= self.fit_var)
        curve = tk.Radiobutton(window, text = 'Quadratic (Curve) Fit', value = 1, variable= self.fit_var)
        if self.numdamages.get()>3:
            row_span = self.numdamages.get() -2
            label.grid(row = 3, column = 3, rowspan= row_span)
        
            value = tk.Scale(window, from_= -10,to = 10, orient='horizontal', variable=self.crop_buffer, tickinterval=5)
            value.grid(row = self.numdamages.get()+1, column = 3, sticky=tk.N, padx=10)
            
            self.apply_crop = tk.Button(window, text = 'Adjust Crop', command = lambda: self.adjust_crop(window, number))
            self.apply_crop.grid(row = self.numdamages.get()+2, column = 3)
            apply = tk.Button(window, text = 'Apply Crop to All Frames and Show Results', command = lambda : self.recrop_damage(window, number, x-c- b, y-c-b, x+c+b, y+c+b))
            apply.grid(row = self.numdamages.get()+4, column = 3)
            apply1 = tk.Button(window, text = 'Show Results with Default Crop', command = lambda : self.eval_indv_damage(window, number))
            apply1.grid(row = self.numdamages.get()+5, column = 3)
            line.grid(row = self.numdamages.get()+6, column = 3)
            curve.grid(row = self.numdamages.get()+7, column = 3)
        else:
            row_span = self.numdamages.get()
            label.grid(row = 3, column = 3, rowspan= row_span)
        
            value = tk.Scale(window, from_= -10,to = 10, orient='horizontal', variable=self.crop_buffer, tickinterval=5)
            value.grid(row = self.numdamages.get()+3, column = 3, sticky=tk.N, padx=10)
            
            self.apply_crop = tk.Button(window, text = 'Adjust Crop', command = lambda: self.adjust_crop(window, number))
            self.apply_crop.grid(row = self.numdamages.get()+4, column = 3)
            apply = tk.Button(window, text = 'Apply Crop to All Frames and Show Results', command = lambda : self.recrop_damage(window, number, x-c- b, y-c-b, x+c+b, y+c+b))
            apply.grid(row = self.numdamages.get()+5, column = 3)
            apply1 = tk.Button(window, text = 'Show Results with Default Crop', command = lambda : self.eval_indv_damage(window, number))
            apply1.grid(row = self.numdamages.get()+6, column = 3)
            line.grid(row = self.numdamages.get()+7, column = 3)
            curve.grid(row = self.numdamages.get()+8, column = 3)
            
        
    def recrop_damage(self, window, number, left, upper, right, lower):
        #when the user applies the crop to the damage, and graphs the results of the counts of damaged pixels
        #this function applies it, and then saves and displays a video of the resulting graphs
        frame_path = self.masks.get().replace('\\', '/')
        save_path = self.progression.get()+'/damage{0}/crop/'.format(number).replace('\\', '/')
        im.crop(frame_path, save_path, left, upper,right,lower)
        c= (right - left) /2
        im.update_single_crop(os.getcwd() + '/__resulting__/' + self.twd.get()+'/damage_localization.csv', number, c)
        
        self.evaluate_damage(window, number)
        path = self.progression.get()+'/damage{0}/graph/'.format(number).replace('\\', '/')
        im.combine(path, path)
        try:
            self.grid_video(window,self.progression.get()+'/damage{0}/graph/savedvideo.wmv'.format(number), 1, 4, self.numdamages.get()+2, 10 )

        except:
            tk.Label(window, text = 'unable to play video').grid(row = 1, column = 4)
        gc.collect()
        
    def eval_indv_damage(self, window= None, number =1):
        #if there are not any graphs for the selected damage, then call new ones from the damaged
        #then, display the video of the resulting graphs
        if window == None:
            window = self.tab4
        #check if any graphs exist, if so, do not generate any new graphs
        if os.path.exists(self.progression.get()+'/damage{0}/graph/damage{0}fig0.png'.format(number)):
            pass
        else:
            self.evaluate_damage(window, number)
            path = self.progression.get()+'/damage{0}/graph/'.format(number).replace('\\', '/')
            im.combine(path, path)
        try:
            self.grid_video(window, self.progression.get()+'/damage{0}/graph/savedvideo.wmv'.format(number), 1, 4, self.numdamages.get()+2, 10, square = True)

        except:
            tk.Label(window, text = 'unable to play video').grid(row = 1, column = 4)
        gc.collect()
    

    def evaluate_damage(self, window, number):
        #counts the number of damaged pixels in all damages, then generates damages for the selected damage
        graph_path = self.make_folder(self.progression.get()+'/damage'+str(number), '/graph/')
        crop_path = self.progression.get()+'/damage'+str(number)+ '/crop/'
        #count pixels for ALL damages, just to be safe
        for i in range(1, self.numdamages.get()+1):
            im.count_pixels(self.progression.get()+'/damage'+str(i)+'/crop/', os.getcwd()+ '/__resulting__/' +self.twd.get()+'/damaged_pixels.csv', i)
        #graph the changes just in (number) damage
        im.make_graph(file_path = os.getcwd()+ '/__resulting__/' +self.twd.get()+'/damaged_pixels.csv', save_path = graph_path, number =number, frame_path = crop_path, fit = self.fit_var.get())
        gc.collect()
        
        
    '''results tab helper methods'''
    
    def generate_results(self, window):
        #makes full siz image spread of results, with frames from each step, based on the current project
        try:
            self.results_video.grid_forget()
        except:
            pass
        if os.path.isfile(self.results.get()+'/savedvideo.wmv'):
            save_path = self.results.get()
            self.results_video = self.grid_video(window, save_path+'/savedvideo.wmv', 2, 2, rowspan= 3)
        else:
            #makes sure that the paths are in a good format
            path1 = self.frames.get()
            path2 = self.crops.get().replace('/','\\')
            path3 = self.masks.get().replace('/','\\')
            path4 = self.segments.get().replace('/','\\')
            path5 = self.localizes.get().replace('/','\\')
            path6 = (self.progression.get()+'graphs/').replace('/','\\')
            pathlist = [path1,path2,path3,path4,path5,path6]
            save_path = self.make_folder(os.getcwd() + '/__resulting__/' + self.twd.get() + '/', 'results')
            try:
                #hopefully this will make things okay if there arent the same # of everything?
                im.make_results(pathlist,save_path)
            except:
                self.show_error(window, text = 'unable to generate results')
            try:
                im.combine(save_path, save_path)
            except:
                self.show_error(window, text = 'unable to generate video')
            try:
                self.results_video =self.grid_video(window, save_path+'/savedvideo.wmv', 2, 2, rowspan= 3)
            except:
                self.show_error(window, 'unable to show video')
        gc.collect()
    
    '''settings tab helper methods'''
    def build_setting(self, window = None, name = 'Directory', variable = None, options = [], column = 1, row= 0, refresh_button = None):
        #in 'Settings' tab, shows what curent value is, and allows for choice from a option menu
        #or inputting a new value. returns the button with the chosen value, as well as the text input
        tk.Label(window, text = name + ' Setting', bg = 'lightgrey').grid(row = (row+1), column = column)
        temp1 = tk.Button(window, text = 'Current '+ name +': ' +str(variable.get()))
        temp1.grid(row = (row+2), column = column)
        tk.OptionMenu(window, variable, variable.get(), *options).grid(row =( row+4), column = column)

        tk.Label(window, text = 'Input New '+name).grid(row = (row+5), column = column)
        temp2 = tk.Text(window, height = 1, width = 5)
        temp2.grid(row = (row+6), column = column)
        refresh_button.grid(row = (row+7), column = column, pady=10, sticky = tk.N )
        return temp1, temp2

    
    def save_settings(self):
        #saves current settings to a .csv file called settings. First updates all settings so they are current.
        self.update_setting_wdir(row= 2, column=1)
        self.update_setting_thresh(row=2, column=2)
        self.update_setting_crop(row=2, column=3)
        self.update_setting_kernel0(row= 11, column = 1)
        self.update_setting_kernel1(row = 11, column=2)
        self.update_setting_blur(row= 11, column=3)
        
        
        self.save_path = os.getcwd()+ '/__resulting__/' + self.twd.get() + '/settings.csv'
        file1 = open(self.save_path, 'w', newline='')
        writer1= writer(file1)
    
        content = []
        content.append(self.twd.get())
        content.append(self.threshold_slide.get())
        content.append(self.left.get())
        content.append(self.upper.get())
        content.append(self.right.get())
        content.append(self.lower.get())
        content.append(self.kernel0.get())
        content.append(self.kernel1.get())
        content.append(self.blur_thresh.get())
    
        writer1.writerow(content)
        
        content2 = []
        try:
            content2.append(im.count_frames(self.frames.get()))
            content2.append(im.count_damages(os.getcwd()+'/__resulting__/'+self.twd.get()))
            writer1.writerow(content2)
        except:
            pass
        
        file1.close()
       
    def load_setting(self):
        #loads in the saved settings from the current project. automatic when switching projects
        i= 0
        self.save_path = os.getcwd()+ '/__resulting__/' + self.twd.get() + '/settings.csv'
        
        try:
            file1 = open(self.save_path, 'r', newline='')
            r = reader(file1)
            for row in r:
                if i ==0:
                    self.threshold_slide.set(row[1])
                    self.left.set(row[2])
                    self.upper.set(row[3])
                    self.right.set(row[4])
                    self.lower.set(row[5])
                    self.kernel0.set(row[6])
                    self.kernel1.set(row[7])
                    self.blur_thresh.set(row[8])
                if i ==1:
                    self.num_frames.set(row[0])
                    self.numdamages.set(row[1])
                i=i+1
            file1.close()
        except:
            pass
       
    def update_setting_wdir(self, row, column, window = None):
        #checks if a new project has been added, if so, makes the empty folders for it.
        if window == None:
            window = self.tab3
        if len(self.input_dir.get("1.0", 'end-1c'))>2:
            self.update_project(self.input_dir.get("1.0", 'end-1c'))
            self.damagefolders.append(self.twd.get())
            self.update_project(self.input_dir.get("1.0", 'end-1c'))
            self.make_folder('__resulting__/',self.twd.get())
            self.make_folder('__resulting__/'+self.twd.get()+'/', "1Frames")
            self.make_folder('__resulting__/'+self.twd.get()+'/', "2Cropped_Frames")
            self.make_folder('__resulting__/'+self.twd.get()+'/', "3Threshold_Mask")
            self.make_folder('__resulting__/'+self.twd.get()+'/', "4Segmented_Damages")
            self.make_folder('__resulting__/'+self.twd.get()+'/', "5Localized_Damages")
            self.make_folder('__resulting__/'+self.twd.get()+'/', "6DamageProgression")
            self.input_dir.delete('1.0',tk.END)
        
        self.load_setting()
            
        self.curr_dir = tk.Button(window, text = 'Current Project: '+self.twd.get())
        self.curr_dir.grid(row = row, column = column)
 
    def update_setting_crop(self, row, column, window = None):
        #brings the value from the crop tab to the setting tab. 
        if window == None:
            window = self.tab3
        self.crop_but = tk.Button(window, text = 'left = ' + str(self.left.get())+' upper = '+ str(self.upper.get()) + ' right = ' + str(self.right.get()) +' lower = '+str(self.lower.get()))
        self.crop_but.grid(row = 2, column = 3, padx= 5)
     
    def update_setting_kernel0(self, row, column, window = None):
        #updates the kernel 0 value to either the text or slider input from the mask tab
        if window == None:
            window = self.tab3
        if len(self.input_kernel0.get(1.0,3.0))!=1:
            self.kernel0.set(int(self.input_kernel0.get(1.0,3.0)))
        self.kernel0_but = tk.Button(window, text = 'Current Kernel 0 : '+str(self.kernel0.get()))
        self.kernel0_but.grid(row = row, column = column)
        
    def update_setting_kernel1(self, row, column, window = None):
        #updates the kernel 1 value to either the text or slider input from the mask tab
        if window == None:
            window = self.tab3
        if len(self.input_kernel1.get(1.0,3.0))!=1:
            self.kernel1.set(int(self.input_kernel1.get(1.0,3.0)))
        self.kernel1_but = tk.Button(window, text = 'Current Kernel 1: '+str(self.kernel1.get()))
        self.kernel1_but.grid(row = row, column = column)
            
    def update_setting_thresh(self, row, column, window = None):
        #updates the threshold value to either the text or slider input from the mask tab
        if window == None:
            window = self.tab3
        
        if len(self.input_thresh.get(1.0,3.0))!=1:
            self.threshold_slide.set(int(self.input_thresh.get(1.0,3.0)))
            self.thresh_options.append(str(self.threshold_slide.get()))
        self.thresh_but = tk.Button(window, text = 'Current Threshold: '+str(self.threshold_slide.get()))
        self.thresh_but.grid(row = row, column = column)
        
    def update_setting_blur(self, row, column, window = None):
        #updates the blur value to either the text or slider input from the mask tab
        if window == None:
            window = self.tab3
        
        if len(self.input_blur.get(1.0,3.0))!=1:
            self.blur_thresh.set(int(self.input_blur.get(1.0,3.0)))
        self.blur_but = tk.Button(window, text = 'Current Blur: '+str(self.blur_thresh.get()))
        self.blur_but.grid(row = row, column = column)
    
    def open_and_show(self, path):
        #opens the folder at the path, so the user can see if there are any issues. shows an error pop up if there are issues
        if os.path.exists (os.getcwd() + '/__resulting__/' + self.twd.get()+path):
            pathout =  os.getcwd() + '/__resulting__/' + self.twd.get()+path
            pathout = os.path.realpath(pathout)
            
            os.startfile(pathout)
        else:
            self.show_error(text=path + ' does not contain any files.')


    '''other helper methods'''
    def update_project(self, value=None):
        #updates the working directory, and the other varible paths.
        if value == None:
            value = self.twd.get()
        self.twd.set(value)
        self.frames.set((os.getcwd() + '/__resulting__/' + self.twd.get()+'/1Frames/').replace('\\','/'))
        self.crops.set((os.getcwd() + '/__resulting__/' + self.twd.get()+'/2Cropped_Frames/').replace('\\','/'))
        self.masks.set((os.getcwd() + '/__resulting__/' + self.twd.get()+'/3Threshold_Mask/').replace('\\','/'))
        self.segments.set(os.getcwd() + '/__resulting__/' + self.twd.get()+'/4Segmented_Damages/')
        self.localizes.set(os.getcwd() + '/__resulting__/' + self.twd.get()+'/5Localized_Damages/')
        self.progression.set(os.getcwd() + '/__resulting__/' + self.twd.get()+'/6DamageProgression/')
        self.results.set(os.getcwd() + '/__resulting__/' + self.twd.get()+'/results/')
        self.load_setting()
        
        
    def instructions(self, window, tab):
        #makes a new pop up message with the instructions, depending on the tab. 
        top= tk.Toplevel(window)
        top.geometry("600x600")
        
        root.eval(f'tk::PlaceWindow {str(top)} center')
        text = ''
        if tab == 'home':
            text = '''In order to analyze your inputs, please select a video by clicking the \'Begin New Project\' Button. The video should be a .wmv file, of a thermal imaging recording of blade damages.
            \n The thermal video MUST be in either Greyscale or Fusion. \n You will be asked for the name you would like for your project, and all analysis will be completed in a folder with that name.
            \n You will also be asked for the frame spacing. This is an option for projects with very long videos. By indicating a frame spacing value of more than one, that number of frames will be skipped and not processed. A frame spacing value of 2 means every other frame is processed. Skipping frames may not give the most accurate analysis result. '''
        if tab == 'crop':
            text = '''Here you can crop an individual frame of your video, in order to focus only on the damaged section of the blade. This crop will be applied to all frames of the video.The default image is the first frame of the inputted video. Click and drag your mouse over the image to make a selection. Then, that selection can be applied to every frame of the video. 
            \nIt is recommended that the video is cropped as close to the damage as possible, while ensuring that all parts of the damage are still in frame. It is very beneficial to ensure that any hot spots that do not occur on the turbine blade are also cropped, as those can be falsely identified as damages. '''
        if tab == 'mask':
            text = '''In order to detect the damages, a \'binary mask\' is used. This is an image with the same dimension as the cropped thermal image, but with the damages in white, and all other pixels black. This is used both to locate and count the size of the damages. The goal of the mask is to clearly distinguish the areas of interest (damages) from surrounding structures. 
            To get the most accurate results, adjust all four sliders until the white mask perfectly covers the damages, and the right most image shows all the damage masked out.
            The threshold slider dictates what threshold value (ie greyscale value) on the thermal image (can distinguish the damaged pixels from the surrounding image). A lower threshold will include darker pixels in the mask. The threshold values range from 0-255 following greyscale color values from dark to light. (low threshold value, detect low intensity)
            So if the threshold slider is set to 0, all colors can be considered damages as all parts of the video will be brighter than black. Likewise, if the value is 255, then no colors will be considered damaged, since nothing is lighter than pure white. 
            \nThe other three sliders adjust the third image from the second, consolidating the damages into clear areas. The kernels controls the \’opening and closing \’  of the mask. These concepts are used in  computer vision for noise removal, and isolating important components of the image. This is a succinct description from Wikipedia: 
            ¨ Opening removes small objects from the foreground (usually taken as the bright pixels) of an image, placing them in the background, while closing removes small holes in the foreground, changing small islands of background into foreground¨. More information can be found at these sites:
            \nhttps://homepages.inf.ed.ac.uk/rbf/HIPR2/open.htm
            https://en.wikipedia.org/wiki/Opening_%28morphology%29
            \nIt is not essential to perfectly understand these concepts in order to create a good damage mask. It is recommended to take time and adjust both values with trial and error.
            
            \nThe blur slider controls the Gaussian Blur. This smooths the boundaries of the image and can help define damage shapes. A smaller number means a less blurred image. It should be noted that the actual blur number used is 1/100th of the slider value. The blur must never be set to 0. 
            \nAll of these slider values can also be adjusted in the \’Settings\’  tab, and saved for this project.
            If you select \’Go\’ without choosing an image, the most recent cropped section will be used.'''
    
        if tab == 'detect':
            text = '''Either choose to complete the steps of damage detection one by one, or select complete damage detection. The complete detection will draw from and save all files to your working project. 
            \nIf there are existing files for any of the damage detection steps, then that part of the process will be skipped. Check what already exists in this project in the \'Settings\'  tab.
            \nThe individual steps allow for each portion of the process to take place independently. This is not recommended, as it may cause issues with the other gui features, as files may not be organized in the typical way. 
            \nFor damage detection, a video is first split into its individual frames to be analyzed. Then those frames can be cropped to focus more closely on only the damaged portion. Then a mask of the image is generated, where white portions represent the damages, and the rest of the image is black. 
            \nThen the damages are segmented, and the damaged pixels removed from the cropped frames using the generated mask. The damages can also be localized and labeled. 
            \nThis process can take a long time, especially if your video has many frames. You can monitor the progress in your project folder.. A window will pop up when the process is complete. '''
        if tab == 'eval':
            text = '''Once damages are detected, they can be evaluated by counting their area based on the damage mask generated previously. 
            If you wish to generate new evaluation results, first clear the previous analysis. If you have already performed an analysis and do not clear the previous, the previous results will be displayed.
            You can either choose to quantify your damage area based on individual damages, or the whole image. If you choose the whole image, individual hot spots are not localized.
            Then the steps will locate the damages in the cropped frames, then crop a small section around each damage in the binary mask. 
            The white - damaged -  pixels in these selections will be counted. Finally, the growth of each damage will be graphed all together. Selecting ‘Generate Damage Progression Data’ will perform these in order.
            This process can take a long time, especially if your video has many frames. You can monitor the progress in your project folder. If new data is generated, a window will pop up when the process is complete.

            '''

        if tab == 'single':
            text = '''Once damages are localized, select load damages, and choose which damage to analyze. You will then see the binary mask of the damage. 
            \nThe slider below the damage can be used to expand the crop, and ensure that all of the damaged pixels are included in the analysis. Then the number of damaged pixels across the fatigue cycles is graphed. 
            \nThis process can take a long time, especially if your video has many frames. You can monitor the progress in your project folder. 
            '''
        
        if tab =='results':
            text = '''Click \'Generate Results\' to combine the video frames, cropped images, binary masks, segmented images, localized images, and damage progression graphs into one video. 
            It is important that all steps are completed prior to this combination. If for any reason (processing space, incomplete previous analysis, ect) it is not possible to generate the results for every frame, the partial results will be generated, and saved.
            \nThis process can take a long time, especially if your video has many frames. You can monitor the progress in your project folder. '''
        
        
        if tab =='settings':
            text = '''Select an option from the drop down menu, or input your own new option. Select the ‘Update’ value below the option to load the change. Select ‘Save Settings’ to save your choices in a particular project. 
            \nView steps in the damage detection process, by selecting the step on the right hand side.'''
        
        tk.Label(top, text = text, wraplength = 550).pack()
    
    def clear_last(self, file_path, file = None):
        #clears the 'last' instance of an evaluation, aka deletes the given folder and file.
        for files in os.listdir(file_path):
            if files == '1Frames':
                pass
            else:
                path = os.path.join(file_path, files)
            
                try:
                    shutil.rmtree(path)
                except OSError:
                    os.remove(path) 
        if file!= None:
            try:
                os.remove(file)
            except FileNotFoundError:
                pass

    def grid_video(self, window, file_path, row, column, rowspan = 1, replayrow = None, square = False):
        #displays a video on the tab, in a grid format. 
        if replayrow == None:
            replayrow = row + rowspan 
        l1 = tk.Label(window)
        l1.grid(row = row, rowspan= rowspan, column = column)
        if not square:
            width, height = im.get_vid_size(file_path)
            width, height = im.get_vid_scale(self.width, self.height, width, height)
        else: 
            width = 400
            height = 400
        player = tkvideo(file_path, l1, loop = 0, size = (width,height))
        player.play()
        tk.Button(window, text = 'replay', command = lambda: [player.play()]).grid(row = replayrow, column = column)
        return l1
    
    def show_video(self, window= None, file_path = None):
        #shows a video using tkvideo. must be in a 'pack' environment (not grid)
        if window == None:
            window = self.tab7
        if file_path == None: 
            file_path = self.open_file(prompt = 'Chose a Video To Display')
        l1 = tk.Label(window)
        l1.pack()
        #make sure that the height will fit on the screen
        width, height = im.get_vid_size(file_path)
        width,height = im.get_vid_scale(self.width, self.height,width, height)

        player = tkvideo(file_path, l1, loop = 0, size = (width,height))
        player.play()
        tk.Button(window, text = 'replay', command = lambda: [player.play()]).pack()
     
    def dummy(self):
       #temporary function to test buttons
       self.show_error("Wow! You pushed a button!")
        
    def print_text(self, text, window = None):
        #displayes text on the given frame
        #must be in a tab that uses pack, NOT grid
        if window == None:
            window = self.tab0
        tk.Label(window, text=text).pack()
    
    def show_image(self, window, imagepath, alignment = tk.TOP, padx = 0, pady= 0):
        #displayes image on the given frame
        #must be in a tab that uses pack, NOT grid
        image = Image.open(imagepath)
        test = ImageTk.PhotoImage(image)
        label17 = tk.Label(window, image=test)
        label17.image = test
        label17.pack(side = alignment, padx = padx, pady= pady)
        
    def grid_image(self, window, imagepath, row, column, rspan = 1):
        #displayes image on the given frame
        #must be in a tab that uses grid, NOT pack
        image = Image.open(imagepath)
        test = ImageTk.PhotoImage(image)
        label = tk.Label(window, image=test)
        label.image = test
        label.grid(row = row, column = column, rowspan=rspan)
        return label             

    def open_dir(self, prompt ="Choose folder", default = None, show = False):
        #chooses a folder, and opens it. 
        if default == None:
            default = self.twd.get()
        if show:
            try:
                filepath = askopenfilename(initialdir= default , title=prompt)
                directory = os.path.split(filepath)[0]
            except:
                filepath = askopenfilename(initialdir= self.twd.get() , title=prompt)
                directory = os.path.split(filepath)[0]
        else:
            try:
                directory = askdirectory(initialdir= default , title=prompt)
            except:
                filepath = askopenfile(initialdir= self.twd.get() , title=prompt)
        return directory + '/'
        
       
    def open_file(self,file_types=[("all files","*.*")], prompt = 'select file', start_dir = None):
        #returns file path, can specify prompt text and initial directory
        if start_dir == None:
            start_dir = self.twd.get()
        file_path = askopenfile(mode='r', title=prompt, filetypes=file_types, initialdir= start_dir)
        filepath = file_path.name

        return filepath
 
    def make_folder(self, path, name):
        #makes new directory with name at path.
        #returns path name, passes even if directory already exists

        try:
            os.mkdir(path+'/'+name)
            new_path = path+'/'+name + '/'
            new_path.replace('\\','/')
            return new_path
        except FileExistsError:

            retpath = path+'/'+name + '/'
            retpath = retpath.replace('\\','/')
            retpath = retpath.replace('//','/')
            return retpath
        except:
            self.show_error(text ='error in creating new folder')
            retpath = path+'/'+name + '/'
            retpath = retpath.replace('\\','/')
            retpath = retpath.replace('//','/')
            return retpath

    def show_error(self, window= None, text = 'There was an Error'):
        #creates a pop up with an error in red text
        if window == None:
            window = self.tab0
        #Create a Toplevel window
        top= tk.Toplevel(window)
        top.geometry("250x50")
        
        root.eval(f'tk::PlaceWindow {str(top)} center')
     
        #Create an Entry Widget in the Toplevel window
        tk.Label(top, text = text, fg = 'red' , wraplength = 230).pack()
    
    def move_on(self, window= None, text = 'Step completed, ready to move on.'):
        #creates a pop up sharing when the user has completed a long step and can move on
        if window == None:
            window = self.tab0
        #Create a Toplevel window
        top= tk.Toplevel(window)
        top.geometry("250x50")
        
        root.eval(f'tk::PlaceWindow {str(top)} center')
     
        #Create an Entry Widget in the Toplevel window
        tk.Label(top, text = text, wraplength = 230).pack()  
        
     
            
    def on_closing(self):
        #when the gui is closed, the working directory is cleared. 
        try:
            os.remove(os.getcwd().replace('\\','/')+'/working/crop0.png')
        except FileNotFoundError:
            pass   
        try:   
            os.remove(os.getcwd().replace('\\','/')+'/working/adjust0.png')
            os.remove(os.getcwd().replace('\\','/')+'/working/seg0.png')
            os.remove(os.getcwd().replace('\\','/')+'/working/mask0.png')
        except FileNotFoundError:
            pass
        try:
            os.remove(os.getcwd().replace('\\','/')+'/working/localized0.png')
        except FileNotFoundError:
            pass
        
        root.destroy()
        
'''main method to instantiate GUI'''
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root,"AQUADA GUI", "1500x750") 
    #Default size: 1500x750 
    #Figures in paper: 750x600
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    app.pack()
    root.mainloop()
    


    