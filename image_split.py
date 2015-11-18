from __future__ import division
import Image
import math
import os
from collections import namedtuple
import numpy as np

Location = namedtuple('Location','x y')
sliced_images = {}
sliced_non_white_char_images = []

def slice_images(image_path, out_name, outdir, slice_height, slice_width):
    """slice an image into parts slice_size tall"""
    img = Image.open(image_path).convert('L')
    width, height = img.size
    left = 0
    upper = 0
    right = 0
    lower = 0

    rows = int(math.ceil(height/slice_height))
    cols = int(math.ceil(width/slice_width))
    print "Generating slices..."
    #print "rows = ",rows," columns = ",cols
    count = 1
    for row in range(rows-1):
        upper = row * slice_height
        lower = (row+1) * slice_height
        for col in range(cols-1):
            left = col * slice_width
            right = (col+1) * slice_width
            #print "left = ", left, " upper = ",upper, " right = ", right, " lower = ",lower
            bbox = (left, upper, right, lower)
            working_slice = img.crop(bbox)
            #if we want to save the intermediate images...
            #working_slice.save(os.path.join(outdir, "slice_" + out_name + "_" + str(count)+".png"))
            count += 1
            #saving to sliced_Images
            sliced_images[Location(row,col)] = working_slice
    print "Done..."

def prune_sliced_white_images(out_name, outdir,imgs,pixel_height, pixel_width):
    """just the characters now, no white spaces"""
    print "pruning blank images from sliced_images array..."
    if(len (sliced_images) == 0):
        print 'no sliced image array found'
        return
    img = Image.new("RGB", (len(sliced_non_white_char_images)*pixel_width,pixel_height))
    for index, item in enumerate(sliced_non_white_char_images):
        #left, upper = index*pixel_width, 0 |||| right,lower =  (index+1)*pixel_width, pixel_height
        img.paste(item,(index*pixel_width, 0, (index+1)*pixel_width, pixel_height))
    img.save(os.path.join(outdir,out_name),"PNG")

def blank_row(row,total_cols):
    """returns true if the entire row is blank"""
    for col in range(total_cols-1):
        temp_extrema = sliced_images[Location(row,col)].getextrema()
        if(temp_extrema[0] != temp_extrema[1]):
            return False
    return True



def stich_images(image_path, out_name, outdir, slice_height, slice_width,options={}):
    """stich images from sliced_images array"""
    print "stiching images from sliced_images array..."
    if(len (sliced_images) == 0):
        print 'sliced_images array is empty. Run the slice_images function first'
        return
    img = Image.open(image_path)
    width, height =img.size
    try:
        blank_img = Image.new("RGB", (width, height), options["IMAGE_COLOR"])
    except KeyError:
        blank_img = Image.new("RGB", (width, height), None)
    left = 0
    upper = 0
    right = 0
    lower = 0
    rows = int(math.ceil(height/slice_height))
    cols = int(math.ceil(width/slice_width))
    collapse_row_flag = 0 #we will keep a separate counter for row if 0s need to be collapsed
    for row in range(rows-1):
        # upper = row * slice_height
        # lower = (row+1) * slice_height
        #row collapse
        if options["COLLAPSE_ROWS"]:
            if(blank_row(row, cols)):
                #print "skipping row...", row
                continue
            else:
                collapse_row_flag += 1
        else:
            collapse_row_flag = row

        upper = collapse_row_flag * slice_height
        lower = (collapse_row_flag+1) * slice_height
        for col in range(cols-1):
            left = col * slice_width
            right = (col+1) * slice_width
            bbox = (left, upper, right, lower)
            #fetch images from sliced_images dict
            temp_extrema = sliced_images[Location(row,col)].getextrema()
            #print "temp_extrema = ", temp_extrema
            if temp_extrema[0] != temp_extrema[1]:
                blank_img.paste(sliced_images[Location(row,col)],bbox)
                sliced_non_white_char_images.append(sliced_images[Location(row,col)])


    blank_img.save(os.path.join(outdir,out_name),"PNG")

if __name__ == '__main__':
    slice_images("test_text_sample.png","test_text", os.getcwd(), 5,5)
    stich_images("test_text_sample.png","output.png",os.getcwd(), 5,5,{"COLLAPSE_ROWS":True,"IMAGE_COLOR":"white"})
    print "Non white slices = ", len(sliced_non_white_char_images), " out of total slices = ",len(sliced_images)
    prune_sliced_white_images("output_row.png",os.getcwd(),sliced_non_white_char_images, 5,5)
