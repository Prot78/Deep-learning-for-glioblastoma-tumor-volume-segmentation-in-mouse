# Deep learning for glioblastoma tumor volume segmentation in mouse

__0.94 DSC (94% accuracy)________________Predicted segmentation_________________Manual segmentation        

![hello](images/630_FLAIR.gif).   ![hello](images/630_FLAIR_pred.png).     ![hello](images/630_FLAIR_true.png).


## Method
### Mouse glioblastoma model
All procedures and imaging protocols for this study were approved and performed in accordance with Dana-Farber Cancer Institute's Institutional Animal Care and Use Committee (IACUC). For the intercranial injection of the GL261-luc2 cells, 6 to 10-week old female B6(Cg)-Tyrc-2J/J mice (The Jackson Laboratory, Bar Harbor, ME).
### In-vivo MRI imaging data collection  
MRI in vivo studies were performed on a 7T/30 cm USR horizontal bore Superconducting Magnet System 300.3 MHz (Bruker BioSpin MRI, Ettlingen, Germany BioSpec). 
Three MRI sequences were engaged in-vivo on GBM mice: Fluid attenuated inversion recovery (FLAIR), Fast-Spin-Echo T1 and T2 weighted
FLAIR MRI datasets and related segmentation masks have been made public and available in kaggle (https://www.kaggle.com/prot78/deep-learning-gbm-tumor-volume-estimation-in-mouse).
### Data preparation
The dicom files produced by our Bruker MRI scanner had to be converted in 256x256 RGB images. 
1.	“Image segmentation”. The dicom MRI files were upload into our in-house software (named ClinicalVolumes). The software performs image segmentation either in a semi-automatic or manual manner, but for this particular work the use a full manual tumor area segmentation was preferred. Tumor segmentation masks (“tumor mask”) were saved in dicom format and the calculated tumor volumes collected in a text file (named “vol.txt”) together with additional volume segmented information.
For the FLAIR dataset, a manual segmentation was also applied to generate a “brain mask” for skull-stripping segmentation purposes and saved in dicom format. A text file (named “vol_brain.txt”) was generated for each mouse containing brain volume information.   
2.	“8 bits masks”. A MatLab (R2018a (9.4.0) 64-bits) program was used to convert the masks, both for tumor and brain, created in the previous segmentation step, from a dicom format to a 8bits Tiff image 256x256 matrix. 
3.	“RGB images”. A Python 3.7 program was used to generate RGB Tiff 256x256 images from the MRI dicom format datasets.
### Automatic segmentation
A detailed description of the automatic segmentation algorithm is given in the work of Buda et al. [Buda M, Saha A, Mazurowski MA. Association of genomic subtypes of lower-grade gliomas with shape features automatically extracted by a deep learning algorithm. Comput Biol Med. 2019;109:218-25]. 
To initialize the training phase, MRI images and related masks fed the CNN U-net model. A minimum of 16 volumes were used. The data were selected homogeneously throughout the tumor volume range and then divided in two groups: small tumor (<15 mm3) and middlesize_to_large tumor (> 15 mm3). In order to achieve reliable and robust “weights” few factors results crucial during the training phase:
•	Good image quality;
•	Good contrast between tumor and healthy tissues;
•	Precise differentiation between tumor volumes groups (small tumor to large tumor);
•	Similar number of slices between datasets;
•	Images must be vertically aligned or tilted within a maximum of 20 degrees angle, any large angular deformation can compromise the training and therefore images must be rotate toward the vertical axis during data preparation.  
Once completed the data training, the calculated “weights” were used in the “inference” part of the code.
### Data analysis
The deep learning program calculated the Dice coefficient (DSC) of each animal highlighting the level of similarity and accuracy between manual and automatic segmentation. In addition to the DSC analysis, the segmented areas were further analyzed by comparing the volumes obtained by each animal (“volumes” analysis) and by slice (“slice by slice” area analysis). “Volumes” and “slice by slice” analysis undergo a two-sided P value, test of correlation (Pearson’s coefficient) and agreement (Bland-Altman). P value less than .05 was considered statistically different.

![hello](images/Fig_2.jpg).


## Results
