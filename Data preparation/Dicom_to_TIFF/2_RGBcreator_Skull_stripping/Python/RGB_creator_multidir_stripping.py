# Creating RGB images (optional) + removing previous images from folders + inverting (optional) + rotate (optional)
# Remember to change the 4 options just below!!

# Step 1 place the folder with dicom files in the main folder ('1_RGBcreator_inverse_rotate')
# step 2, select the options
# Step 3, run the program from terminal

# Special cases:
# If you have the RGB images already, place the images files in the 'RGB_and_rotation' folder. In the code below, select 'RGB_constructor' as 'NO' and select the other options

# Remember 1, if RGB_constructor is 'NO', place the images in the folder 'RGB'
# Remember 2, if you need to rotate only (rotate only 'YES'), place the images in the folder 'RGB_and_rotation'
# Remember 3, if rename_and_invert is 'YES' the images will always show in the 'RGB_invert_and_rotation' folder

# THIS program need to be run from the TERMINAL!!!!!    (command:  python RGB_creatorv2.py)

## NAME the files as: LFIC_MR_0492_20190000

import png, os, pydicom, shutil
from PIL import Image, ImageOps
from resizeimage import resizeimage
import cv2
import numpy as np

import shutil


#INSERT the directories !!!
source_folder_main = r'/Users/andreaprotti/Desktop/Machine_learning/MRI_brain_segmentation/Dicom_to_tiff/2_RGBcreator_Skull_stripping/Python/'     #MAIN FOLDER
source_folder_fordata = r'/Users/andreaprotti/Desktop/Machine_learning/MRI_brain_segmentation/Dicom_to_tiff/2_RGBcreator_Skull_stripping/Python/data_dir/'     #MAIN FOLDER

### OPTIONS  Insert these  !!!

rename_and_invert   =  'YES'      #choose between "YES" and "NO" to have images inverted  !!!!!!    if rename_and_invert is 'YES' the images will always show in the 'RGB_invert_and_rotation' folder
   #ROTATION OPTION
up_down_rotation    =  'YES'       #choose between "YES" and "NO" to have images rotated  !!!!!!      if you need to retate only (rotate only 'YES'), place the images in the folder 'RGB'
left_right_rotation =  'YES'       #choose between "YES" and "NO" to have images rotated  !!!!!!      if you need to retate only (rotate only 'YES'), place the images in the folder 'RGB'
rotate              =  'no'       #this rotate clockwise of 180deg (not very useful) choose between "YES" and "NO" to have images rotated  !!!!!!      if you need to retate only (rotate only 'YES'), place the images in the folder 'RGB'
degrees = (20)     #degrees of rotation use: "(-angle)" for negative deg clockwise; use "(deg)" for positive deg anti-clockwise
###
#
#
#
#
#
### PROGRAM STARTING ......
RGB_folder                = r'RGB/'
output_folder             = r'Trans_folder/'
RGB_folder_Transformation = r'RGB_Transformation/'
Skull_stripping_mask      = r'Skull_stripping_mask/'

folder  = source_folder_main + RGB_folder
folder1 = source_folder_main + output_folder
folder2 = source_folder_main + RGB_folder_Transformation
folder3 = source_folder_main + Skull_stripping_mask

os.mkdir(source_folder_main + 'Trans_folder')
os.mkdir(source_folder_main + 'RGB')
os.mkdir(source_folder_main + 'RGB_Transformation')
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
    count_tif = 0
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

            # Skull_stripping
            count_tif += 1
            folder4 = folder3 + file_name
            im = Image.open(os.path.join(folder4, 'Skull_stripping_{:02d}.tif'.format(count_tif)))
            imarray = np.array(im)
            imarray[imarray > 1] = 1

            image_2d_scaled = image_2d_scaled * imarray

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
    lenght_file = len(os.listdir(folder))   #sorce folder = "folder"

    #the following inverse image order and rename the files in the correct way
    for filename in sorted (os.listdir(folder)):
        src =  folder + filename

        if "mask" in filename:
            dst = folder2 + file_name + '_{:02d}'.format(lenght_file - i) + '_mask' + '.tif'
        else:
            dst = folder2 + file_name + '_{:02d}'.format(lenght_file - i) + '.tif'

        if i>=0 :
            os.rename(src, dst)
        i += 1


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
                print('Option chosen:ONLY DICOM Transformation')

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
        dicom2png(source_folder, output_folder, file_name)

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