import cupy as cp
from cupyx.scipy.ndimage import gaussian_filter

def gaussian_smoothing_2d(input_data, sigma):
    smoothed_data = gaussian_filter(input_data, sigma)
    return smoothed_data

# Example usage
# Create a random 2D array
input_data = cp.random.random((1000, 1000))

# Set the sigma value for Gaussian smoothing
sigma = 1.0

# Transfer data to the GPU
input_data_gpu = cp.asarray(input_data)

# Perform Gaussian smoothing on the GPU
smoothed_data_gpu = gaussian_smoothing_2d(input_data_gpu, sigma)

# Transfer data back to the CPU
smoothed_data_cpu = cp.asnumpy(smoothed_data_gpu)

# Print the smoothed data
print(smoothed_data_cpu)

