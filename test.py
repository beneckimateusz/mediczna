import SimpleITK as sitk
import matplotlib.pylab as plt

# https://stackoverflow.com/questions/37290631/reading-mhd-raw-format-in-python
# (512, 512, 439)
ct_scans = sitk.GetArrayFromImage(sitk.ReadImage("data/segmentation_14.mhd", sitk.sitkFloat32))
# subset
ct_scans = ct_scans[:513][:513][150:180]

plt.figure(figsize=(20, 16))
plt.gray()
plt.subplots_adjust(0, 0, 1, 1, 0.01, 0.01)

for i in range(ct_scans.shape[0]):
    plt.subplot(5, 6, i + 1), plt.imshow(ct_scans[i]), plt.axis('off')
plt.show()