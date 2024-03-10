import os
import time
import pandas

def count_files(directory):
    total_files = 0
    for root, dirs, files in os.walk(directory):
        total_files += len(files)
    return total_files

if __name__ == "__main__":
    directory_path = "data/maildir"

    start_time = time.time()
    num_files = count_files(directory_path)
    end_time = time.time()

    print("Total number of files:", num_files)
    print("Time taken:", end_time - start_time, "seconds")
