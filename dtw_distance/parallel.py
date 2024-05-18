import threading
import signal
import sys
import numpy as np
import time
from tqdm import tqdm

def euclidean_distance(v1, v2):
    return np.linalg.norm(v1 - v2)

def dtw_distance(series1, series2):
    n = len(series1)
    m = len(series2)
    
    # Initialize the cost matrix with infinity
    dtw_matrix = np.full((n+1, m+1), np.inf)
    
    # The cost of aligning the first element with the first element is zero
    dtw_matrix[0, 0] = 0
    
    # Populate the cost matrix
    for i in range(1, n+1):
        for j in range(1, m+1):
            cost = euclidean_distance(series1[i-1], series2[j-1])
            # Find the minimum cost path to (i, j)
            last_min = min(dtw_matrix[i-1, j],    # insertion
                           dtw_matrix[i, j-1],    # deletion
                           dtw_matrix[i-1, j-1])  # match
            dtw_matrix[i, j] = cost + last_min
    
    # The DTW distance is the value at the bottom-right corner of the matrix
    return dtw_matrix[n, m]


def signal_handler(sig, frame):
    global exit_event
    
    exit_event = True


def single_thread_calculator(i, series1, series2):
    global threads_left_to_create
    global result_data_file
    global writing_to_file_lock

    # For example we want to calculate factorials up to 10^2
    thread_result = dtw_distance(series1, series2)
    
    writing_to_file_lock.acquire()
    #result_data_file.write(str(i) + ',' + str(thread_result) + '\n')
    writing_to_file_lock.release()
    
    threads_left_to_create.release()



MAX_THREAD_COUNT = 4

exit_event = False
threads_left_to_create = threading.Semaphore(MAX_THREAD_COUNT)
writing_to_file_lock = threading.Lock()

np.random.seed(0)  # For reproducibility
time_series_set = [np.random.rand(np.random.randint(5, 15), 768) for _ in range(1800)]

"""
try:
    data = np.genfromtxt("data.csv", delimiter=',',)
    calculated_key = data[:,0]
    calculated_result = data[:,1]
    mask = numpy.isin(key_to_calculate, calculated_key)
    key_to_calculate = key_to_calculate[~mask]
    result_data_file = open("data.csv", "a")
except:
"""
result_data_file = open("data.csv", "w+")


# Register signal handlers based on platform
if sys.platform.startswith('win'):
    # Windows doesn't support signals other than SIGINT
    signal.signal(signal.SIGINT, signal_handler)
else:
    # Unix-like platforms support multiple signals
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGUSR1, signal_handler)

num_series = len(time_series_set)
distance_matrix = np.zeros((num_series, num_series))

start_time = time.time()

# Calculate DTW distance between each pair of time series with progress bar
for i in tqdm(range(num_series), desc="Calculating DTW distances"):
    for j in range(i+1, num_series):
        threading.Thread(target = single_thread_calculator(i*num_series+j, time_series_set[i], time_series_set[j])).start()
        threads_left_to_create.acquire()
        if exit_event:
            break
        
end_time = time.time()
time_taken = end_time - start_time

result_data_file.close()

print(f"Time taken: {time_taken:.2f} seconds")
