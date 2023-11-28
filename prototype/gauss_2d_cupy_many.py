"""
Will need approximately 240 GB RAM on the GPU + CPU !!
"""

import numpy as np
import cupy as cp
from cupyx.scipy.ndimage import gaussian_filter
from multiprocessing import Pool

def gaussian_smoothing_2d(input_data, sigma):
    smoothed_data = gaussian_filter(input_data, sigma)
    return smoothed_data

# Function to process a single image
def process_image(image):
    # Set the sigma value for Gaussian smoothing
    sigma = 1.0
    
    # Transfer data to the GPU
    input_data_gpu = cp.asarray(image)
    
    # Perform Gaussian smoothing on the GPU
    smoothed_data_gpu = gaussian_smoothing_2d(input_data_gpu, sigma)
    
    # Transfer data back to the CPU
    smoothed_data_cpu = cp.asnumpy(smoothed_data_gpu)
    
    return smoothed_data_cpu

# Example usage
# Generate 10,000 random 2D images
num_images = 10000
image_shape = (1000, 1000)
input_data = [np.random.random(image_shape) for _ in range(num_images)]

# Create a pool of worker processes
pool = Pool(128)

# Perform parallel processing on the CPU using the pool
smoothed_data_cpu = pool.map(process_image, input_data)

# Close the pool of worker processes
pool.close()
pool.join()

# Print the first smoothed image
print(smoothed_data_cpu[0])

