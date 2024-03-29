import os
import time
import pandas
import paths

def count_files(directory):
    """
    Count the total number of files in a given directory including all subdirectories.

    Args:
    - directory (str): The path to the directory to count files in.

    Returns:
    - total_files (int): The total number of files found in the directory and its subdirectories.
    """
    total_files = 0
    for root, dirs, files in os.walk(directory):
        total_files += len(files)
    return total_files


if __name__ == "__main__":
    start_time = time.time()
    num_files = count_files(paths.DATA_FOLDER)
    end_time = time.time()

    print("Total number of files:", num_files)
    print("Time taken:", end_time - start_time, "seconds")
