# links
# # https://stackoverflow.com/questions/31877353/overlay-an-image-segmentation-with-numpy-and-matplotlib
import argparse
from pathlib import Path
from medpy.io import load
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider, Button
from matplotlib.colors import ListedColormap

def get_program_parameters():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('data_folder', help='The path to segmentation and volume mhd/raw files')
    parser.add_argument('volume_filename', help='e.g. volume_14.mhd')
    parser.add_argument('true_segmentation_filename', help='e.g segmentation_14.mhd')
    parser.add_argument('computed_segmentation_filename', help='e.g segmentation_14.mhd')
    args = parser.parse_args()
    return args


args = get_program_parameters()

# Load mhd files
path = Path(args.data_folder)

volume_path = str(path.joinpath(args.volume_filename))
volume_img, _ = load(volume_path)

truth_source_path = str(path.joinpath(args.true_segmentation_filename))
truth_source_img, _ = load(truth_source_path)

computed_path = str(path.joinpath(args.computed_segmentation_filename))
computed_img, _ = load(computed_path)

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
truth_source.imshow(truth_source_img[0], cmap='Blues')
computed.imshow(computed_img[0], cmap='Reds')
# volume_ax = volume.imshow(volume_img[0], cmap='Greys')
# truth_source_ax = truth_source.imshow(truth_source_img[0], cmap='Greys')
# computed_ax = computed.imshow(computed_img[0], cmap='Greys')

# Masks
intersection = np.logical_and(truth_source_img > 0, computed_img > 0)

# a 0 b 0 -> 0
# a 0 b 1 -> 0
# a 1 b 0 -> 1
# a 1 b 1 -> 0
truth_minus_computed = np.logical_and(truth_source_img, np.logical_not(intersection))
computed_minus_truth = np.logical_and(computed_img, np.logical_not(intersection))


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
    truth_source.imshow(truth_source_img[rounded], cmap='Blues')
    computed.imshow(computed_img[rounded], cmap='Reds')

    diff.imshow(volume_img[rounded], cmap='Greys')
    diff.imshow(intersection[rounded], cmap='Purples', alpha=0.2)
    diff.imshow(truth_minus_computed[rounded], cmap='Blues', alpha=0.2)
    diff.imshow(computed_minus_truth[rounded], cmap='Reds', alpha=0.2)


# Register the update function with the slider
frame_slider.on_changed(update)

# Create a `matplotlib.widgets.Button` to reset the slider to initial value
resetax = plt.axes([0.8, 0.025, 0.1, 0.04])
button = Button(resetax, 'Reset', hovercolor='0.975')


def reset(event):
    frame_slider.reset()


button.on_clicked(reset)

plt.show()
