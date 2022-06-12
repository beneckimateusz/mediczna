from pathlib import Path
from medpy.io import load
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

def get_program_parameters():
    import argparse
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('data_folder', help='The path to segmentation and volume mhd/raw files')
    parser.add_argument('volume_filename', help='e.g. volume_14')
    parser.add_argument('true_segmentation_filename', help='e.g segmentation_14')
    parser.add_argument('computed_segmentation_filename', help='e.g segmentation_14')
    args = parser.parse_args()
    return args


args = get_program_parameters()
path = Path(args.data_folder)
volume_img, _ = load(str(path.joinpath(args.volume_filename)))
truth_source_img, _ = load(str(path.joinpath(args.true_segmentation_filename)))
computed_img, _ =load(str(path.joinpath(args.computed_segmentation_filename)))
# diff_img = axs[1, 1]
# Create the figure and the line that we will manipulate
fig, axs = plt.subplots(2, 2)

volume = axs[0, 0]
truth_source = axs[0, 1]
computed = axs[1, 0]
diff = axs[1, 1]

print(volume_img)

volume.set_title('Volume')
truth_source.set_title('Truth source')
computed.set_title('Computed')

volume.imshow(volume_img[0], cmap = cm.Greys_r)
truth_source.imshow(truth_source_img[0], cmap = cm.Greys_r)
computed.imshow(computed_img[0], cmap = cm.Greys_r)


# adjust the main plot to make room for the sliders
fig.subplots_adjust(bottom=0.25, hspace=0.5)

# Make a horizontal slider to control the frequency.
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
    #TODO tak chyba powinno sie rerenderowac ale cus nie dziala :/
    #image.set_data(i[round(val)])
    #fig.canvas.draw()
    rounded = round(val)
    volume.imshow(volume_img[rounded], cmap = cm.Greys_r)
    truth_source.imshow(truth_source_img[rounded], cmap = cm.Greys_r)
    computed.imshow(computed_img[rounded], cmap = cm.Greys_r)




# register the update function with each slider
frame_slider.on_changed(update)

# Create a `matplotlib.widgets.Button` to reset the sliders to initial values.
resetax = plt.axes([0.8, 0.025, 0.1, 0.04])
button = Button(resetax, 'Reset', hovercolor='0.975')


def reset(event):
    frame_slider.reset()

button.on_clicked(reset)

plt.show()