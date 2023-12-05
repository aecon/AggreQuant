from multiprocessing import Pool
from image_segmentation import ImageSegmentation
from statistics_generation import StatisticsGeneration

def process_image(image):
    # Perform image segmentation using the ImageSegmentation module/class
    segmentation = ImageSegmentation()
    segmented_image = segmentation.segment_nuclei(image)

    # Generate statistics for the segmented image using the StatisticsGeneration module/class
    statistics = StatisticsGeneration()
    image_stats = statistics.generate_statistics(segmented_image)

    return image_stats

def main():
    # Read the list of 10,000 images

    # Create a pool of worker processes
    pool = Pool(processes=128)  # Number of CPU cores

    # Process images in parallel using the worker processes
    results = pool.map(process_image, images)  # images is the list of 10,000 images
    # images can be a list with the 3 nuclei, cell, agg image set. Then each seg algo uses the correct image from the list.

    # Close the pool of worker processes
    pool.close()
    pool.join()

    # Process the results as needed

if __name__ == '__main__':
    main()

