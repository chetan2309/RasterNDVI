import io
import logging
import azure.functions as func
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import rasterio


def main(myblob: func.InputStream, outputBlob: func.Out[bytes]) -> None:
    logging.info(f"Blob trigger function processed blob \n"
                 f"Name:{myblob.name}\n"
                 f"Blob Size: {myblob.length}")

    # Check if the file is a TIFF file
    if myblob.name.lower().endswith('.tif') or myblob.name.lower().endswith('.tiff') or myblob.name.lower().endswith('.png'):
        # Directly use the single band data and save as PNG with custom color map
        band_data = myblob.read()
        png_data = save_band_as_png(band_data)

        # Save the PNG data to the output blob without specifying the name
        outputBlob.set(png_data)

    else:
        logging.warning("The input file is not a TIFF file. Skipping processing.")


def save_band_as_png(band_data: bytes) -> bytes:
    with rasterio.io.MemoryFile(band_data) as memfile:
        with memfile.open() as dataset:
            # Get raster dimensions
            width = dataset.width
            height = dataset.height

            # Convert band_data to a NumPy array with the specified shape and data type (e.g., float64)
            band_array = dataset.read(1)

            # Check if band_array is not empty
            if not np.any(band_array):
                logging.warning("The band data is empty. Skipping processing.")
                return b''

            # Create a custom colormap for different NDVI ranges
            cmap = create_custom_colormap()

            # Apply the colormap to the single-band data
            rgba_image = cmap(band_array)

            # Save the colorized image as PNG in memory
            with io.BytesIO() as output_buffer:
                plt.imsave(output_buffer, rgba_image, format='png')
                png_data = output_buffer.getvalue()

    return png_data

def create_custom_colormap():
    # Define NDVI value ranges and corresponding colors
    ndvi_ranges = np.linspace(-1, 1, 8)  # Divide the range into 7 values between -1 to 1
    colors = ['#1B8819', '#2ADE08', '#9BFF0C', '#FCE51C', '#F8850C', '#F80711', '#930A0C']

    # Create a ListedColormap using the specified colors and ranges
    cmap = ListedColormap(colors, name='custom_colormap', N=len(ndvi_ranges) - 1)
    return cmap