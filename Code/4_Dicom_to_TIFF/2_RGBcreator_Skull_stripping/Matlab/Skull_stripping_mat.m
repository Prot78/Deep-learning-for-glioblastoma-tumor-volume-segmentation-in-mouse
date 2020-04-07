% How to create a skull map from dicom to gray-scale and uint8 TIF file _AP
% 1) Move the "seg_skull_stripping" folder in the Matlab folder
% 2) Remember that the map is not resized. mantained the original size and orientation!
% 3) Run the program
% 4) Images will be left in 

%  REmember to chage this!!!!
file_name = 'Skull_stripping';          % output file name     
%
numrows =256;
numcols = 256;

% Delete files
pathName_delete = 'Skull_stripping_mask';                       
fileList_delete = dir(fullfile(pathName_delete, '*.tif'));   
for k = 1 : length(fileList_delete)
  baseFileName = fileList_delete(k).name;
  fullFileName = fullfile(pathName_delete, baseFileName);
  %fprintf(1, 'Now deleting %s\n', fullFileName);
  delete(fullFileName);
end

% Program
pathName = 'seg_skull_stripping';               % directory of reference for inputs
fileList = dir(fullfile(pathName, '*.dcm'));    % dicom list

pathName_output = 'Skull_stripping_mask';         % directory of the outputs

for k = 1:numel(fileList)
  info = dicominfo(fullfile(pathName, fileList(k).name));
  files = 1;
  data(:,:,files) =  dicomread(info);
  data_for_dicom = dicomread(info);
  info2 = mat2gray(data);
  info4 = im2uint8(info2); 
  %info4 = imresize(info3,[numrows numcols]);   % NO resize here!!
  
  if info4>0
      info4 = 1;
  end
  
  if length(fileList) == 29
      number = sprintf('%02d',30-k);  % use this for old datasets!!!!!                   AP
  elseif length(fileList) == 30
      number = sprintf('%02d',31-k);  % use this for old datasets!!!!!                   AP
  else
      number = sprintf('%02d',k);
  end
  
  outputFileName = fullfile(pathName_output, [file_name , '_', number, '.tif']);
  
  imwrite(info4, outputFileName)
end