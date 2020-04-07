import argparse
import os

import numpy as np
import torch
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from medpy.filter.binary import largest_connected_component
from skimage.io import imsave
from torch.utils.data import DataLoader
from tqdm import tqdm

from dataset import BrainSegmentationDataset as Dataset
from unet import UNet
from utils import dsc, gray2rgb, outline


def main(args):
    makedirs(args)
    device = torch.device("cpu" if not torch.cuda.is_available() else args.device)

    loader = data_loader(args)

    FOV_x = 20  # AP FOV_x mm
    FOV_y = 20  # AP FOV_y mm
    FOV_z = 1  # AP Thickness mm
    resolution_x = FOV_x / 256
    resolution_y = FOV_y / 256

    conversion_factor = 3.5   #Conversion factor for cropping. Typically 3.5
    print('Conversion factor for automatic seg = %.2f' % conversion_factor)

    with torch.set_grad_enabled(False):
        unet = UNet(in_channels=Dataset.in_channels, out_channels=Dataset.out_channels)
        state_dict = torch.load(args.weights, map_location=device)
        unet.load_state_dict(state_dict)
        unet.eval()
        unet.to(device)

        input_list = []
        pred_list = []
        true_list = []

        for i, data in tqdm(enumerate(loader)):
            x, y_true = data
            x, y_true = x.to(device), y_true.to(device)

            y_pred = unet(x)
            y_pred_np = y_pred.detach().cpu().numpy()
            pred_list.extend([y_pred_np[s] for s in range(y_pred_np.shape[0])])

            y_true_np = y_true.detach().cpu().numpy()
            true_list.extend([y_true_np[s] for s in range(y_true_np.shape[0])])

            x_np = x.detach().cpu().numpy()
            input_list.extend([x_np[s] for s in range(x_np.shape[0])])

    volumes = postprocess_per_volume(
        input_list,
        pred_list,
        true_list,
        loader.dataset.patient_slice_index,
        loader.dataset.patients,
    )

    dsc_dist = dsc_distribution(volumes, conversion_factor, resolution_x, resolution_y, FOV_z)

    dsc_dist_plot = plot_dsc(dsc_dist)
    imsave(args.figure, dsc_dist_plot)

    filepath_pixels_predicted_total = "{}.txt".format("predictions/Predicted-volume-singleslice_total")  # AP
    with open(filepath_pixels_predicted_total, 'w') as fff:  # AP
        fff.write('FOV = %s x %s x %s mm3 \n' % (FOV_x, FOV_y, FOV_z))
        fff.write('Matrix size = 256x256 \n\n')
        fff.write('Predicted volume per single slice for all cases (mm3): \n')

        filepath_pixels_true_total = "{}.txt".format("predictions/True-volume-singleslice_total")  # AP
        with open(filepath_pixels_true_total, 'w') as ffff:  # AP
            ffff.write('FOV = %s x %s x %s mm3 \n' % (FOV_x, FOV_y, FOV_z))
            ffff.write('Matrix size = 256x256 \n\n')
            ffff.write('True (manual seg) volume per single slice for all cases (mm3): \n')

            for p in volumes:
                x = volumes[p][0]
                y_pred = volumes[p][1]
                #y_pred_round = np.round(y_pred).astype(int)
                #print(p, 'y_pred is = ', y_pred_round)
                y_true = volumes[p][2]

                y_pred_pixels_total = 0                                               #AP
                y_true_pixels_total = 0
                y_pred_pixels_singleslice = 0                                         #AP
                volume_predicted_value_singleslice = 0                                #AP

                y_true_pixels_singleslice = 0                                         #AP
                volume_true_value_singleslice = 0                                     #AP

                for s in range(x.shape[0]):

                    # Volume true per slice
                    y_true_array = y_true[s, 0] * 1  # AP
                    y_true_pixels_total = np.count_nonzero(y_true_array == 1) + y_true_pixels_total  # AP

                # Reading volume total from ClinicalVolumes manual segmentation
                filepath_vol = os.path.join(args.images, p, 'vol.txt')  # "images" is the argument corresponding to ./kaggle_3m  #AP
                read_volume = open(filepath_vol, 'r')  # AP
                lines = read_volume.readlines()  # AP
                volume_true_value_fromline = lines[12]  # AP
                volume_true_value_ClinicalVolumes = float(volume_true_value_fromline)  # AP
                # volume_true_value_ClinicalVolumes = volume_true_value_ClinicalVolumes             #AP (removed 5: the term to adjust to the contorn differences in T2)

                volume_true_value_before_corection = resolution_x * resolution_y * FOV_z * y_true_pixels_total  # AP  volume calc
                # Calculating the true conversion factor
                true_conversion_factor = volume_true_value_before_corection / volume_true_value_ClinicalVolumes  # AP mask volume is incorrectly calculated from the sofware, it needs an adjustment
                print('Conversion factor for manual seg = %.2f' % true_conversion_factor)
                # Calculating the true volume
                volume_true_value = volume_true_value_before_corection / true_conversion_factor
                y_true_pixels_total = y_true_pixels_total / true_conversion_factor

                # Creating predicted and True volumes
                filename_pixels_predicted_true = "{}-{}.txt".format(p, "Predicted_and-True-volume-singleslice")  # AP
                filepath_pixels_predicted_true = os.path.join(args.predictions, filename_pixels_predicted_true)  # AP
                with open(filepath_pixels_predicted_true, 'w') as f:  # AP

                    # Creating True single slice volumes
                    f.write('True (manual seg) volume per single slice (mm3): \n')
                    for s in range(x.shape[0]):
                        y_true_array = y_true[s, 0] * 1  # AP
                        y_true_pixels_singleslice = np.count_nonzero(y_true_array == 1) + y_true_pixels_singleslice  # AP
                        volume_true_value_singleslice = resolution_x * resolution_y * FOV_z * y_true_pixels_singleslice / true_conversion_factor  # /conversion_factor #* 1.5

                        f.write('%.2f' % volume_true_value_singleslice)
                        f.write('\n')  # AP
                        y_true_pixels_singleslice = 0

                        ffff.write('%.2f \n' % volume_true_value_singleslice)  # AP
                    # END Creating True single slice volumes

                    # Creating predicted volumes
                    f.write('\nPredicted volume per slice slice (mm3): \n')
                    for s in range(x.shape[0]):
                        # Images creation
                        image = gray2rgb(x[s, 1])  # channel 1 is for FLAIR

                        image = outline(image, y_pred[s, 0], color=[255, 0, 0])  # AP y_pred RED is the predicted volume!
                        image = outline(image, y_true[s, 0], color=[0, 255, 0])  # AP y_true GREEN is for true volumes!

                        filename = "{}-{}.png".format(p, str(s).zfill(2))
                        filepath = os.path.join(args.predictions, filename)
                        imsave(filepath, image)
                        # End images creation

                        # Volume predicted per slice
                        y_pred_array = y_pred[s, 0] * 1    #AP
                        y_pred_pixels_total = np.count_nonzero(y_pred_array == 1) + y_pred_pixels_total   #AP
                        y_pred_pixels_singleslice = np.count_nonzero(y_pred_array == 1) + y_pred_pixels_singleslice  # AP
                        volume_predicted_value_singleslice = resolution_x * resolution_y * FOV_z * y_pred_pixels_singleslice/conversion_factor  # AP  predicted volume per slice
                        f.write('%.2f' % volume_predicted_value_singleslice)
                        f.write('\n')  # AP
                        y_pred_pixels_singleslice = 0
                        # End volume predicted per slice

                        fff.write('%.2f \n' % volume_predicted_value_singleslice)
                    # END Creating predicted volumes


                # Predicted mask pixels total
                y_pred_pixels_total = y_pred_pixels_total / conversion_factor  # AP 3.5 is the conversion factor for skull stripping image zooming
                # Calculating the predicted volume
                volume_predicted_value = resolution_x * resolution_y * FOV_z * y_pred_pixels_total  # AP  volume calc

                # Calculating the difference in volumes
                volume_difference = volume_true_value - volume_predicted_value    #AP
                if (volume_true_value == 0):                                      #AP
                    volume_difference_percentage = 0                              #AP
                else:
                    volume_difference_percentage = abs(100 - (volume_predicted_value*100/volume_true_value))  #AP

                filename_pixels = "{}-{}.txt".format(p, "Volume")                  #AP
                filepath_pixels = os.path.join(args.predictions, filename_pixels)  #AP

                with open(filepath_pixels, 'w') as f:                              #AP
                    f.write('FOV = %s x %s x %s mm3 \n' % (FOV_x, FOV_y, FOV_z))
                    f.write('Matrix size = 256x256 \n\n')
                    f.write('Number of pixels true      = %d \n' % y_true_pixels_total)

                    f.write('Number of pixels predicted = %d \n\n' % y_pred_pixels_total)

                    f.write('Volume from manual segmentation (mm3)    = %.2f \n' % volume_true_value)

                    f.write('Volume from predicted segmentation (mm3) = %.2f \n\n' % volume_predicted_value)

                    f.write('Volume difference (mm3) = %.2f \n' % volume_difference)

                    f.write('Volume difference percentage (%%) = %.2f \n' % volume_difference_percentage)

                with open(filepath_pixels) as f1:
                    with open(filepath_pixels_predicted_true) as f2:
                        filename_pixels_volume_summary = "{}-{}.txt".format(p, "Volume_summary")  # AP
                        filepath_pixels_volume_summary = os.path.join(args.predictions, filename_pixels_volume_summary)  # AP
                        with open(filepath_pixels_volume_summary, "w") as f3:
                            for line in f1:
                                f3.write(line)
                            f3.write('\n\n')
                            for line in f2:
                                f3.write(line)

                os.remove(filepath_pixels)
                os.remove(filepath_pixels_predicted_true)


def data_loader(args):
    dataset = Dataset(
        images_dir=args.images,
        subset="validation",
        image_size=args.image_size,
        random_sampling=False,
    )
    loader = DataLoader(
        dataset, batch_size=args.batch_size, drop_last=False, num_workers=1
    )
    return loader


def postprocess_per_volume(
    input_list, pred_list, true_list, patient_slice_index, patients
):
    volumes = {}
    num_slices = np.bincount([p[0] for p in patient_slice_index])
    index = 0
    for p in range(len(num_slices)):
        volume_in = np.array(input_list[index : index + num_slices[p]])
        volume_pred = np.round(
            np.array(pred_list[index : index + num_slices[p]])
        ).astype(int)
        volume_pred = largest_connected_component(volume_pred)
        volume_true = np.array(true_list[index : index + num_slices[p]])
        volumes[patients[p]] = (volume_in, volume_pred, volume_true)
        index += num_slices[p]
    return volumes

# Modified AP
def dsc_distribution(volumes, conversion_factor, resolution_x, resolution_y, FOV_z):     #Note! The definition dsc from utils is not used anymore!!!!  AP
    dsc_dict = {}
    for p in volumes:
        x = volumes[p][0]
        y_pred = volumes[p][1]
        y_true = volumes[p][2]
        y_true_pixels_total = 0
        y_true_pixels_singleslice = 0
        y_pred_pixels_singleslice = 0
        volume_minimum_singleslice = 0
        volume_sum = 0

        for s in range(x.shape[0]):
            # Volume true per slice
            y_true_array = y_true[s, 0] * 1  # AP
            y_true_pixels_total = np.count_nonzero(y_true_array == 1) + y_true_pixels_total  # AP

        for s in range(x.shape[0]):
            y_true_array = np.round(y_true[s, 0]).astype(int)

            y_true_pixels_singleslice = np.count_nonzero(y_true_array == 1) + y_true_pixels_singleslice  # AP

            # Reading volume total from ClinicalVolumes manual segmentation
            filepath_vol = os.path.join(args.images, p,
                                        'vol.txt')  # "images" is the argument corresponding to ./kaggle_3m  #AP
            read_volume = open(filepath_vol, 'r')  # AP
            lines = read_volume.readlines()  # AP
            volume_true_value_fromline = lines[12]  # AP
            volume_true_value_ClinicalVolumes = float(volume_true_value_fromline)  # AP
            volume_true_value_before_corection = resolution_x * resolution_y * FOV_z * y_true_pixels_total  # AP  volume calc

            # Calculating the true conversion factor
            true_conversion_factor = volume_true_value_before_corection / volume_true_value_ClinicalVolumes  # AP mask volume is incorrectly calculated from the sofware, it needs an adjustment

            # Volume true per slice
            volume_true_value_singleslice = resolution_x * resolution_y * FOV_z * y_true_pixels_singleslice / true_conversion_factor  # /conversion_factor #* 1.5

            # Volume predicted per slice
            y_pred_array = np.round(y_pred[s, 0]).astype(int) # AP
            y_pred_pixels_singleslice = np.count_nonzero(y_pred_array == 1) + y_pred_pixels_singleslice  # AP
            volume_predicted_value_singleslice = resolution_x * resolution_y * FOV_z * y_pred_pixels_singleslice / conversion_factor  # AP  predicted volume per slice

            volume_minimum_singleslice = min(volume_true_value_singleslice , volume_predicted_value_singleslice) +volume_minimum_singleslice
            volume_sum = volume_true_value_singleslice + volume_predicted_value_singleslice + volume_sum

            y_true_pixels_singleslice = 0
            y_pred_pixels_singleslice = 0

        dsc_dict[p] = (volume_minimum_singleslice*2) / volume_sum
        #dsc_dict[p] = dsc(y_pred, y_true, lcc=False)              # Note! The definition dsc from utils is not used anymore!!!!  AP
    return dsc_dict


def plot_dsc(dsc_dist):
    y_positions = np.arange(len(dsc_dist))
    dsc_dist = sorted(dsc_dist.items(), key=lambda x: x[1])
    values = [x[1] for x in dsc_dist]
    labels = [x[0] for x in dsc_dist]
    labels = ["_".join(l.split("_")[1:-1]) for l in labels]
    fig = plt.figure(figsize=(12, 8))
    canvas = FigureCanvasAgg(fig)
    plt.barh(y_positions, values, align="center", color="skyblue")
    plt.yticks(y_positions, labels)
    plt.xticks(np.arange(0.0, 1.0, 0.1))
    plt.xlim([0.0, 1.0])
    plt.gca().axvline(np.mean(values), color="tomato", linewidth=2)
    print('\n Mean DSC value = %.2f \n' % np.mean(values))
    plt.gca().axvline(np.median(values), color="forestgreen", linewidth=2)
    print('Median DSC value = %.2f \n' % np.median(values))
    plt.xlabel("Dice coefficient", fontsize="x-large")
    plt.gca().xaxis.grid(color="silver", alpha=0.5, linestyle="--", linewidth=1)
    plt.tight_layout()
    canvas.draw()
    plt.close()
    s, (width, height) = canvas.print_to_buffer()
    return np.fromstring(s, np.uint8).reshape((height, width, 4))


def makedirs(args):
    os.makedirs(args.predictions, exist_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Inference for segmentation of brain MRI"
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cuda:0",
        help="device for training (default: cuda:0)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="input batch size for training (default: 32)",
    )
    parser.add_argument(
        "--weights", type=str, required=True, help="path to weights file"
    )
    parser.add_argument(
        "--images", type=str, default="./kaggle_3m", help="root folder with images"
    )
    parser.add_argument(
        "--image-size",
        type=int,
        default=256,
        help="target input image size (default: 256)",
    )
    parser.add_argument(
        "--predictions",
        type=str,
        default="./predictions",
        help="folder for saving images with prediction outlines",
    )
    parser.add_argument(
        "--figure",
        type=str,
        default="./dsc.png",
        help="filename for DSC distribution figure",
    )

    args = parser.parse_args()
    main(args)
