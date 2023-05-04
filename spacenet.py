from abc import ABC, abstractmethod
from dataclasses import dataclass
import matplotlib.pyplot as plt
from typing import Optional
from osgeo import gdal
from tqdm import tqdm
import numpy as np
import json
import os


@dataclass(kw_only=True)
class GeoTIFF(ABC):
    """Base class for GeoTIFF files."""
    tif_path: str
    json_path: Optional[str] = None

    def __post_init__(self):

        # Load data
        self.gdata: osgeo.gdal.Dataset = gdal.Open(self.tif_path)

        # Extract some basic metadata about the bands
        self.n_bands = self.gdata.RasterCount
        self.x_res = self.gdata.RasterXSize
        self.y_res = self.gdata.RasterYSize

        # Process transform data
        self._proc_geotransform()

        # Process bands
        self._read_bands()

        # Read in JSON data
        self._load_json()

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

    def _load_json(self):

        if self.json_path is not None:
            self.gj = GeoJSON(path=self.json_path)

    @abstractmethod
    def plot_bands(self, ax: plt.Axes):
        pass

    def plot_roads(
            self,
            ax: plt.Axes,
    ) -> None:
        """Plot JSON roads on axes."""

        # Plot each road
        for road in self.gj.json['features']:
            x, y = np.array(road['geometry']['coordinates']).T
            ax.plot(
                x,
                y,
                color='white',
                lw=2,
            )


@dataclass(kw_only=True)
class PAN(GeoTIFF):
    """GeoTIFF files containing PAN data."""
    def __post_init__(self):
        super().__post_init__()

    def plot_bands(
            self,
            ax: plt.Axes,
    ):
        """Plot PAN data."""
        ax.imshow(
            self.bands[0],
            extent=self.extent,
        )


@dataclass(kw_only=True)
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

        # Transform array
        for i in range(self.n_bands):
            self.rgb[:, :, i] = self.bands[i]

        # Scale array
        rgb_min = np.min(self.rgb, axis=(0, 1))
        rgb_max = np.max(self.rgb, axis=(0, 1))
        self.rgb = (self.rgb - rgb_min) / (rgb_max - rgb_min)


@dataclass(kw_only=True)
class GeoJSON:
    path: str

    def __post_init__(self):

        # Load json
        with open(self.path, 'r') as f:
            self.json = json.load(f)




def experiment():
    pan_path = 'AOI_3_Paris/PAN/SN3_roads_train_AOI_3_Paris_PAN_img100.tif'
    psrgb_path = 'AOI_3_Paris/PS-RGB/SN3_roads_train_AOI_3_Paris_PS-RGB_img100.tif'
    json_path = 'AOI_3_Paris/geojson_roads/SN3_roads_train_AOI_3_Paris_geojson_roads_img100.geojson'

    geo = PAN(
        tif_path=pan_path,
        json_path=json_path,
    )

    # geo = PSRGB(
    #     tif_path=psrgb_path,
    #     json_path=json_path,
    # )

    # Make figure objects
    figure: plt.Figure = plt.figure()
    ax: plt.Axes = figure.add_subplot()

    # Plot bands
    geo.plot_bands(ax=ax)

    # Plot roads
    geo.plot_roads(ax=ax)

    # Format
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    figure.set_dpi(300)
    figure.savefig('roads.png')



def plot_spacenet():

    # Make figure objects
    figure: plt.Figure = plt.figure(
        figsize=(10, 8)
    )
    ax: plt.Axes = figure.add_subplot()

    # Define the plotting bounds
    x_min = np.inf
    x_max = -np.inf
    y_min = np.inf
    y_max = -np.inf

    # Iterate through patches
    folder = 'AOI_3_Paris/PS-RGB'
    files = sorted(os.listdir(folder))

    for file in tqdm(files[:50]):
        if file.endswith('.tif'):

            # Read data
            tif = PSRGB(
                tif_path=f'{folder}/{file}',
            )

            # Add to figure
            ax.imshow(
                tif.rgb,
                extent=tif.extent,
            )

            # Update bounds
            x_min = min(x_min, tif.extent[0])
            x_max = max(x_max, tif.extent[1])
            y_min = min(y_min, tif.extent[2])
            y_max = max(y_max, tif.extent[3])

    # Format and save
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    figure.set_dpi(1000)
    figure.savefig('patches.png')


if __name__ == '__main__':
    experiment()