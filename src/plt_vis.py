# links
# # https://stackoverflow.com/questions/31877353/overlay-an-image-segmentation-with-numpy-and-matplotlib
import argparse
from pathlib import Path
from medpy.io import load
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider, Button
from matplotlib.colors import ListedColormap
from medpy.metric.binary import hd, assd, asd, dc, jc
from medpy.io import header

truth_colors = [(128, 0, 0), (230, 25, 75), (250, 190, 212)]
computed_colors = [(0, 0, 128), (0, 128, 128), (0, 130, 200)]

def get_program_parameters():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('data_folder', help='The path to segmentation and volume mhd/raw files')
    parser.add_argument('volume_filename', help='e.g. volume_14.mhd')
    parser.add_argument('true_segmentation_filename', help='e.g segmentation_14.mhd')
    parser.add_argument('computed_segmentation_filename', help='e.g segmentation_14.mhd')
    args = parser.parse_args()
    return args

def get_segmentations_differences(truth_source_img, computed_img):
    unique_values = np.unique(truth_source_img)
    #skipping non-segmentated stuff
    unique_values = unique_values[unique_values != 0]
    print(f"unique values: {unique_values}")
    truth_minus_computed = []
    computed_minus_truth = []
    for value in unique_values:
        truth_image_with_value = np.logical_and(truth_source_img == value, True)
        computed_image_with_value = np.logical_and(computed_img == value, True)
        intersection = np.logical_and(truth_image_with_value, computed_image_with_value)
        truth_minus_computed.append(np.logical_and(truth_image_with_value, np.logical_not(intersection)))
        computed_minus_truth.append(np.logical_and(computed_image_with_value, np.logical_not(intersection)))

    return truth_minus_computed, computed_minus_truth

def get_segmentations(truth_source_img, computed_img):
    unique_values = np.unique(truth_source_img)
    #skipping non-segmentated stuff
    unique_values = unique_values[unique_values != 0]
    print(f"unique values: {unique_values}")
    truth_minus_computed = []
    computed_minus_truth = []
    for value in unique_values:
        truth_minus_computed.append(np.logical_and(truth_source_img == value, True))
        computed_minus_truth.append(np.logical_and(computed_img == value, True))


    return truth_minus_computed, computed_minus_truth

def map_diffs_to_colors(image, masks, kind, with_alfa=True):
    channel_size, default = (4, (0, 0, 0, 0)) if with_alfa else (3, (255, 255, 255))

    image_copy = np.copy(image)
    image_copy = np.stack((image_copy,)*channel_size, axis=-1)
    image_copy[:,:,:] = default
    colors = computed_colors if kind == 'computed' else truth_colors
    for mask, color in zip(masks, colors):
        image_copy[mask] = np.array([*color, 255] if with_alfa else color)
    return image_copy
   
args = get_program_parameters()

# Load mhd files
path = Path(args.data_folder)

volume_path = str(path.joinpath(args.volume_filename))
volume_img, volume_header = load(volume_path)

truth_source_path = str(path.joinpath(args.true_segmentation_filename))
truth_source_img, truth_source_header = load(truth_source_path)

computed_path = str(path.joinpath(args.computed_segmentation_filename))
computed_img, _ = load(computed_path)
# calculate metrics
spacing = truth_source_header.get_voxel_spacing()


truth, computed = get_segmentations(truth_source_img, computed_img)
truth_minus_computed, computed_minus_truth = get_segmentations_differences(truth_source_img, computed_img)

truth_minus_computed_to_colors = map_diffs_to_colors(truth_source_img, truth_minus_computed, 'truth')
computed_minus_truth_to_colors = map_diffs_to_colors(computed_img, computed_minus_truth, 'computed')
truth_to_colors = map_diffs_to_colors(truth_source_img, truth, 'truth', with_alfa=False)
computed_to_colors = map_diffs_to_colors(computed_img, computed, 'computed', with_alfa=False)

'''
print(f"Hausdorff distance: {hd(computed_img, truth_source_img, spacing)}")
print(f"Average surface distance: {asd(computed_img, truth_source_img, spacing)}")
print(f"Average symmetric surface distance: {assd(computed_img, truth_source_img, spacing)}")
print(f"Dice coeff: {dc(computed_img, truth_source_img)}")
print(f"Jaccard index: {jc(computed_img, truth_source_img)}")
'''
# Prepare the plot
fig, axs = plt.subplots(1, 3)
truth_source = axs[0]
diff = axs[1]
computed = axs[2]

for ax in axs:
    ax.set_xticks([])
    ax.set_yticks([])

truth_source.set_title('Truth source')
computed.set_title('Computed')
diff.set_title('Diff')

diff.imshow(volume_img[0], cmap='Greys')
truth_source.imshow(truth_to_colors[0])
computed.imshow(computed_minus_truth_to_colors[0])
# volume_ax = volume.imshow(volume_img[0], cmap='Greys')
# truth_source_ax = truth_source.imshow(truth_source_img[0], cmap='Greys')
# computed_ax = computed.imshow(computed_img[0], cmap='Greys')



# Masks
#intersection = np.logical_and(truth_source_img > 0, computed_img > 0)

# a 0 b 0 -> 0
# a 0 b 1 -> 0
# a 1 b 0 -> 1
# a 1 b 1 -> 0
#truth_minus_computed = np.logical_and(truth_source_img, np.logical_not(intersection))
#computed_minus_truth = np.logical_and(computed_img, np.logical_not(intersection))


# Adjust the main plot to make room for the sliders
fig.subplots_adjust(bottom=0.25, hspace=0.5)

# Make a horizontal slider to control the displayed frame
axfreq = plt.axes([0.25, 0.1, 0.65, 0.03])
frame_slider = Slider(
    ax=axfreq,
    label='Frame',
    valmin=0,
    valmax=volume_img.shape[0] - 1,
    valinit=0,
    valfmt="%i"
)


# The function to be called anytime a slider's value changes
def update(val):
    rounded = round(val)

    # approach 1 - faster, does not work for truth_source and computed_ax
    # if the 0th frame is empty
    # truth_source_ax.set(data=truth_source_img[rounded], cmap='Greys')
    # volume_ax.set(data=volume_img[rounded], cmap='Greys')
    # computed_ax.set(data=computed_img[rounded], cmap='Greys')
    # fig.canvas.draw()

    # approach 2 - much slower, works every time
    truth_source.imshow(truth_to_colors[rounded])
    computed.imshow(computed_to_colors[rounded])

    diff.imshow(volume_img[rounded], cmap='Greys')
    diff.imshow(truth_minus_computed_to_colors[rounded])
    diff.imshow(computed_minus_truth_to_colors[rounded])


# Register the update function with the slider
frame_slider.on_changed(update)

# Create a `matplotlib.widgets.Button` to reset the slider to initial value
resetax = plt.axes([0.8, 0.025, 0.1, 0.04])
button = Button(resetax, 'Reset', hovercolor='0.975')


def reset(event):
    frame_slider.reset()


button.on_clicked(reset)

plt.show()
