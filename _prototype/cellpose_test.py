from cellpose import models
from cellpose.io import imread
import skimage.io
import numpy as np
import matplotlib.pyplot as plt

model = models.Cellpose(gpu=True, model_type='cyto2')

file = 'data/Plate4_B - 05(fld 5 wv Blue and Red Channels).tif'

img  = imread(file)  # read with cellpose
img0 = skimage.io.imread(file, plugin='tifffile')  # read with skimage

print(np.sum(img[0])-np.sum(img0[0]))
print(np.sum(img[1])-np.sum(img0[1]))


channels = [1,2]
masks, flows, styles, diams = model.eval(img0, diameter=None, channels=channels, resample=True,
                                         flow_threshold=0.4, cellprob_threshold=0.0, do_3D=False)


from cellpose import plot

maski = masks
flowi = flows[0]

fig = plt.figure(figsize=(12,5))
plot.show_segmentation(fig, img, maski, flowi, channels=channels)
plt.tight_layout()
plt.show()


# Default settings. For more info see:
# https://cellpose.readthedocs.io/en/latest/settings.html
#
# Explanation of 'channel' parameter:
# https://forum.image.sc/t/about-the-correct-meaning-of-channel-in-cellpose-2-2/79671/7
