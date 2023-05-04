"""
An example of processing geospatial data from SpaceNet with the GDAL library.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
import matplotlib.pyplot as plt
from osgeo import gdal
from tqdm import tqdm
import numpy as np
import json
import os


@dataclass(kw_only=True)
class GeoTIFF(ABC):
    """Base class for GeoTIFF files."""
    path: str

    def __post_init__(self):

        # Load data
        self.gdata: gdal.Dataset = gdal.Open(self.path)

        # Extract some basic metadata about the bands
        self.n_bands = self.gdata.RasterCount
        self.x_res = self.gdata.RasterXSize
        self.y_res = self.gdata.RasterYSize

        # Process transform data
        self._proc_geotransform()

        # Process bands
        self._read_bands()

    def _proc_geotransform(self):

        # See https://gdal.org/tutorials/geotransforms_tut.html
        self.extent = np.zeros(4)
        gt = self.gdata.GetGeoTransform()

        # Left, right, bottom, top
        self.extent[0] = gt[0]
        self.extent[1] = gt[0] + self.x_res * gt[1] + self.y_res * gt[2]
        self.extent[2] = gt[3] + self.x_res * gt[4] + self.y_res * gt[5]
        self.extent[3] = gt[3]

    def _read_bands(self):
        """Read in the band data."""
        self.bands = np.zeros((self.n_bands, self.x_res, self.y_res))
        for i in range(self.n_bands):
            band: gdal.Band = self.gdata.GetRasterBand(i+1)
            self.bands[i] = band.ReadAsArray()

    @abstractmethod
    def plot_bands(self, ax: plt.Axes):
        """Plot RGB bands."""
        pass


@dataclass(kw_only=True)
class PAN(GeoTIFF):
    """GeoTIFF files containing PAN data."""
    def __post_init__(self):
        super().__post_init__()

    def plot_bands(self, ax: plt.Axes):
        """Plot PAN data."""
        ax.imshow(self.bands[0], extent=self.extent)


@dataclass(kw_only=True)
class PSRGB(GeoTIFF):
    """GeoTIFF files containing PSRGB data."""
    def __post_init__(self):
        super().__post_init__()
        self._proc_rgb()

    def _proc_rgb(self):
        """Reshape and normalize RGB data."""
        self.rgb = np.zeros((self.x_res, self.y_res, self.n_bands))

        # Transform array
        for i in range(self.n_bands):
            self.rgb[:, :, i] = self.bands[i]

        # Scale array
        rgb_min = np.min(self.rgb, axis=(0, 1))
        rgb_max = np.max(self.rgb, axis=(0, 1))
        self.rgb = (self.rgb - rgb_min) / (rgb_max - rgb_min)

    def plot_bands(self, ax: plt.Axes):
        # TODO implement.
        pass


@dataclass(kw_only=True)
class GeoJSON:
    """A helper dataclass for processing .geojson files."""
    path: str

    def __post_init__(self):

        # Load json
        with open(self.path, 'r') as f:
            self.json = json.load(f)

    def plot_roads(self, ax: plt.Axes) -> None:
        """Plot JSON roads on axes."""

        # Plot each road
        for road in self.json['features']:
            try:
                x, y = np.array(road['geometry']['coordinates']).T
                ax.plot(x, y, color='white', lw=0.5, solid_capstyle='round')
            except ValueError:
                pass  # TODO catch and plot multi-path roads.


def plot_spacenet():
    """Plot all .tiff and .geojson files in one figure."""

    # Make figure objects
    figure: plt.Figure = plt.figure(
        figsize=(8, 6),
        dpi=300,
    )
    ax: plt.Axes = figure.add_subplot()

    # Define the plotting bounds
    x_min = np.inf
    x_max = -np.inf
    y_min = np.inf
    y_max = -np.inf

    # Source folders
    folder_tif_a = 'AOI_3_Paris/PAN'
    folder_tif_b = 'AOI_3_Paris_Train/PAN'
    folder_json = 'AOI_3_Paris/geojson_roads'

    # Generate paths
    tif_paths = []
    json_paths = []

    for file in os.listdir(folder_tif_a):
        tif_paths.append(f'{folder_tif_a}/{file}')
    for file in os.listdir(folder_tif_b):
        tif_paths.append(f'{folder_tif_b}/{file}')

    for file in os.listdir(folder_json):
        json_paths.append(f'{folder_json}/{file}')

    # Plot bands
    for path in tqdm(tif_paths):

        # Read data
        tif = PAN(path=path)

        # Plot bands
        tif.plot_bands(ax=ax)

        # Update bounds
        x_min = min(x_min, tif.extent[0])
        x_max = max(x_max, tif.extent[1])
        y_min = min(y_min, tif.extent[2])
        y_max = max(y_max, tif.extent[3])

        # Cleanup
        del tif

    # Plot roads
    for path in tqdm(json_paths):

        # Read data
        gj = GeoJSON(path=path)

        # Plot roads
        gj.plot_roads(ax=ax)

    # Format and save
    ax.set_title('SpaceNet PAN band for Paris, France (with road overlay)')
    ax.set_facecolor('black')
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    figure.savefig('patches_low-res.png')


if __name__ == '__main__':
    # experiment()
    plot_spacenet()
