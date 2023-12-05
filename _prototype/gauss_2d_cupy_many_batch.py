import numpy as np
import cupy as cp
from cupyx.scipy.ndimage import gaussian_filter
from multiprocessing import Pool

def gaussian_smoothing_2d(input_data, sigma):
    smoothed_data = gaussian_filter(input_data, sigma)
    return smoothed_data

# Function to process a batch of images
def process_batch(batch):
    # Set the sigma value for Gaussian smoothing
    sigma = 1.0

    # Transfer data to the GPU
    batch_gpu = cp.asarray(batch)

    # Perform Gaussian smoothing on the GPU
    smoothed_batch_gpu = gaussian_smoothing_2d(batch_gpu, sigma)

    # Transfer data back to the CPU
    smoothed_batch_cpu = cp.asnumpy(smoothed_batch_gpu)

    del batch_gpu
    del smoothed_batch_gpu
    cp._default_memory_pool.free_all_blocks()

    return smoothed_batch_cpu

# Example usage
# Generate 10,000 random 2D images
num_images = 1000
image_shape = (1000, 1000)
input_data = [np.random.random(image_shape) for _ in range(num_images)]
print("A: Generated input data.")

# Determine batch size based on available GPU memory
GPU_RAM = 8  # GB
max_batch_size = int(GPU_RAM * 1024 * 1024 * 1024 / (image_shape[0] * image_shape[1] * 8))
batch_size = 10 #min(max_batch_size, num_images)
print("B: Specified (max) batch sizes:", max_batch_size, batch_size)

# Create a pool of worker processes
pool = Pool()

# Process the images in batches
smoothed_data_cpu = []
for i in range(0, num_images, batch_size):
    print(i)
    batch = input_data[i:i+batch_size]
    smoothed_batch_cpu = pool.map(process_batch, [batch])[0]
    smoothed_data_cpu.extend(smoothed_batch_cpu)

print("C: Done!")

# Close the pool of worker processes
pool.close()
pool.join()

# Print the first smoothed image
print(smoothed_data_cpu[0])

