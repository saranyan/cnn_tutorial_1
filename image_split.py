from __future__ import division
import Image
import math
import os
from collections import namedtuple

Location = namedtuple('Location','x y')
sliced_images = {}

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
            working_slice.save(os.path.join(outdir, "slice_" + out_name + "_" + str(count)+".png"))
            count += 1
            #saving to sliced_Images
            sliced_images[Location(row,col)] = working_slice
    print "Done..."

def stich_images(image_path, out_name, outdir, slice_height, slice_width,options={}):
    """stich images from sliced_images array"""
    if(len (sliced_images) == 0):
        raise Exception('sliced_images array is empty. Run the slice_images function first')
    img = Image.open(image_path)
    width, height =img.size
    blank_img = Image.new("RGB", (width, height), "black")
    left = 0
    upper = 0
    right = 0
    lower = 0
    rows = int(math.ceil(height/slice_height))
    cols = int(math.ceil(width/slice_width))
    for row in range(rows-1):
        upper = row * slice_height
        lower = (row+1) * slice_height
        for col in range(cols-1):
            left = col * slice_width
            right = (col+1) * slice_width
            bbox = (left, upper, right, lower)
            #fetch images from sliced_images dict
            if options["NO_WHITES"]:
                temp_extrema = sliced_images[Location(row,col)].getextrema()
                print "temp_extrema = ", temp_extrema
                if temp_extrema[0] != temp_extrema[1]:
                    blank_img.paste(sliced_images[Location(row,col)],bbox)
            else:
                blank_img.paste(sliced_images[Location(row,col)],bbox)
    blank_img.save(os.path.join(outdir,out_name),"PNG")

if __name__ == '__main__':
    slice_images("test_text_sample.png","test_text", os.getcwd(), 30,20)
    stich_images("test_text_sample.png","output.png",os.getcwd(), 30,20,{"NO_WHITES":True})
