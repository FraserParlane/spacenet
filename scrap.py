from dataclasses import dataclass
import matplotlib.pyplot as plt
from skimage import exposure
from osgeo import gdal
from tqdm import tqdm
import numpy as np
import os


@dataclass
class GeoTIFF:
    path: str

    def __post_init__(self):
        self.gdal_data: osgeo.gdal.Dataset = gdal.Open(self.path)


@dataclass
class PAN(GeoTIFF):

    def __post_init__(self):
        super().__post_init__()


#
# # Create a dataclass type for PAN-RGB
# @dataclass
# class PSRGB(GeoTIFF):
#
#     def __post_init__(self):
#         super().__post_init__()
#
#         # Get RGB values
#         band_arrays = []
#         for i in range(3):
#             band = gdata.GetRasterBand(i+1)
#             band_arrays.append(band.ReadAsArray())
#         rgb = np.dstack(band_arrays[::-1]).astype(np.float32)

# Normalize RGB
# for i in range(3):
# rgb[:, :, i] += rgb[:, :, i].min()
# rgb[:, :, i] *= 1 / rgb[:, :, i].max()

# rgb += -rgb.min()
# rgb *= 1 / rgb.max()
# print(rgb)
# self.rgb = contrast_stretch(rgb, 5, 95)
# print(self.rgb)
#     self.rgb = rgb
#
# def plot(self):
#
#     plt.figure()
#     plt.imshow(self.rgb)
#     plt.show()


def run():
    # Just use greyscale pan? What is MS?

    path = 'AOI_3_Paris/PS-RGB/SN3_roads_train_AOI_3_Paris_PS-RGB_img100.tif'
    pan_rgb = PanRGB(path=path)
    # pan_rgb.plot()
    # val = 1940
    # folder = 'AOI_3_Paris/PS-RGB'
    # for file in tqdm(os.listdir(folder)):
    #     if file.endswith('.tif'):
    #         p = PanRGB(path=f'{folder}/{file}')
    #         val = min(val, p.rgb.min())
    # print(val)


if __name__ == '__main__':
    run()
