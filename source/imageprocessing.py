# -*- coding: utf-8 -*-
"""
Created on Fri Sep  2 13:35:51 2022

@author: catspe
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
import cv2  ## import the required library
from numpy import ones, uint8, where, all, array
from pandas import DataFrame, read_csv
import glob2 as glob
import regex as re
import os
import gc
import csv
from math import floor, ceil
from PIL import Image
from imutils import contours, grab_contours
from scipy.optimize import curve_fit
from matplotlib import pyplot as plt
from matplotlib import pylab
import matplotlib.font_manager as font_manager
import matplotlib.colors as mcolors

   
def readvid(pathvid='C:', pathim= 'C:'):
    ### Reading input video frame by frame

    # Opens the Video file
    cap= cv2.VideoCapture(pathvid)  ## read the video frame by frame
    i=0
    while(cap.isOpened()):
        ret, frame = cap.read()  ## ret is a boolean regarding whether or not there is a frame.
        if ret == False:
            break
        cv2.imwrite(pathim+'img'+str(i)+'.png',frame)  ## save the images with png format
        i+=1
    cap.release()
    cv2.destroyAllWindows()

def select_frames(pathvid, pathim, num):
    ### Reading input video frame by frame

    # Opens the Video file
    cap= cv2.VideoCapture(pathvid)  ## read the video frame by frame
    i=0
    j=0
    while(cap.isOpened()):
        ret, frame = cap.read()  ## ret is a boolean regarding whether or not there is a frame.
        if ret == False:
            break
        if i%num == 0:    
            cv2.imwrite(pathim+'img'+str(j)+'.png',frame)  ## save the images with png format
            j+=1
        i+=1
    cap.release()
    cv2.destroyAllWindows()

def crop(frame_path='C:', save_path='C:',left =130, upper =0, right =480, lower=480):
    #crops the frames from frame path with the input dimensions, saves to savepath
    dirs = os.listdir(frame_path) #list all the frames to be cropped
    for item in dirs: #for each frame...
        fullpath = os.path.join(frame_path,item)         
        if os.path.isfile(fullpath):
            im = Image.open(fullpath)
            index = fullpath.rfind('/') #get the last instance of / just to get the file
            fullpath = fullpath[index:]
            file_name,e = os.path.splitext(fullpath) 
            imCrop = im.crop((left, upper, right, lower)) 
            imCrop.save(save_path + file_name + ".png", quality=100) # save the cropped images with the png format and quality of 100 (quality specifies the resolution of an image in a 1-100 scale)

def processing(frame_path ='C:', save_path ='C:',  threshold = 177, one = False ,kernel0val = 13, kernel1val = 3, blur_thresh = 0.8):
    #either masks one or all of the input videos according to the paramters input.
    kernel0 = ones((kernel0val,kernel0val),uint8) #(numpy.ones, numpy.uint8) 
    kernel1= ones((kernel1val,kernel1val),uint8) #define openign ang closing kernels
    imdir1 = frame_path 
    if one:
        img1= cv2.imread(frame_path) 
        gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (0, 0), blur_thresh)
        opening = cv2.morphologyEx(blurred, cv2.MORPH_CLOSE, kernel0)
        closing = cv2.morphologyEx(opening, cv2.MORPH_OPEN, kernel1)         
        thresh = cv2.threshold(closing, threshold, 255, cv2.THRESH_BINARY)[1] 
        cv2.imwrite(save_path+"adjust"+str(0)+".png", thresh)
    else:
        count = count_frames(frame_path)
        ext = ['png']    # could add image formats here
        files1 = []
        [files1.extend(glob.glob(imdir1 + '*.' + e)) for e in ext] #reads in all the files
        files1.sort(key=lambda x1:[int(c1) if c1.isdigit() else c1 for c1 in re.split(r'(\d+)', x1)]) #sorts files
        images1 = [cv2.imread(file1,cv2.IMREAD_COLOR) for file1 in files1]
        for j in range (0,count):
            img1=images1[j]
            gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY) #makes grey scale
            blurred = cv2.GaussianBlur(gray, (0, 0), blur_thresh) #applies blur
            opening = cv2.morphologyEx(blurred, cv2.MORPH_CLOSE, kernel0) #adjust morphology
            closing = cv2.morphologyEx(opening, cv2.MORPH_OPEN, kernel1)
            thresh = cv2.threshold(closing, threshold, 255, cv2.THRESH_BINARY)[1] 
            cv2.imwrite(save_path+"mask"+str(j)+".png", thresh) #saves
            j+=1  
    
def threshold(frame_path ='C:', save_path ='C:',  threshold = 177, one = False, kernel0val = 3, kernel1val = 13, blur_thresh = 0.8):
   ##  Generating masks of damaged and non-damaged pixels
   # IMPORTANT NOTE: the opening and closing kernels, as well as the blur threshold have been removed from this function
   # not used as if one is false typically
    imdir1 = frame_path 
    if one:
        img1= cv2.imread(frame_path)
        gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)[1] 
        cv2.imwrite(save_path+"mask"+str(0)+".png", thresh)

    else:
        count = count_frames(frame_path)
        ext = ['png']    # add image formats here
        files1 = []
        [files1.extend(glob.glob(imdir1 + '*.' + e)) for e in ext]
        files1.sort(key=lambda x1:[int(c1) if c1.isdigit() else c1 for c1 in re.split(r'(\d+)', x1)])
        images1 = [cv2.imread(file1,cv2.IMREAD_COLOR) for file1 in files1]
        for j in range (0,count):
            img1=images1[j]
            gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)[1]
            cv2.imwrite(save_path+"mask"+str(j)+".png", thresh)
            j+=1
        
def segmentation(frame_path='C:', mask_path='C:',save_path='C:', one = False):
        ### Damage segmentation, removing the mask areas from the full (cropped= image
    if one:
        #segment only one image
        img1 = cv2.imread(frame_path) #if there is only one, this will be a path to a file, not folder
        img2 = cv2.imread(mask_path)
        indecis=where(all(img2>=img1, axis=-1))  ## Find the pixels of img2>img1 (numpy.where, numpy.all)
        img1[indecis]=(0,0,0) ## set those pixels to black to remove the background
        cv2.imwrite(save_path+"seg"+str(0)+".png", img1) #save image
    else:
        #segment all of the files from a frame
        count = count_frames(frame_path) # number of frames to loop over
        imdir1 = frame_path+'img'
        imdir2 = mask_path+'mask'
    
        ext = ['png']    # add image formats here
        files1 = [] #empty list for the croped image files
        [files1.extend(glob.glob(imdir1 + '*.' + e)) for e in ext] #list all the files
        files1.sort(key=lambda x1:[int(c1) if c1.isdigit() else c1 for c1 in re.split(r'(\d+)', x1)]) #sort the files
        images1 = [cv2.imread(file1) for file1 in files1] #read in a list of images
    
        files2 = [] #empty list for threshold binary masks
        [files2.extend(glob.glob(imdir2 + '*.' + e)) for e in ext]
        files2.sort(key=lambda x1:[int(c1) if c1.isdigit() else c1 for c1 in re.split(r'(\d+)', x1)])
        images2 = [cv2.imread(file2) for file2 in files2]
        for i in range (0,count): #loop over all of the frames
            img1=images1[i]
        
            img2=images2[i]
        
            indecis=where(all(img2>=img1, axis=-1))  ## Find the pixels of img2>img1
            img1[indecis]=(0,0,0)                           ## set those pixels to black to remove the background
            cv2.imwrite(save_path+"seg"+str(i)+".png", img1) #save
            i+=1

def localize(frame_path ='C:',thresh_path ='C:',save_path ='C:',data_path = 'C:', one = False ):
    #both makes and saves the images with the localization, and saves the data
    stats = {} #need to track lots of the things for each 
    count = count_frames(frame_path) 
    #counting the contours on just the last image
    if one:
        j=0
        thresh_path = thresh_path + '/mask{0}.png'.format(count -1)
        frame_path = frame_path + '/img{0}.png'.format(count -1)
        img1 = cv2.imread(thresh_path,cv2.IMREAD_COLOR)
        img2 = cv2.imread(frame_path,cv2.IMREAD_COLOR)
        img1=cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)  ## convert the (segmented) images to grayscale format
        cnts = cv2.findContours(img1.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)                 ## find the contours in the binary masks using cv2.findContours and grab_contours
        
        cnts = grab_contours(cnts)
        cnts = contours.sort_contours(cnts)[0]       ## sort the contours from left to right 
        var=0
        for (i, c) in enumerate(cnts):
    	# draw the bright spot on the image
            [x, y, w, h] = cv2.boundingRect(c) 
            ((cX, cY), radius) = cv2.minEnclosingCircle(c) #make a circle arround the episode
            cv2.circle(img2, (int(cX), int(cY)), int(1.5*radius),(0, 0, 0), 1)  ## draw a circle around the damage in black color(0,0,0) and thickness of 1.
            cv2.putText(img2, "#Damage{}".format(i + 1), (x, y+15),             ## To put text for each damage with black color and thickness of 1.
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1) 
            cv2.imwrite(save_path+"localized"+str(j)+".png",img2) #save the image!
            if j == 0: #is this is the first frame, initialize the damage localization csv
                stats[str(i+1)] = {'x':[],'y':[], 'c':[]}
                stats[str(i+1)]['x'].append(cX)
                stats[str(i+1)]['y'].append(cY)
                stats[str(i+1)]['c'].append(radius)
        f = open(data_path+'/damage_localization.csv', 'w', newline='')
        writer= csv.writer(f)
        
        for (i,c) in enumerate(cnts): 
            content = []
            content.append(max(stats[str(i+1)]['x']))
            content.append(max(stats[str(i+1)]['y']))
            content.append(max(stats[str(i+1)]['c']))
            writer.writerow(content)
        
        f.close()
        return len(cnts)
    
    #this is for if you do the full thing:
    else:  
        imdir1 = thresh_path
        imdir2 = frame_path 
        
        ext = ['png']  # add image formats here
        
        #read in segmented image 
        files1 = []
        [files1.extend(glob.glob(imdir1 + '*.' + e)) for e in ext]
        files1.sort(key=lambda x1:[int(c1) if c1.isdigit() else c1 for c1 in re.split(r'(\d+)', x1)])
        images1 = [cv2.imread(file1,cv2.IMREAD_COLOR) for file1 in files1]
        #read in base thermal (cropped) image
        files2 = []
        [files2.extend(glob.glob(imdir2 + '*.' + e)) for e in ext]
        files2.sort(key=lambda x2:[int(c2) if c2.isdigit() else c2 for c2 in re.split(r'(\d+)', x2)])
        images2 = [cv2.imread(file2,cv2.IMREAD_COLOR) for file2 in files2]
        for j in range (0,count): #loop over all the frames
            img1=images1[j]
            img2=images2[j]
            
            img1=cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)  ## convert the (segmented) images to grayscale format
            cnts = cv2.findContours(img1.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)                 ## find the contours in the binary masks using cv2.findContours and grab_contours
            
            cnts = grab_contours(cnts)
            cnts = contours.sort_contours(cnts)[0]       ## sort the contours from left to right
            
            # loop over the contours
            var=0

            for (i, c) in enumerate(cnts):
        	# draw the bright spot on the image
                [x, y, w, h] = cv2.boundingRect(c)
                ((cX, cY), radius) = cv2.minEnclosingCircle(c) #draw a circle arround damage
                cv2.circle(img2, (int(cX), int(cY)), int(1.5*radius),(0, 0, 0), 1)  ## draw a circle around the damage in black color(0,0,0) and thickness of 1.
                cv2.putText(img2, "#Damage{}".format(i + 1), (x, y+15),             ## To put text for each damage with black color and thickness of 1.
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1) 
                cv2.imwrite(save_path+"finalimg"+str(j)+".png",img2) #save image
                if j == 0:
                    stats[str(i+1)] = {'x':[],'y':[], 'c':[]} #if this is the first frame, start the data
                stats[str(i+1)]['x'].append(cX)
                stats[str(i+1)]['y'].append(cY)
                stats[str(i+1)]['c'].append(radius)
                
            var+=1
               
            j+=1
        f = open(data_path+'/damage_localization.csv', 'w', newline='') #open the data file
        writer= csv.writer(f) #write the data to the data file
        for (i,c) in enumerate(cnts): #for each contour, save the biggest area of the enclosing circle
            content = []
            content.append(max(stats[str(i+1)]['x']))
            content.append(max(stats[str(i+1)]['y']))
            content.append(max(stats[str(i+1)]['c']))
            writer.writerow(content)
        f.close() #close the data writer
        return len(cnts) #return the number of hot spots
    
def crop_ind_damages(file_path, frame_path, save_path):
    #takes damage_localization which contains x, y, and center of enclosing circle.
    #frame path is any folder with the right number of images to consider
    #save path should be akin to /6DamageProgression, subfolders will be created if needed
    with open(file_path) as csv_file:
        c = csv.reader(csv_file)
        count = 0
        for row in c:
            try: 
                #get the coordinates from the location
                x = int(floor(float(row[0]))) #have to round somehow, x and y round down
                y = int(floor(float(row[1])))
                c = int(ceil(float(row[2]))) #round c up, to make sure the area is enclosed
                try:
                    #try to make all the folders
                    os.mkdir(save_path+'/damage'+str(count+1))
                    os.mkdir(save_path+'/damage'+str(count+1)+'/crop')
                    new_path = save_path+'/damage'+str(count+1)++'/crop/'
                    new_path.replace('\\','/')
                except:
                    new_path = save_path+'/damage'+str(count+1)+'/crop/'            
                crop(frame_path, new_path, left = x-c, upper = y-c, right = x+c, lower = y+c)
                count= count+1
            except:
                count = count #in case that there is an empty row in the data file
                
                
def get_indv_coords(file_path, number):
    #gets the coordinates of a single damage of number, number
     with open(file_path) as csv_file:
         c = csv.reader(csv_file)
         count = 1
         for row in c:
             try: 
                 x = int(floor(float(row[0])))
                 y = int(floor(float(row[1])))
                 c = int(ceil(float(row[2])))
                 if count == number:
                     return x, y, c
                 count= count+1
             except:
                 count = count
             
def update_single_crop(file_path, number, inc): 
    #recrop the damage, with inc number of pixels on each size
    count = 0
    existingdf = read_csv(file_path, header=None)
          
    for row in existingdf.head().itertuples():
        existingdf.at[count,2]
        count= count+1
        if int(count) == int(number):
            existingdf.at[count-1, 2] = inc
    existingdf.to_csv(file_path, header=False, index= False)
        

                 
def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
    #this makes sure that all files will go img0,img1,img2,img3 NOT img0, img1, img10
    return [
        int(text)
        if text.isdigit() else text.lower()
        for text in _nsre.split(s)]

def combine(frame_path, save_path, video_name = 'savedvideo'):
    #from https://www.geeksforgeeks.org/python-create-video-using-multiple-images-using-opencv/
    #assuming all images are same size already. 
    #stitches all the images back into a video

        
        #create list of images
        images0 = [img for img in os.listdir(frame_path)  if img.endswith(".jpg") or img.endswith(".jpeg") or img.endswith(".png")]
        images = sorted(images0, key=natural_sort_key)
        frame = cv2.imread(os.path.join(frame_path, images[0]))
        height, width, layers = frame.shape 

        #combine into video
        fourcc = cv2.VideoWriter_fourcc(*'wmv2')
        video = cv2.VideoWriter(save_path+'/'+video_name+'.wmv', fourcc , 10, (width, height)) 
        for image in images:
            video.write(cv2.imread(os.path.join(frame_path, image)))
            
        cv2.destroyAllWindows() 
        video.release()
        
def count_frames(frame_path):
    #based on a frame path, count the number of frames in the folder
    files = os.listdir(frame_path)
    count = 0 
    for file in files:
        if 'png' in file:
            count += 1
    return count

def count_damages(data_path):
    #based on the data sheet, count the number of hot spot/damages
    f = open(data_path+'/damage_localization.csv', 'r')
    count  = 0
    for row in f:
        if len(row) >3:
            count = count + 1
    f.close()
    return count
    
def count_pixels(frame_path, save_path, number):
    ## To count the number of pixels in the damage segmentation
    #outputs a datafile with pixel counts per damage per frame
    frame_path = frame_path.replace('//','/')
    num=[]
    count = count_frames(frame_path)
    if number == 1:
        existingdf = DataFrame()
    else:
        try:
            existingdf = read_csv(save_path)
            os.remove(save_path)
        except:
            existingdf = DataFrame()
    imdir1 = frame_path  ## bounding box found from damage localization code.
    ext = ['png']    # add image formats here
    files1 = []
    [files1.extend(glob.glob(imdir1 + '*.' + e)) for e in ext]
    files1.sort(key=lambda x1:[int(c1) if c1.isdigit() else c1 for c1 in re.split(r'(\d+)', x1)])
    images1 = [cv2.imread(file1,cv2.IMREAD_COLOR) for file1 in files1]        
    for j in range(count):
        ## The area around each damage is cropped through the damaged and non-damaged masks based on the coordinates of
        image=images1[j]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) ## convert the images to the grayscale format
        pixels = cv2.countNonZero(gray) ## count the number of non-zero pixels through images (the non-zero pixels are damage pixels)
        num.append(pixels)
        num_train=array([int(x) for x in num]) #ensures each pixel number is an integer type
        data=num_train
        j+=1
    existingdf['d'+str(number)] = data
 
    existingdf.to_csv(save_path, index=False, header=True)  ##  save the dataframe as csv file without index
    
def all_pixel_count(frame_path, save_path):
    #counts all of the pixels in the threshold mask, not just the individual crops. 
    #not currently used, but may be useful for masks with a non constant damage number
    frame_path = frame_path.replace('//','/')
    num=[]
    count = count_frames(frame_path)
    
    existingdf = DataFrame()

    imdir1 = frame_path  ## bounding box found from damage localization code.
    ext = ['png']    # add image formats here
    files1 = []
    [files1.extend(glob.glob(imdir1 + '*.' + e)) for e in ext]
    files1.sort(key=lambda x1:[int(c1) if c1.isdigit() else c1 for c1 in re.split(r'(\d+)', x1)])
    images1 = [cv2.imread(file1,cv2.IMREAD_COLOR) for file1 in files1]        
    for j in range(count):
          ## The area around each damage is cropped through the damaged and non-damaged masks based on the coordinates of
        image=images1[j]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) ## convert the images to the grayscale format
        pixels = cv2.countNonZero(gray) ## count the number of non-zero pixels through images (the non-zero pixels are damage pixels)
        num.append(pixels)
        num_train=array([int(x) for x in num]) #ensures each pixel number is an integer type
        data=num_train
        j+=1
    existingdf = data
    existingdf.to_csv(save_path, index=False, header=True)  ##  save the dataframe as csv file without index
    
def objective(x, a, b):
    #helper for linear regression when plotting damages
    return a * x + b  

def objective_curve(x, a, b,c):
    #helper for quadratic regression when plotting damages
    return a * x + b * x**2 + c
   
def make_graph(file_path, save_path,frame_path, number, fit = 0):
    #file of damage pixels counts, save path as save location, frame path with same number of frames as iterations
    #number indicates which damage is being graphed, must be looped over , or called again to analzye multipe damages
    data = read_csv(file_path)
    count = count_frames(frame_path)
    number = int(number)
    plt.ioff()
    
    #make a single plot with all of the data points first
    x = list(range(count))[0:count]
    y1 = list(data['d'+str(number)])[0:count]
    norm= y1[0]
    y = [i/norm for i in y1]
        
    if fit == 0:
        popt, _ = curve_fit(objective, x, y)
        a, b= popt
    if fit == 1:
        popt, _ = curve_fit(objective_curve, x, y)
        a, b,c= popt
        
    #set plot styles and labels
    plt.style.use('seaborn')
    fig=plt.figure(figsize=(90,90))  ## (90,90) (150,200)
    ax = plt.axes()
    csfont = {'fontname':'Times New Roman'}
    ax.set_facecolor("white")
    ax.patch.set_edgecolor('black')  
    ax.patch.set_linewidth('4')
    
    plt.xlabel('Number of frame', fontsize=220,**csfont)
    plt.ylabel('Normalized number of pixels\nin damage segmentation', fontsize=220,**csfont)
    plt.xticks(fontsize = 220,**csfont)
    plt.yticks(fontsize =220,**csfont)

    plt.scatter(x,y,marker=".",s=6000,edgecolors="black",c="black")
    x_line = pylab.arange(min(x), max(x), 1)
    # calculate the output for the range
    if fit == 0:
        y_line = objective(x_line, a, b)   
    if fit ==1:
        y_line = objective_curve(x_line, a, b,c)
    # create a line plot for the mapping function
    plt.plot(x_line, y_line, '--', color='black',linewidth=40,label='damage{0}'.format(number))
    font = font_manager.FontProperties(family='Times New Roman', size=150)
    plt.legend(prop=font)
    fig = plt.gcf()
    plt.tight_layout()
    
    #save figure, and clear some memory
    plt.savefig(save_path+'/damage{0}figall.png'.format(number), dpi = 14)
    fig.clf()
    plt.close()
    del x, y
    gc.collect()
    #end of making the single graph with all 
    
    #now, loop over each frame and graph all the data up until that frame
    #set up plot styles 
    
    for i in range (count-3):
        y1 = list(data['d'+str(number)])[0:i+3]
        x = list(range(i+3))
        norm= y1[0]
        y = [j/norm for j in y1] 
        if fit == 0:
            popt, _ = curve_fit(objective, x, y)
            a, b= popt
            
        if fit ==1:
            popt, _ = curve_fit(objective_curve, x, y)
            a, b,c= popt
        plt.style.use('seaborn')
        fig=plt.figure(figsize=(90,90))
        ax = plt.axes()
        csfont = {'fontname':'Times New Roman'}   
        ax.set_facecolor("white")
        ax.patch.set_edgecolor('black')  
        ax.patch.set_linewidth('4')
        plt.xlabel('Number of frame', fontsize=220,**csfont)
        plt.ylabel('Normalized number of pixels in \n damage segmentation', fontsize=220,**csfont)
        plt.xticks(fontsize = 220,**csfont)
        plt.yticks(fontsize =220,**csfont)
        font = font_manager.FontProperties(family='Times New Roman', size=150)
        plt.scatter(x,y,marker=".",s=6000,edgecolors="black",c="black")
    
        x_line = pylab.arange(min(x), max(x), 1)
    # calculate the output for the range
        if fit == 0:
            y_line = objective(x_line, a, b)   
        if fit ==1:
            y_line = objective_curve(x_line, a, b,c)
            
    # create a line plot for the mapping function
        plt.plot(x_line, y_line, '--', color='black',linewidth=40,label='damage{0}'.format(number))
    
        #plt.ylim(0,y_max)

        plt.legend(prop=font)
        fig = plt.gcf()
        plt.tight_layout()
    
        plt.savefig(save_path+'/damage{0}fig{1}.png'.format(number,i), dpi = 14)
        fig.clf()
        plt.close()
        del x, y
        i+= i
        gc.collect()
        
def plot_all(file_path, save_path, folder_path, number):
    #gets file of pixel count data, place to save, and folder of masks with same length as data.
    #plots points and linear regression for each damage on same figure, normalized to a percentage change
    #a new figure is made for each frame
    #plots the points and a curve for every damage on the same frame
    plt.ioff()
    data = read_csv(file_path)
    count = len(os.listdir(folder_path))
    number = number +1
    i = 0 #frame iterator
    normalizing = []
    

    for i in range(count-2): #loop over the number of frames
        j=1 #damage iterator
        
        points = {}
        labels = []
        
        for j in range(1,number): #loop over each damage
            #save the point values, as well as fit curve data in a dictionary, so all can be plotted on one plot.
            if i ==0:
                normalizing.append(list(data['d'+str(j)])[0])
            name_name = 'damage {0}'.format(j)
            x_name = 'x {0}'.format(j)
            y_name = 'y {0}'.format(j)
            xcurve_name = 'xcurve {0}'.format(j)
            ycurve_name = 'ycurve {0}'.format(j)
            

            x = list(range(i+2))
            y1 = list(data['d'+str(j)])[0:i+2]
            #'normalize' all values by dividing by the number of pixels in the first value, to create a % change
            num = normalizing[j-1]
            y = [i/num for i in y1]
     
            popt, _ = curve_fit(objective, x, y)

            # summarize the parameter values
            a, b= popt

            
            x_line = pylab.arange(min(x), max(x), 1)
        # calculate the output for the range
            y_line = objective(x_line, a, b)
            
        
            points[name_name] = name_name
            points[x_name] = x
            points[y_name]= y
            points[xcurve_name] = x_line
            points[ycurve_name] = y_line
            j = j+1
            gc.collect()
        
        #note to self: it may be tempting to move this outside the loop but DONT- must be defined in each loop
        csfont = {'fontname':'Times New Roman'}
        plt.style.use('seaborn')    
        fig=plt.figure(figsize=(90,90))  ## (90,90) (150,200)
        ax = plt.axes()
        ax.set_facecolor("white")
        ax.patch.set_edgecolor('black')  
        ax.patch.set_linewidth('4')
        plt.xlabel('Number of fatigue cycles', fontsize=220,**csfont)
        plt.ylabel('Normalized number of pixels\nin damage segmentation', fontsize=220,**csfont)
        plt.xticks(fontsize = 220,**csfont)
        plt.yticks(fontsize =220,**csfont)

        colors = list(mcolors.TABLEAU_COLORS) #make a list of colors so that each damage can be a different color
        font = font_manager.FontProperties(family='Times New Roman', size=150)
        k = 1
        for k in range(1,number):
            #loop over the damage dictionary, plotting all curves and points on the same graph
            name_name = 'damage {0}'.format(k)
            x_name = 'x {0}'.format(k)
            y_name = 'y {0}'.format(k)
            xcurve_name = 'xcurve {0}'.format(k)
            ycurve_name = 'ycurve {0}'.format(k)
            #get x and y
            plt.scatter(points[x_name],points[y_name],marker=".",s=6000,edgecolors="black",c=colors[k-1])
            #get lines

            plt.plot(points[xcurve_name], points[ycurve_name], '--', color=colors[k-1],linewidth=40)
            labels.append(name_name + ' point')
            labels.append(name_name + ' fit curve')
            gc.collect()
        
        
        plt.legend(labels= labels,prop=font)
        fig = plt.gcf()
        plt.tight_layout()
        plt.savefig(save_path+'/damagesfig{0}.png'.format(i), dpi=7)
        fig.clf()
        plt.close('all')
        del points, x, y, x_line, y_line
        i+= i
        gc.collect()
    gc.collect()

def plot_all_faster(file_path, save_path, frame_count, number_dam):
    #an attempt to make this faster, not actually used anywhere.
    #gets file of pixel count data, place to save, and folder of masks with same length as data.
    #plots points and linear regression for each damage on same figure, normalized to a percentage change
    #a new figure is made for each frame
    plt.ioff()
    data = read_csv(file_path)
    count = frame_count
    number = number_dam +1
    i = 0 #frame iterator
    normalizing = []
    for i in range(count-2): #loop over the number of frames
        j=1 #damage iterator
        
        points = {}
        labels = []
        
        for j in range(1,number): #loop over each damage
            #save the point values, as well as fit curve data in a dictionary, so all can be plotted on one plot.
            working_y = list(data['d'+str(j)])
            if i ==0:
                normalizing.append(working_y[0])
            name_name = 'damage {0}'.format(j)
            x_name = 'x {0}'.format(j)
            y_name = 'y {0}'.format(j)
            xcurve_name = 'xcurve {0}'.format(j)
            ycurve_name = 'ycurve {0}'.format(j)
            

            x = list(range(i+2))
            #'normalize' all values by dividing by the number of pixels in the first value, to create a % change
            num = normalizing[j-1] #use j-1 becuase there is no 'damage 0'
            y = [i/num for i in working_y[0:i+2]] #normalize all values

            popt, _ = curve_fit(objective, x, y)

            # summarize the parameter values
            a, b= popt
            x_line = pylab.arange(min(x), max(x), 1)
        # calculate the output for the range
            y_line = objective(x_line, a, b)

        
            points[name_name] = name_name
            points[x_name] = x
            points[y_name]= y
            points[xcurve_name] = x_line
            points[ycurve_name] = y_line
            j = j+1
            gc.collect()
        fig=plt.figure(figsize=(90,90))  ## (90,90) (150,200)

        ax = plt.axes()

        #stylize the plot!
        csfont = {'fontname':'Times New Roman'}
        plt.style.use('seaborn')    
        ax.set_facecolor("white")
        ax.patch.set_edgecolor('black')  
        ax.patch.set_linewidth('4')
        plt.xlabel('Number of fatigue cycles', fontsize=220,**csfont)
        plt.ylabel('Normalized number of pixels\nin damage segmentation', fontsize=220,**csfont)
        plt.xticks(fontsize = 220,**csfont)
        plt.yticks(fontsize =220,**csfont)
        
        colors = list(mcolors.TABLEAU_COLORS)
        font = font_manager.FontProperties(family='Times New Roman', size=150)
        k = 1
        for k in range(1,number):
            #loop over dictionary, plotting all curves and points on the same graph
            name_name = 'damage {0}'.format(k)
            x_name = 'x {0}'.format(k)
            y_name = 'y {0}'.format(k)
            xcurve_name = 'xcurve {0}'.format(k)
            ycurve_name = 'ycurve {0}'.format(k)
            #get x and y
            plt.scatter(points[x_name],points[y_name],marker=".",s=6000,edgecolors="black",c=colors[k-1])
            #get lines

            plt.plot(points[xcurve_name], points[ycurve_name], '--', color=colors[k-1],linewidth=40)
            labels.append(name_name + ' point')
            labels.append(name_name + ' fit curve')
            gc.collect()
        
        
        plt.legend(labels= labels,prop=font)
        fig = plt.gcf()
        plt.tight_layout()
        plt.savefig(save_path+'/damagesfig{0}.png'.format(i), dpi=7)
        fig.clf()
        plt.close('all')
        del points, x, y, x_line, y_line
        i+= i
        gc.collect()
    gc.collect()
    
def all_pixel_progression(file_path, save_path, folder_path):
    #takes in file of pixel counts, save path for resulting graphs, folder of images to count. 
    #graphs all pixels in the whole threshold mask, not currently used. 
    plt.ioff()
    data = read_csv(file_path)
    count = len(os.listdir(folder_path))
    i = 0 #frame iterator

    for i in range(count-2): #loop over the number of frames
       

        x = list(range(i+2))
        y1 = data[0:i+2]
            #'normalize' all values by dividing by the number of pixels in the first value, to create a % change
        num = data[1]
        y = [i/num for i in y1]
 
        popt, _ = curve_fit(objective, x, y)

        # summarize the parameter values
        a, b= popt

        
        x_line = pylab.arange(min(x), max(x), 1)
    # calculate the output for the range
        y_line = objective(x_line, a, b)

    
        fig=plt.figure(figsize=(90,90))  ## (90,90) (150,200)

        ax = plt.axes()

        csfont = {'fontname':'Times New Roman'}
        plt.style.use('seaborn')    
        ax.set_facecolor("white")
        ax.patch.set_edgecolor('black')  
        ax.patch.set_linewidth('4')
        plt.xlabel('Number of fatigue cycles', fontsize=220,**csfont)
        plt.ylabel('Normalized number of pixels\nin damage segmentation', fontsize=220,**csfont)
        plt.xticks(fontsize = 220,**csfont)
        plt.yticks(fontsize =220,**csfont)
        plt.scatter(x,y,marker=".",s=6000,edgecolors="black",c="black")
        plt.plot(x_line, y_line, '--',linewidth=40)
        font = font_manager.FontProperties(family='Times New Roman', size=150)
        plt.legend(prop=font)
        fig = plt.gcf()
        plt.tight_layout()
        plt.savefig(save_path+'/pixelsfig{0}.png'.format(i), dpi=7)
        fig.clf()
        plt.close('all')

        i+= i
        gc.collect()
    gc.collect()
    
def fix_graphs(folder_path):
    #takes in a folder of graphs, makes them smaller (400x400)
    #not currently used, instead changed dpi to be smaller.
    for file in os.listdir(folder_path):
        try:
            imgPath = folder_path+file
            img = Image.open(imgPath)

            img.thumbnail((400, 400))
            img.save(imgPath)
        except FileNotFoundError:
            print('Provided image path is not found')

def make_results_old(list_of_paths, save_path):
    #slow old version, reads in all file names before selecting the image
    #but a more flexible version that can account for different names or extentions, so keeping for now.
    
    # plt.ioff()
    # num_frames = count_frames(list_of_paths[5])
    # ext = ['png']
    # size = 7
    # plt.ioff()
    # for i in range(num_frames):
    #     j =1
    #     for impath in list_of_paths:
    #         imdir = impath
    #         files = []
    #         [files.extend(glob.glob(imdir + '*.' + e)) for e in ext]
    #         images = []
    #         files = sorted(files, key=natural_sort_key)
    #         for file in files:
    #             images.append(cv2.imread(file))
    #         #images = [cv2.imread(file) for file in files]
            
    #         img=images[i]
            

    #         fig = plt.figure(i)
    #         #subplot has 2 rows, 3 columns, and we are entering item number j
    #         fig.add_subplot(2, 3, j)
    #         #fig.tight_layout(pad=0.1)
    #         fig.subplots_adjust(wspace=0.05)
    #         fig.subplots_adjust(hspace=0)
    #         plt.imshow(img[:,:,::-1])
    #         plt.axis('off')
    #         #add title to each image, based on where in the loops we are
    #         if j==1:
    #             plt.title("Thermal Image", fontsize=size)
    #         elif j ==2:
    #             plt.title("Crop Relevant Area", fontsize=size)
    #         elif j == 3:
    #             plt.title("Binary Mask", fontsize=size)
    #         elif j ==4:
    #             plt.title("Damage Segmentation", fontsize=size)
    #         elif j ==5:
    #             plt.title("Damage Localization", fontsize=size)
    #         elif j ==6:
    #             plt.title("Damage Progression", fontsize=size)
    #         else:
    #             plt.title("title "+str(j), fontsize=size)
    #         j=j+1
            
    #     plt.savefig(save_path+'/{0}.png'.format(i), dpi=500)
    #     i+=1
    #     fig.clf()
    #     plt.close()
    #     gc.collect()

    # gc.collect()
    pass

def make_results(list_of_paths, save_path):
    #takes in a list of 6 paths, and a location to save
    #arranges the 6 images in a grid of subfigures, then saves the image
    plt.ioff() #important!! use this command to avoid out of memory error
    num_frames = count_frames(list_of_paths[5])-1 #get the number of frames in the localized images
    size = 10 #font size for the labels
   
    for i in range(num_frames): #for each frame...
        j =1 #counting variable for within each figure
        for impath in list_of_paths: #for each path in the list...
            imdir = impath
            fig = plt.figure(i)
            fig.add_subplot(2, 3, j) #two rows, three columns, adding item number j
            fig.subplots_adjust(wspace=0.1) #width between subplots
            fig.subplots_adjust(hspace=0.1) #height between subplots
            fig.tight_layout() #shrinks the borders
            plt.axis('off')
            if j==1: #if this is first path in the list, then it is the og image
                img=cv2.imread(imdir + 'img'+str(i)+'.png') #read in the image
                plt.title("Thermal Image", fontsize=size) #add a title for this image
            elif j ==2:
                img=cv2.imread(imdir + 'img'+str(i)+'.png')
                plt.title("Crop Relevant Area", fontsize=size)
            elif j == 3:
                img=cv2.imread(imdir + 'mask'+str(i)+'.png')
                plt.title("Binary Mask", fontsize=size)
            elif j ==4:
                img=cv2.imread(imdir + 'seg'+str(i)+'.png')
                plt.title("Damage Segmentation", fontsize=size)
            elif j ==5:
                img=cv2.imread(imdir + 'finalimg'+str(i)+'.png')
                plt.title("Damage Localization", fontsize=size)
            elif j ==6:
                #if there is a single damage, then it will be called damage1fig
                #if there are multiple, damagesfig. we handle both cases
                if os.path.exists(imdir + 'damage1fig'+str(i)+'.png'):
                    img=cv2.imread(imdir + 'damage1fig'+str(i)+'.png') 
                    plt.title("Damage Progression", fontsize=size)
                elif os.path.exists(imdir + 'damagesfig'+str(i)+'.png'):
                    img=cv2.imread(imdir + 'damagesfig'+str(i)+'.png')
                    plt.title("Damage Progression", fontsize=size)
                else:
                    #this will cause its own error if there arent graphed results
                    pass
            else:
                #it realyl should never come to this
                plt.title("title "+str(j), fontsize=size)
            
            plt.imshow(img[:,:,::-1]) #show the image in the figure
            j=j+1 #move on to the next subplot
            
        plt.savefig(save_path+'/{0}.png'.format(i), dpi=500) #save the image
        i+=1
        fig.clf()
        plt.close()

    gc.collect()
    
def get_vid_size(video_path):
    #returns the physical dimensions of a video, so it can be resized if needed.
    #im pretty sure this is in pixels
    vid = cv2.VideoCapture(video_path)
    height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    return width, height

def get_vid_scale(winwidth, winheight, vidwidth, vidheight):
    #tests to see if the video is too large for the window, scales it down if so.
    if int(vidwidth) > int(winwidth)-100 or int(vidheight) > int(winheight)-100:
        ##this assumes that height is the constraining factor here!!
        scale = ceil(vidheight /int(winheight))
        width = int(vidwidth //(scale+1))
        height = int(vidheight //(scale+1))
        return width, height
    else:
        return vidwidth, vidheight