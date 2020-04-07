# ANDREA PROTTI python program
#
# Editing TIFF images with options to invert and rotate
#
# step 1, select the options
# Step 2, run the program  (If run from terminal (command:  python IMAGE_editing_multidir.py)

## Image folder and image files have the same name
### NAME the folder where the files are stored as: LFIC_MR_0001_20190101

import png, os, pydicom, shutil
from PIL import Image, ImageOps
from resizeimage import resizeimage
import cv2
import numpy as np

import shutil


#####################################
### OPTIONS  Insert these  !!!

rename_and_invert   =  'no'      #choose between "YES" and "NO" to have images inverted  !!!!!!
   #ROTATION OPTION
up_down_rotation    =  'no'       #choose between "YES" and "NO" to have images rotated  !!!!!!
left_right_rotation =  'no'       #choose between "YES" and "NO" to have images rotated  !!!!!!
rotate              =  'YES'       #this rotate clockwise of 180deg (not very useful) choose between "YES" and "NO" to have images rotated  !!!!!!
degrees = (20)     #degrees of rotation use: "(-angle)" for negative deg clockwise; use "(deg)" for positive deg anti-clockwise
#####################################
#
#
#
#
#
### PROGRAM STARTING ......
source_folder_fordata     = r'data_dir/'     #MAIN FOLDER
RGB_folder                = r'RGB/'
output_folder             = r'Trans_folder/'
RGB_folder_Transformation = r'RGB_Transformation/'

folder  = RGB_folder
folder1 = output_folder
folder2 = RGB_folder_Transformation

os.mkdir('Trans_folder')
os.mkdir('RGB')
os.mkdir('RGB_Transformation')
#
#
#
### DEFINITIONS
def remove_files_Ds(source_folder):
    for (dirpath, dirnames, filenames) in os.walk(source_folder):
        if os.path.isfile(source_folder + '/.DS_Store'):
            os.unlink(source_folder + '/.DS_Store')  # AP had to include this because the .Ds_Store was troubling me '''
        #if os.path.isfile(source_folder + '/vol.txt'):
         #   os.unlink(source_folder + '/vol.txt')


def dicom2png(source_folder, output_folder, file_name):
    list_of_files = sorted (os.listdir(source_folder))
    count = 0
    for file in list_of_files:
        try:
            ds = pydicom.dcmread(os.path.join(source_folder,file))
            shape = ds.pixel_array.shape

            # Convert to float to avoid overflow or underflow losses.
            image_2d = ds.pixel_array.astype(float)

            # Rescaling grey scale between 0-255
            image_2d_scaled = (np.maximum(image_2d,0) / image_2d.max()) * 255.0

            # Convert to uint
            image_2d_scaled = np.uint8(image_2d_scaled)

            # Write the PNG file
            with open(os.path.join(output_folder, file) + '.tif', 'wb') as png_file:
                w = png.Writer(shape[1], shape[0], greyscale=True)
                w.write(png_file, image_2d_scaled)                    #this write a tif in greyscale 8bits!

            # Grayscale and resize image containing red values
            r = cv2.imread(os.path.join(output_folder, file) + '.tif', 0)
            r = cv2.resize(r, (256,256))

            # Grayscale and resize image containing Blue values
            b = cv2.imread(os.path.join(output_folder, file) + '.tif', 0)
            b = cv2.resize(b, (256, 256))

            # Grayscale and resize image containing Green values
            g = cv2.imread(os.path.join(output_folder, file) + '.tif', 0)
            g = cv2.resize(g, (256, 256))

            # creating a rgb image using grayscales
            img = cv2.merge((r, b, g))

            # This below save the file as NUMBERED_RGB.tiff
            count += 1

            cv2.imwrite(folder + file_name + '_{:02d}.tif'.format(count), img)     #the RGB images are stored in "folder"

        except:
            print('Could not convert: ', file)


def inverseorder(file_name):
    i = 0
    i_mask = 0

    # Use this if you have either mask or RGB images
    lenght_file = len(os.listdir(folder))  # sorce folder = "folder"

    ## Use this if you have both mask and RBG images
    #lenght_file = (len(os.listdir(folder)))/2  # sorce folder = "folder"
    #lenght_file = int(lenght_file)
    ##

    # the following inverse image order and rename the files in the correct way
    for filename in sorted(os.listdir(folder)):
        src = folder + filename

        if "mask" in filename:
            dst = folder2 + file_name + '_{:02d}'.format(lenght_file - i_mask) + '_mask' + '.tif'
            i_mask += 1
        else:
            dst = folder2 + file_name + '_{:02d}'.format(lenght_file - i) + '.tif'
            i += 1

        if i>=0 :
            os.rename(src, dst)
        #i += 1


def up_down_rotation_image():
    for (dirpath, dirnames, filenames) in os.walk(folder2):
        for filename in sorted(filenames):
            picture = Image.open(dirpath+'/'+filename)
            ImageOps.flip(picture).save(folder2 + filename)

def left_right_rotation_image():
    for (dirpath, dirnames, filenames) in os.walk(folder2):
        for filename in sorted(filenames):
            picture = Image.open(dirpath+'/'+filename)
            ImageOps.mirror(picture).save(folder2 + filename)

def up_down_left_right_rotation_image():
    for (dirpath, dirnames, filenames) in os.walk(folder2):
        for filename in sorted(filenames):
            picture = Image.open(dirpath+'/'+filename)
            image_flip = ImageOps.flip(picture)
            ImageOps.mirror(image_flip).save(folder2 + filename)

def rotate_image():
    for (dirpath, dirnames, filenames) in os.walk(folder2):
        for filename in sorted(filenames):
            picture = Image.open(dirpath+'/'+filename)
            picture.rotate(degrees).save(folder2 + filename)
#
#
#
#
#PRINTING the option chosen on screen
# NO, NO, NO, NO
if rename_and_invert is not 'YES':
    if up_down_rotation is not 'YES':
        if left_right_rotation is not 'YES':
            if rotate is not 'YES':
                print('Option chosen: No Transformation')

# YES, NO, NO, NO
if rename_and_invert is 'YES':
    if up_down_rotation is not 'YES':
        if left_right_rotation is not 'YES':
            if rotate is not 'YES':
                print('Option chosen: YES, NO, NO, NO')

# YES, YES, NO, NO
if rename_and_invert is 'YES':
    if up_down_rotation is 'YES':
        if left_right_rotation is not 'YES':
            if rotate is not 'YES':
                print('Option chosen: YES, YES, NO, NO')

# YES, YES, YES, NO
if rename_and_invert is 'YES':
    if up_down_rotation is 'YES':
        if left_right_rotation is 'YES':
            if rotate is not 'YES':
                print('Option chosen: YES, YES, YES, NO')

# If up_down_rotation is 'YES'
# YES, YES, YES, YES
if rename_and_invert is 'YES':
    if up_down_rotation is 'YES':
        if left_right_rotation is 'YES':
            if rotate is 'YES':
                print('Option chosen: YES, YES, YES, YES')

# NO, YES, NO, NO
if rename_and_invert is not 'YES':
    if up_down_rotation is 'YES':
        if left_right_rotation is not 'YES':
            if rotate is not 'YES':
                print('Option chosen: NO, YES, NO, NO')

# If left_right_rotation is 'YES'
# YES, NO, YES, NO
if rename_and_invert is 'YES':
    if up_down_rotation is not 'YES':
        if left_right_rotation is 'YES':
            if rotate is not 'YES':
                print('Option chosen: YES, NO, YES, NO')

# NO, NO, YES, NO
if rename_and_invert is not 'YES':
    if up_down_rotation is not 'YES':
        if left_right_rotation is 'YES':
            if rotate is not 'YES':
                print('Option chosen: NO, NO, YES, NO')

# If up_down_left_right_rotation is 'YES'
# NO, YES, YES, NO
if rename_and_invert is not 'YES':
    if up_down_rotation is 'YES':
        if left_right_rotation is 'YES':
            if rotate is not 'YES':
                print('Option chosen: NO, YES, YES, NO')

# If rotate 180deg clockwise is 'YES'
# YES, NO, NO, YES
if rename_and_invert is 'YES':
    if up_down_rotation is not 'YES':
        if left_right_rotation is not 'YES':
            if rotate is 'YES':
                print('Option chosen: YES, NO, NO, YES')

# NO, NO, NO, YES
if rename_and_invert is not 'YES':
    if up_down_rotation is not 'YES':
        if left_right_rotation is not 'YES':
            if rotate is 'YES':
                print('Option chosen: NO, NO, NO, YES')

# NO, YES, YES, YES
if rename_and_invert is not 'YES':
    if up_down_rotation is 'YES':
        if left_right_rotation is 'YES':
            if rotate is 'YES':
                print('Option chosen: NO, YES, YES, YES')

# YES, NO, YES, YES
if rename_and_invert is 'YES':
    if up_down_rotation is not 'YES':
        if left_right_rotation is 'YES':
            if rotate is 'YES':
                print('Option chosen: YES, NO, YES, YES')

# YES, YES, NO, YES
if rename_and_invert is 'YES':
    if up_down_rotation is 'YES':
        if left_right_rotation is not 'YES':
            if rotate is 'YES':
                print('Option chosen: YES, NO, YES, YES')

# NO, NO, YES, YES
if rename_and_invert is not 'YES':
    if up_down_rotation is not 'YES':
        if left_right_rotation is 'YES':
            if rotate is 'YES':
                print('Option chosen: NO, NO, YES, YES')

# NO, YES, NO, YES
if rename_and_invert is not 'YES':
    if up_down_rotation is 'YES':
        if left_right_rotation is not 'YES':
            if rotate is 'YES':
                print('Option chosen: NO, YES, NO, YES')
#END PRINTING option chosen
#
#
#
#
##Program to remove possible data folder
for (dirpath, dirnames, filenames) in sorted (os.walk(source_folder_fordata)):
    for dirname in sorted (dirnames):
        file_name = dirname
        source_folder = source_folder_fordata + '%s' % dirname    #THIS is the source folder or dicom folder

        #unlink (remove) image folder if already existing
        source_folder_forunlink = source_folder + '/' + file_name
        for (dirpath, dirnames, filenames) in os.walk(source_folder):
            if os.path.isdir(source_folder_forunlink):
                shutil.rmtree(source_folder_forunlink)
##END
#
#
#
#
#PROGRAM Options
for (dirpath, dirnames, filenames) in sorted (os.walk(source_folder_fordata)):
    for dirname in sorted (dirnames):
        file_name = dirname
        source_folder = source_folder_fordata + '%s' % dirname    #THIS is the source folder or dicom folder
        remove_files_Ds(source_folder)

        #Move images to folder
        files_tif = os.listdir(source_folder)
        files_tif.sort()
        for f_tif in files_tif:
            src_tif = source_folder + '/' + f_tif
            dst_tif = folder + '/' + f_tif
            #shutil.move(src_tif, dst_tif)
            shutil.copy(src_tif, dst_tif)

        if rename_and_invert is 'YES':
            inverseorder(file_name)
        else:
            files = os.listdir(folder)
            files.sort()
            for f in files:
                src = folder + f
                dst = folder2 + f
                shutil.move(src, dst)

        if up_down_rotation is 'YES':
            up_down_rotation_image()

        if left_right_rotation is 'YES':
            left_right_rotation_image()

        if rotate is 'YES':
            rotate_image()

        # PRINT the directory where the data have been saved
        print('Files saved in: data_dir/' + file_name + '/' + file_name )

        # OPTION to create the image directory
        os.mkdir(source_folder_fordata + '%s/' % dirname + '%s' % dirname)    #Create image folders AP

        #MOVE the images from folder2 to the appropriate image directory
        source = folder2
        destination = source_folder_fordata + '%s/' % dirname + '%s/' % dirname
        files = os.listdir(source)
        files.sort()
        for f in files:
            src = source + f
            dst = destination + f
            shutil.move(src, dst)
#END PROGRAM Options

shutil.rmtree(folder)
shutil.rmtree(folder1)
shutil.rmtree(folder2)

### END