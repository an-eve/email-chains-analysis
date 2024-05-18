import numpy as np
from dtw_numba import dtw_distance, _cosine
import time
from tqdm import tqdm

def dtw_distance_mine(series1, series2):
    n = len(series1)
    m = len(series2)
    
    # Initialize the cost matrix with infinity
    dtw_matrix = np.full((n+1, m+1), np.inf)
    
    # The cost of aligning the first element with the first element is zero
    dtw_matrix[0, 0] = 0
    
    # Populate the cost matrix
    for i in range(1, n+1):
        for j in range(1, m+1):
            cost = _cosine(series1[i-1], series2[j-1])
            # Find the minimum cost path to (i, j)
            last_min = min(dtw_matrix[i-1, j],    # insertion
                           dtw_matrix[i, j-1],    # deletion
                           dtw_matrix[i-1, j-1])  # match
            dtw_matrix[i, j] = cost + last_min
    
    # The DTW distance is the value at the bottom-right corner of the matrix
    return dtw_matrix[n, m]

time_series_set = [np.random.rand(np.random.randint(5, 15), 768) for _ in range(30000)]

start_time = time.time()
res_numba = dtw_distance(time_series_set[:100], time_series_set)
end_time = time.time()
time_taken = end_time - start_time
print(f"Time taken: {time_taken:.2f} seconds")

"""
# Initialize the distance matrix
num_series = len(time_series_set)
distance_matrix = np.zeros((num_series, num_series))

# Measure the time taken to calculate the DTW distances
start_time = time.time()

# Calculate DTW distance between each pair of time series with progress bar
for i in tqdm(range(num_series), desc="Calculating DTW distances"):
    for j in range(i+1, num_series):
        distance = dtw_distance_mine(time_series_set[i], time_series_set[j])
        distance_matrix[i, j] = distance
        distance_matrix[j, i] = distance  # Symmetric matrix

end_time = time.time()
time_taken = end_time - start_time

print("Distance Matrix:")
print(distance_matrix)
print(f"Time taken: {time_taken:.2f} seconds")

dtw_distance(time_series_set, time_series_set)

all_elements_close = np.all(np.isclose(res_numba, distance_matrix))
print(all_elements_close)  

is_symmetric = np.array_equal(res_numba, res_numba.T)

if is_symmetric:
    print("The matrix is symmetric.")
else:
    print("The matrix is not symmetric.")
"""