from dataclasses import dataclass
import matplotlib.pyplot as plt
from osgeo import gdal
from tqdm import tqdm
import numpy as np
import os


@dataclass
class GeoTIFF:
    """Base class for GeoTIFF files."""
    path: str

    def __post_init__(self):
        self.gdata: osgeo.gdal.Dataset = gdal.Open(self.path)
        self._read_bands()

    def _read_bands(self):
        """Read in the band data."""
        self.n_bands = self.gdata.RasterCount
        self.x_res = self.gdata.RasterXSize
        self.y_res = self.gdata.RasterYSize
        self.bands = np.zeros(
            (
                self.n_bands,
                self.x_res,
                self.y_res,
            )
        )
        for i in range(self.n_bands):
            band: gdal.Band = self.gdata.GetRasterBand(i+1)
            self.bands[i] = band.ReadAsArray()

    def plot_band(self, n=0):

        plt.figure()
        plt.imshow(self.bands)
        plt.show()


@dataclass
class PAN(GeoTIFF):
    """GeoTIFF files containing PAN data."""
    def __post_init__(self):
        super().__post_init__()


@dataclass
class PSRGB(GeoTIFF):
    """GeoTIFF files containing PSRGB data."""
    def __post_init__(self):
        super().__post_init__()
        self._proc_rgb()

    def _proc_rgb(self):
        """Reshape and normalize RGB data."""
        self.rgb = np.zeros(
            (
                self.x_res,
                self.y_res,
                self.n_bands,
            )
        )
        for i in range(self.n_bands):
            self.rgb[:, :, i] = self.bands[i]




def run():
    pan_path = 'AOI_3_Paris/PAN/SN3_roads_train_AOI_3_Paris_PAN_img100.tif'
    psrgb_path = 'AOI_3_Paris/PS-RGB/SN3_roads_train_AOI_3_Paris_PS-RGB_img100.tif'
    pan = PSRGB(
        path=psrgb_path
    )

    plt.figure()
    print(pan.rgb.shape)
    plt.imshow(pan.rgb)
    plt.show()

if __name__ == '__main__':
    run()