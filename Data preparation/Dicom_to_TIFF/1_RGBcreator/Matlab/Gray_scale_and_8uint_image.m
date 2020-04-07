% How to convert a dicom to gray-scale and uint8 TIF file    _AP
% 1) Move the "seg" folder in the 2_8bits_Matlab folder
% 2) Remeber to change the variable "file_name" and check "number" if incorrect !!!!!!
% 3) Run the program

%  REmember to chage this!!!!
file_name = 'LFIC_MR_0000_20190000';          % file name     
%
numrows =256;
numcols = 256;

% Delete files
pathName_delete = 'Images_GrayS_8bits';                       
fileList_delete = dir(fullfile(pathName_delete, '*.tif'));   
for k = 1 : length(fileList_delete)
  baseFileName = fileList_delete(k).name;
  fullFileName = fullfile(pathName_delete, baseFileName);
  %fprintf(1, 'Now deleting %s\n', fullFileName);
  delete(fullFileName);
end

% Program
pathName = 'seg';                               % directory of reference for inputs
fileList = dir(fullfile(pathName, '*.dcm'));    % dicom list

pathName_output = 'Images_GrayS_8bits';         % directory of the outputs

for k = 1:numel(fileList)
  info = dicominfo(fullfile(pathName, fileList(k).name));
  files = 1;
  data(:,:,files) =  dicomread(info);
  info2 = mat2gray(data);
  info3 = im2uint8(info2); 
  info4 = imresize(info3,[numrows numcols]);
  %rgbImage = cat(3, info3, info3, info3);  % this if we want rgb image
  %I3 = flip(info3 ,1);    % this flip the image vertically (for orizontal put a 2)
  if length(fileList) == 29
      number = sprintf('%02d',30-k);  % use this for old datasets!!!!!                   AP
  elseif length(fileList) == 30
      number = sprintf('%02d',31-k);  % use this for old datasets!!!!!                   AP
  else
      number = sprintf('%02d',k);
  end
  
  outputFileName = fullfile(pathName_output, [file_name , '_', number, '_mask.tif']);
  
  imwrite(info4, outputFileName)
end