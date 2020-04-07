###  INSTRUCTIONS:
# 1) Place the images tif in RGB folder
# 2) Change the file name
# 3) Run the program


import os
from remove_files import remove_files

#Insert the file name !!!
file_name           =  'LFIC_MR_0490_20190000'     # Output RGB Image File name


source_folder_part1 = r'/Users/andreaprotti/Desktop/Machine_learning/MRI_brain_segmentation/Dicom_to_tiff/2_RGBcreator_Skull_stripping/Python/'     #MAIN FOLDER
RGB_folder                = r'RGB/'               # Output RGB Image Folder name
RGB_folder_Transformation = r'RGB_Transformation/'
source_folder = source_folder_part1 + RGB_folder
output_folder = source_folder_part1 + RGB_folder_Transformation

remove_files(output_folder)

def rename_files():
    print('Files saved in: RGB_Transformation')

    i = 1
    for filename in sorted (os.listdir(source_folder)):
        src =  source_folder + filename

        if "mask" in filename:
            dst = output_folder + file_name  + '_{:02d}'.format(i) + '_mask' + '.tif'
        else:
            dst = output_folder + file_name  + '_{:02d}'.format(i) + '.tif'

        os.rename(src, dst)

        i += 1


rename_files()