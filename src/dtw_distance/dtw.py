import numpy as np
import pandas as pd
import time
from tqdm import tqdm
import csv

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

# Generate a set of 100 random time series with elements as vectors of length 768
np.random.seed(0)  # For reproducibility
time_series_set = [np.random.rand(np.random.randint(5, 15), 768) for _ in range(1800)]

with open('time_series.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Index', 'Time Series'])
    for idx, series in enumerate(time_series_set):
        writer.writerow([idx, series.tolist()])

df = pd.read_csv('time_series.csv')

# Display the first few rows of the DataFrame
print(df.head())
df['Time Series'] = df['Time Series'].apply(lambda x: eval(x)).tolist()


# Initialize the distance matrix
num_series = len(time_series_set)
distance_matrix = np.zeros((num_series, num_series))

# Measure the time taken to calculate the DTW distances
start_time = time.time()

# Calculate DTW distance between each pair of time series with progress bar
for i in tqdm(range(num_series), desc="Calculating DTW distances"):
    for j in range(i+1, num_series):
        distance = dtw_distance(time_series_set[i], time_series_set[j])
        distance_matrix[i, j] = distance
        distance_matrix[j, i] = distance  # Symmetric matrix

end_time = time.time()
time_taken = end_time - start_time

print("Distance Matrix:")
print(distance_matrix)
print(f"Time taken: {time_taken:.2f} seconds")
